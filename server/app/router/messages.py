from typing import Dict
import json
from bson import ObjectId
from fastapi import APIRouter, Depends, Request, WebSocketException, status
from starlette.websockets import WebSocket, WebSocketDisconnect

from ..config import FriendCollection, ConversationCollection, MessageCollection
from ..deps import get_user_from_access_token
from ..schemas import (
    UserOut,
    MessageData,
    Message,
    Conversation,
    PyObjectId,
    Message_Status,
)
from ..utils import get_user_form_conversation

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connection: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connection[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connection:
            del self.active_connection[user_id]

    def is_online(self, user_id: str):
        return user_id in self.active_connection

    async def send_personal_message(self, user_id: str, message: Message):
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
            await handle_recieved_message(user.id, MessageData(**json.loads(data)))

    except WebSocketDisconnect:
        connections.disconnect(user.id)
    return


async def handle_recieved_message(user_id: ObjectId, data: MessageData):
    # when user start new conversation and don't have the conversation id
    if not data.conversation_id:
        if not data.reciever_id:
            raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA)

        # check if the users are friend or not
        friend = await FriendCollection.find_one(
            {"user_id": user_id, "friends_id": ObjectId(data.reciever_id)}
        )

        if not friend:
            raise WebSocketException(
                code=status.WS_1003_UNSUPPORTED_DATA, reason="Invalid reciever id"
            )

        # check if conversations between the user exist
        conv_response = await ConversationCollection.find_one(
            {"participants": {"$all": [user_id, ObjectId(data.reciever_id)]}}
        )

        conversation = conv_response["_id"]

        if not conversation:
            # create a new conversation document
            conv_data = Conversation(participants=[user_id, ObjectId(data.reciever_id)])
            conversation = await ConversationCollection.insert_one(
                conv_data.model_dump(exclude=["id"])
            )

        data.conversation_id = conversation

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

    # check the online status of the reciever
    if connections.is_online(participant_id):

        # update the status of the message
        message_data.status = Message_Status.recieve

        # store the message document and add the id to the Message instance
        response = await MessageCollection.insert_one(
            message_data.model_dump(exclude=["id", "temp_id"])
        )
        message_data.id = response.inserted_id

        # send the message to the user reciever
        await connections.send_personal_message(
            user_id=participant_id, message=message_data
        )

    else:
        # store the message document and add the id to the Message instance
        response = await MessageCollection.insert_one(
            message_data.model_dump(exclude=["id", "temp_id"])
        )

        message_data.id = response.inserted_id

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
        user_id=message_data.sender_id, message=message_data
    )
