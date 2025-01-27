from bson import ObjectId
import json
import asyncio
from aiokafka import AIOKafkaConsumer
from .config import (
    user_collection,
    FriendCollection,
    KAFKA_CONNECTION,
    ConversationCollection,
)
from .router.sync_sockets import send_message
from .schemas import OnlineStatusMessage


async def watch_user_updates():
    async with user_collection.watch(
        pipeline=[{"$match": {"operationType": "update"}}]
    ) as stream:
        async for change in stream:
            try:
                cursor = FriendCollection.find({"_id": change["documentKey"]["_id"]})

                # Extracting the `friends_id` values from each result document
                friends_ids = [doc["friends_id"] async for doc in cursor]

                # Sending the data to the online frinds
                await send_message(
                    friends_ids, change["updateDescription"]["updatedFields"]
                )

                # updating the lastupdate fo friends data
                await FriendCollection.update_many(
                    {"friends_id": change["documentKey"]["_id"]},
                    {"$set": {"update_at": change["wallTime"]}},
                )

            except Exception as e:
                print(f"Error processing user update : {e}")


async def handle_online_status_update():
    while True:
        consumer = AIOKafkaConsumer("online_status", bootstrap_servers=KAFKA_CONNECTION)

        try:
            await consumer.start()

            # Asyncronous Loop for iterating over the available messages
            async for msg in consumer:
                # Decoding the received data
                data = json.loads(msg.value.decode("utf-8"))
                user_id = data["user_id"]
                user_list = []

                try:
                    # Retrive the conversations with the user
                    async for document in ConversationCollection.find(
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
                    print(f"kafak message recieved and list of user ids: {user_list}")
                    await send_message(user_ids=user_list, message_data=msg_data)

                except Exception as e:
                    print("Error retrieving user:", e)
        except json.JSONDecodeError as e:
            print("Error decoding the kafka message : ", e)
        except Exception as e:
            print("Error in kafka consumer : ", e)

        finally:
            await consumer.stop()
            print("Reconnecting in 5 sec")
            asyncio.sleep(5)
