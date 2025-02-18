from bson import ObjectId
import json
import asyncio
from typing import List
from aiokafka import AIOKafkaConsumer  # type: ignore
from app.core.config import settings
from app.api.msg_socket.router import send_message
from app.api.sync_socket.router import send_message as send_sync_message
from app.core.schemas import (
    OnlineStatusMessage,
    MessageEvent,
    MessageStatusUpdate,
    MessageNoAlias,
    Message,
)
from app.core.db import AsyncDatabase
from app.api.msg_socket.services import get_user_form_conversation


async def watch_user_updates(db: AsyncDatabase):
    async with db.user_profile.watch(
        pipeline=[{"$match": {"operationType": "update"}}]
    ) as stream:
        async for change in stream:
            try:
                cursor = db.friends.find({"_id": change["documentKey"]["_id"]})

                # Extracting the `friends_id` values from each result document
                friends_ids: List[ObjectId] = [
                    doc["friends_id"] async for doc in cursor
                ]

                # Sending the data to the online frinds
                await send_sync_message(
                    friends_ids, change["updateDescription"]["updatedFields"]
                )

                # updating the lastupdate fo friends data
                await db.friends.update_many(
                    {"friends_id": change["documentKey"]["_id"]},
                    {"$set": {"update_at": change["wallTime"]}},
                )

            except Exception as e:
                print(f"Error processing user update : {e}")


async def handle_online_status_update(db: AsyncDatabase):
    while True:
        consumer = AIOKafkaConsumer(
            "online_status", bootstrap_servers=settings.KAFKA_CONNECTION
        )

        try:
            await consumer.start()

            # Asyncronous Loop for iterating over the available messages
            async for msg in consumer:
                # Decoding the received data
                data = json.loads(msg.value.decode("utf-8"))
                user_id = data["user_id"]
                user_list: List[ObjectId] = []

                try:
                    # Retrive the conversations with the user
                    async for document in db.conversation.find(
                        {"participants": {"$all": [ObjectId(user_id)]}}
                    ):
                        # Add the firend id to the list
                        user_list.extend(
                            ObjectId(userid)
                            for userid in document["participants"]
                            if str(userid) != user_id
                        )

                    # Prepare the date and sending it to the list of user
                    msg_data = OnlineStatusMessage(
                        user_id=user_id, status=data["status"]
                    )
                    await send_sync_message(user_ids=user_list, message_data=msg_data)

                except Exception as e:
                    print("Error retrieving user:", e)
        except json.JSONDecodeError as e:
            print("Error decoding the kafka message : ", e)
        except Exception as e:
            print("Error in kafka consumer : ", e)

        finally:
            await consumer.stop()
            print("Reconnecting in 5 sec")
            await asyncio.sleep(5)


async def watch_message_updates(db: AsyncDatabase):
    """
    Watches for updates in the MessageCollection and sends message status updates
    to the sender when the message status changes.
    """
    async with db.message.watch(
        pipeline=[{"$match": {"operationType": "update"}}]
    ) as stream:
        async for change in stream:
            try:
                # Extract the required data from the event
                message_id = change["documentKey"]["_id"]
                updated_field = change["updateDescription"]["updatedFields"]
                status = change["updateDescription"]["updatedFields"]["status"]

                # Get the timestamp of the update
                timestamp = next(iter(updated_field.values()))

                # Fetch the updated message from the database
                message_request = await db.message.find_one({"_id": message_id})

                # Construct a MessageEvent Object
                message_event = MessageEvent(
                    message_id=str(message_id), timestamp=timestamp
                )

                # Create a MessageStatusUpdate object to send to the user
                sync_message = MessageStatusUpdate(
                    data=[message_event],
                    status=status,
                )

                # Send the status update to the message sender
                await send_sync_message(
                    user_ids=[message_request["sender_id"]], message_data=sync_message
                )

            except Exception as e:
                print(f"Error processing user update : {e}")


async def distribute_published_messages():
    while True:
        consumer = AIOKafkaConsumer(
            "message", bootstrap_servers=settings.KAFKA_CONNECTION
        )

        try:
            await consumer.start()

            # Asyncronous Loop for iterating over the available messages
            async for msg in consumer:
                # Decoding the received data
                data = json.loads(msg.value.decode("utf-8"))
                message_alias = MessageNoAlias(**data)
                message = Message.model_validate(
                    message_alias.model_dump(by_alias=True)
                )

                # Send the message back to sender with all data
                await send_message(user_id=message.sender_id, message_data=message)

                # Getting the receiver's ID
                receiver_id = await get_user_form_conversation(
                    message.conversation_id, message.sender_id
                )

                # Sending the message to receiver
                await send_message(user_id=receiver_id, message_data=message)

        except json.JSONDecodeError as e:
            print("Error decoding the kafka message : ", e)
        except Exception as e:
            print("Error in kafka consumer : ", e)

        finally:
            await consumer.stop()
            print("Reconnecting in 5 sec")
            asyncio.sleep(5)
