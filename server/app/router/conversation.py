from bson import ObjectId
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import JSONResponse

from ..config import (
    ConversationCollection,
    MessageCollection,
)

from ..schemas import (
    UserOut,
    Message,
    ConversationResponse,
)

from ..deps import get_user_from_access_token
from .sync_sockets import connections

router = APIRouter()


@router.get("/get-conversation")
async def retrive_conversation(
    user: UserOut = Depends(get_user_from_access_token),
    conversation_id: Optional[str] = Query(
        None, description="conversation id who's conversation is to retrive"
    ),
    friend_id: Optional[str] = Query(
        None, description="freind id who's conversation is to retrive"
    ),
    before: Optional[datetime] = Query(
        None, description="Fetch message sent before this timestamp"
    ),
    after: Optional[datetime] = Query(
        None, description="Fetch message sent after this timestamp"
    ),
    limit: Optional[int] = Query(
        20, ge=1, le=50, description="number of messages to retrieve (1-50)"
    ),
):
    try:
        # This if else block retrives the conversation based on the data provided
        if not conversation_id:
            if friend_id:
                conv_response = await ConversationCollection.find_one(
                    {"participants": {"$all": [user.id, ObjectId(friend_id)]}}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nither 'conversation_id' not 'friend_id' is given",
                )
        else:
            conv_response = await ConversationCollection.find_one(
                {"_id": ObjectId(conversation_id)}
            )

        if not conv_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Using dictionary unpacking to initialize ConversationResponse
        conversation = ConversationResponse(**conv_response)

        # Setting message query
        message_query = {"conversation_id": conversation.id}
        if after:
            message_query.setdefault("sending_time", {})["$gt"] = after
        else:
            message_query["sending_time"] = {"$lt": before}

        # Retrives messages, unpack and add the data to the converstion
        message_cursor = (
            MessageCollection.find(message_query).sort("sending_time").limit(limit)
        )
        messages = await message_cursor.to_list(length=limit)

        conversation.messages = [Message(**message) for message in messages]

        return conversation

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/list-conversations")
async def list_conversations(
    user: UserOut = Depends(get_user_from_access_token),
    after: Optional[datetime] = Query(
        None, description="conversation which have message after this date"
    ),
):

    pipeline = [
        {
            "$match": {
                "participants": {"$all": [user.id]},
            }
        },
        {
            "$lookup": {
                "from": "message",
                "localField": "_id",
                "foreignField": "conversation_id",
                "as": "messages",
            }
        },
    ]

    if after:
        pipeline[0]["$match"]["last_message_date"] = {"$gt": after}

    try:
        cursor = ConversationCollection.aggregate(pipeline)
        response = await cursor.to_list(length=None)

        # Map to pydentic model
        conversations = [
            ConversationResponse(**conversation) for conversation in response
        ]

        return conversations

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error fetching users list",
        )


@router.get("/online-users")
async def get_online_status_for_active_conversations(
    user: UserOut = Depends(get_user_from_access_token),
):
    pipeline = [
        {"$match": {"participants": {"$all": [user.id]}}},
        {"$project": {"_id": 0, "participants": 1}},
    ]

    try:
        cursor = ConversationCollection.aggregate(pipeline=pipeline)

        friends_id = set()
        async for document in cursor:
            friends_id.update(
                str(id) for id in document["participants"] if id != user.id
            )

        online_friends = [
            id for id in friends_id if connections.is_online(ObjectId(id))
        ]

        return JSONResponse(
            content={"online_friends": online_friends}, status_code=status.HTTP_200_OK
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
