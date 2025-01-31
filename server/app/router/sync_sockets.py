import asyncio
import json
from aiokafka import AIOKafkaProducer
from bson import ObjectId
from typing import Literal, List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pymongo import UpdateOne
from ..schemas import (
    SyncSocketMessage,
    UserOut,
    SyncPacket,
    PacketType,
    SyncMessageType,
    MessageStatusUpdate,
    Message_Status,
)
from ..deps import get_user_from_access_token
from ..config import KAFKA_CONNECTION, MessageCollection

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connection: Dict[ObjectId, WebSocket] = {}

    async def connect(self, user_id: ObjectId, websocket: WebSocket):
        await websocket.accept()
        self.active_connection[user_id] = websocket
        await notify_online_status(user_id, "online")

    async def disconnect(self, user_id: ObjectId):
        if user_id in self.active_connection:
            del self.active_connection[user_id]
            await notify_online_status(user_id, "offline")

    def is_online(self, user_id: ObjectId):
        return user_id in self.active_connection

    async def send_personal_message(self, user_id: ObjectId, message: SyncPacket):
        if self.active_connection[user_id]:
            await self.active_connection[user_id].send_text(message.model_dump_json())


connections = ConnectionManager()


@router.websocket("/socket")
async def websocket_endpoint(
    websocket: WebSocket, user: UserOut = Depends(get_user_from_access_token)
):
    await connections.connect(user.id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data["type"] == "ping":
                await connections.send_personal_message(
                    user_id=user.id, message=SyncPacket(packet_type="pong")
                )
            else:
                await handle_recieved_message(user_id=user.id, message=data["data"])

    except WebSocketDisconnect:
        await connections.disconnect(user.id)
    return


async def handle_recieved_message(user_id: ObjectId, message: SyncSocketMessage):
    if message["type"] == SyncMessageType.message_status:
        try:
            # Parse the incoming message data into a structured model
            message = MessageStatusUpdate(**message)
            message_status = message.status.value

            # Determine the correct field to update in the database
            time_field = (
                "seen_time"
                if message_status == Message_Status.seen
                else "received_time"
            )
            # Prepare bulk update operations for each message in the update list
            updates = [
                UpdateOne(
                    {"_id": ObjectId(obj.message_id), time_field: None},
                    {
                        "$set": {
                            "status": message_status,
                            time_field: obj.timestamp,
                        }
                    },
                )
                for obj in message.data
            ]

            # Only proceed with the database update if there are updates to make
            if updates:
                request = await MessageCollection.bulk_write(updates)
        except Exception as e:
            print(e)


async def send_message(user_ids: List[ObjectId], message_data: SyncSocketMessage):
    """
    Send message to list of users IDs if online

    Args:
        user_ids : List of IDs to send the message to.
        message_data : The message to send.
    """

    try:
        for user_id in user_ids:
            if connections.is_online(user_id):
                data_packet = SyncPacket(
                    packet_type=PacketType.message, data=message_data
                )

                await connections.send_personal_message(user_id, data_packet)
    except Exception as e:
        print(e)


async def notify_online_status(user_id: str, is_online: Literal["online", "offline"]):
    """
    Notify Kafka about the online status of a user.

    Args:
        user_id (str): The unique identifier of the user.
        is_online (Literal["online", "offline"]): The online status of the user,
            either "online" or "offline".

    This function:
        1. Creates an AIOKafkaProducer instance to connect to the Kafka server.
        2. Encodes a message containing the user's ID and status as JSON.
        3. Publishes the message to the "online_status" Kafka topic.
        4. Gracefully stops the Kafka producer after sending the message.

    If any error occurs during this process, it logs an error message.

    Raises:
        Prints an error message if the message could not be published to Kafka.
    """
    try:
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_CONNECTION)
        await producer.start()

        message = {"user_id": str(user_id), "status": is_online}
        data = json.dumps(message).encode("utf-8")

        await producer.send_and_wait("online_status", data)
        await producer.stop()
    except Exception as e:
        print("Unable to publish message to kafka : ", e)
