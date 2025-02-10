from typing import Dict, List, Optional
import json
from datetime import datetime
from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    WebSocketException,
    status,
    Query,
)
from starlette.websockets import WebSocket, WebSocketDisconnect

from ..config import (
    FriendCollection,
    ConversationCollection,
    MessageCollection,
)
from ..deps import get_user_from_access_token
from ..schemas import (
    UserOut,
    MessageData,
    Message,
    Conversation,
    MessagePacket,
    PacketType,
)
from ..utils import get_user_form_conversation


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connection: Dict[ObjectId, WebSocket] = {}

    async def connect(self, user_id: ObjectId, websocket: WebSocket):
        await websocket.accept()
        self.active_connection[user_id] = websocket

    def disconnect(self, user_id: ObjectId):
        if user_id in self.active_connection:
            del self.active_connection[user_id]

    def is_online(self, user_id: ObjectId):
        return user_id in self.active_connection

    async def send_personal_message(self, user_id: ObjectId, message: MessagePacket):
        await self.active_connection[user_id].send_text(message.model_dump_json())


connections = ConnectionManager()


@router.websocket("/chat/socket")
async def messages_socket(
    websocket: WebSocket, user: UserOut = Depends(get_user_from_access_token)
):
    await connections.connect(user.id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data["type"] == "ping":
                await connections.send_personal_message(
                    user_id=user.id, message=MessagePacket(packet_type="pong")
                )
            else:
                await handle_recieved_message(user.id, MessageData(**data["data"]))

    except WebSocketDisconnect:
        connections.disconnect(user.id)
    return


async def handle_recieved_message(user_id: ObjectId, data: MessageData):
    # when user start new conversation and don't have the conversation id
    if not data.conversation_id:
        if not data.receiver_id:
            raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA)

        # check if the users are friend or not
        friend = await FriendCollection.find_one(
            {"user_id": user_id, "friends_id": ObjectId(data.receiver_id)}
        )

        if not friend:
            raise WebSocketException(
                code=status.WS_1003_UNSUPPORTED_DATA, reason="Invalid reciever id"
            )

        # check if conversations between the user exist
        conversation = await ConversationCollection.find_one(
            {"participants": {"$all": [user_id, ObjectId(data.receiver_id)]}}
        )

        if conversation:
            # add the conversation id to the message data
            data.conversation_id = conversation["_id"]

        else:
            # create a new conversation document
            conv_data = Conversation(participants=[user_id, ObjectId(data.receiver_id)])
            conversation_resp = await ConversationCollection.insert_one(
                conv_data.model_dump(exclude=["id"])
            )
            data.conversation_id = str(conversation_resp)

    # create a Message instance
    message_data = Message(
        sender_id=user_id,
        conversation_id=ObjectId(data.conversation_id),
        message=data.message,
        temp_id=data.temp_id,
    )

    # get the other participants
    participant_id = await get_user_form_conversation(
        conv_id=message_data.conversation_id, user_id=message_data.sender_id
    )

    # store the message document and add the id to the Message instance
    response = await MessageCollection.insert_one(
        message_data.model_dump(exclude=["id", "temp_id"])
    )
    message_data.id = response.inserted_id

    data_packet = MessagePacket(packet_type=PacketType.message, data=message_data)

    # check the online status of the reciever
    if connections.is_online(participant_id):

        # send the message to the user reciever
        await connections.send_personal_message(
            user_id=participant_id, message=data_packet
        )

    # updating the last_message_date and pushing the new message id to unseen_message_id
    await ConversationCollection.find_one_and_update(
        {"_id": message_data.conversation_id},
        {
            "$set": {"last_message_date": message_data.sending_time},
            "$push": {"unseen_message_ids": message_data.id},
        },
    )

    # sending the message back to sender with other information
    await connections.send_personal_message(
        user_id=message_data.sender_id, message=data_packet
    )


async def send_message(user_id: ObjectId, message_data: Message):
    """
    Send message to a userId if online

    Args:
        user_id : User Id (ObjectId)
        message_data : The message to send.
    """

    try:
        if connections.is_online(user_id):
            data_packet = MessagePacket(
                packet_type=PacketType.message, data=message_data
            )

            await connections.send_personal_message(user_id, data_packet)
    except Exception as e:
        print(e)


@router.get("/updated-status")
async def get_message_status_updates(
    user: UserOut = Depends(get_user_from_access_token),
    last_updated: Optional[datetime] = Query(
        None, description="conversation which have message after this date"
    ),
):
    try:
        # Query the database for messages sent by the user that have been received or seen after `last_updated`
        cursor = MessageCollection.find(
            {
                "sender_id": user.id,
                "$or": [
                    {"received_time": {"$gt": last_updated}},
                    {"seen_time": {"$gt": last_updated}},
                ],
            }
        )

        # Convert the database response into a list of Message objects
        response = await cursor.to_list(length=None)
        message_list: List[Message] = [Message(**message) for message in response]

        # Return the list of updated messages
        return {"message_status_updates": message_list}
    except Exception as e:
        print(e)
