from bson import ObjectId
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, Path, HTTPException, Body, Query
from pymongo import ReturnDocument

from app.core.schemas import (
    UserOut,
    UserBrief,
    UserAuthOut,
    FriendRequestIn,
    FriendRequestDB,
    Friends_Status,
    FriendRequestOut,
)

from app.core.db import AsyncDatabase, get_async_database
from app.api.user.services import get_full_user
from app.deps import get_user_from_access_token_http

from .services import (
    create_friends,
    get_friends_list,
    are_friends,
    reject_friend_request,
    _get_friend,
)

router = APIRouter()


@router.post("/make-request", status_code=201)
async def make_friend_request(
    request_data: Annotated[FriendRequestIn, Body()],
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    # Finding the requested user by username
    requested_user = await db.user_auth.find_one({"username": request_data.username})

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
    if await are_friends(db, user.id, requested_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are already friends"
        )

    # Check if the friend request already exist
    if await db.friend_request.find_one(
        {
            "sender_id": user.id,
            "receiver_id": requested_user["_id"],
            "status": Friends_Status.pending.value,
        }
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
    result = db.friend_request.insert_one(
        request.model_dump(by_alias=True, exclude={"id"})
    )

    return


@router.get("/get-requests")
async def list_friend_request(
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    data = []

    async for document in db.friend_request.find(
        {"receiver_id": user.id, "status": Friends_Status.pending.value}
    ):
        sender = await get_full_user(db, ObjectId(document["sender_id"]))
        sender_data = UserBrief.model_validate(sender.model_dump())

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
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    f_request = await db.friend_request.find_one_and_update(
        {
            "_id": ObjectId(request_id),
            "receiver_id": user.id,
            "status": Friends_Status.pending.value,
        },
        {"$set": {"status": Friends_Status.accepted.value}},
        return_document=ReturnDocument.AFTER,
    )

    if f_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No friend request found."
        )

    friend = await create_friends(
        db, user1_id=f_request["receiver_id"], user2_id=f_request["sender_id"]
    )

    return friend


@router.patch("/reject-request/{request_id}")
async def reject_request(
    request_id: Annotated[str, Path(title="Id of the friend request to be accepted")],
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    return await reject_friend_request(
        db=db, id=ObjectId(request_id), receiver_id=user.id
    )


@router.get("/get-friends")
async def list_friends(
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    updated_after: Optional[datetime] = Query(
        None,
        alias="updateAfter",
        description="Return only friends updated after this date (ISO 8601 format)",
    ),
    db: AsyncDatabase = Depends(get_async_database),
):
    friends = await get_friends_list(db, user.id, updated_after)
    friend_list = [UserOut(**user) for user in friends]

    return friend_list


@router.get("/ger-friend/{id}")
async def get_friend(
    id: Annotated[str, Path(title="Id of the friend")],
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    return await _get_friend(db=db, user_id=user.id, friend_id=ObjectId(id))
