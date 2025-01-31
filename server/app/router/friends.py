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
    if await FriendCollection.find_one(
        {"user_id": user.id, "friends_id": requested_user["_id"]}
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are already friends"
        )

    # Check if the friend request already exist
    if await FriendRequestCollection.find_one(
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

    return friend


@router.get("/get-friends")
async def list_friends(
    user: UserOut = Depends(get_user_from_access_token),
    updated_after: Optional[datetime] = Query(
        None,
        alias="updateAfter",
        description="Return only friends updated after this date (ISO 8601 format)",
    ),
):

    friends = await get_friends_list(user.id, updated_after)
    friend_list = [UserOut(**user) for user in friends]

    return friend_list
