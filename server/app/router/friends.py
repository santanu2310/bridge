from bson import ObjectId
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, Path, HTTPException, Body, Query
from pymongo import ReturnDocument

from ..config import (
    user_collection,
    FriendRequestCollection,
    FriendCollection,
    ConversationCollection,
    MessageCollection,
)

from ..schemas import (
    UserOut,
    FriendRequestIn,
    FriendRequestDB,
    Friends_Status,
    FriendRequestOut,
    Friends,
    Message,
    ConversationResponse,
)

from ..deps import get_user_from_access_token

from ..utils import create_friends, get_friends_list

router = APIRouter()


@router.post("/make-request", status_code=201)
async def make_friend_request(
    request_data: Annotated[FriendRequestIn, Body()],
    user: UserOut = Depends(get_user_from_access_token),
):

    # Finding the requested user by username
    requested_user = await user_collection.find_one({"username": request_data.username})

    # If the user is not found return a 404 error
    if not requested_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User name not found"
        )

    # Check if the requested user is the same user making the request
    if requested_user["_id"] == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="cannot make request to this username",
        )

    # Check if they are already friends
    if FriendCollection.find_one(
        {"user_id": user.id, "friends_id": requested_user["_id"]}
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are already friends"
        )

    # Check if the friend request already exist
    if FriendRequestCollection.find_one(
        {"sender_id": user.id, "receiver_id": requested_user["_id"]}
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Friend request already exist"
        )

    # Creating a friend request
    request = FriendRequestDB(
        sender_id=ObjectId(user.id),
        receiver_id=requested_user["_id"],
        message=request_data.message,
    )

    # Inserting the request into the collection
    result = FriendRequestCollection.insert_one(
        request.model_dump(by_alias=True, exclude=["id"])
    )

    return


@router.get("/get-requests")
async def list_friend_request(user: UserOut = Depends(get_user_from_access_token)):
    data = []

    async for document in FriendRequestCollection.find(
        {"receiver_id": user.id, "status": Friends_Status.pending.value}
    ):
        sender = await user_collection.find_one(
            {"_id": ObjectId(document["sender_id"])}
        )
        sender_data = UserOut(**sender)

        request = FriendRequestOut(
            id=str(document["_id"]),
            user=sender_data,
            message=document["message"],
            status=document["status"],
            created_time=document["created_at"],
        )
        data.append(request)

    return data


@router.patch("/accept-request/{request_id}")
async def accept_friend_request(
    request_id: Annotated[str, Path(title="Id of the friend request to be accepted")],
    user: UserOut = Depends(get_user_from_access_token),
):
    f_request = await FriendRequestCollection.find_one_and_update(
        {"_id": ObjectId(request_id), "receiver_id": user.id},
        {"$set": {"status": Friends_Status.accepted.value}},
        return_document=ReturnDocument.AFTER,
    )

    if f_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No friend request found."
        )

    friend = await create_friends(
        user1_id=f_request["receiver_id"], user2_id=f_request["sender_id"]
    )

    print(friend)

    return


@router.get("/get-friends")
async def list_friends(user: UserOut = Depends(get_user_from_access_token)):

    friends = await get_friends_list(user.id)
    friend_list = [UserOut(**user) for user in friends]
    print(friend_list)

    return friend_list


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
