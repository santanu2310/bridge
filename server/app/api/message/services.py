from bson import ObjectId
from fastapi import WebSocketException, status
from app.core.db import AsyncDatabase
from app.core.schemas import Conversation


async def get_or_create_conversation(
    db: AsyncDatabase, user_id: ObjectId, friend_id: ObjectId
):
    # check if the users are friend or not
    friend = await db.friends.find_one({"user_id": user_id, "friends_id": friend_id})

    if not friend:
        raise WebSocketException(
            code=status.WS_1003_UNSUPPORTED_DATA, reason="Invalid reciever id"
        )

    # check if conversations between the user exist
    conversation = await db.conversation.find_one(
        {"participants": {"$all": [user_id, friend_id]}}
    )

    if conversation:
        # Return the conversation Id
        return conversation["_id"]

    else:
        # create a new conversation document
        conv_data = Conversation(participants=[user_id, friend_id])
        conversation_resp = await db.conversation.insert_one(
            conv_data.model_dump(exclude={"id"})
        )

        # Return the conversation Id
        return str(conversation_resp)
