import os
import jwt
from bson import ObjectId
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, cast
from fastapi import HTTPException, status, Request, WebSocketException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from passlib.context import CryptContext

from .models import UserRegistration, User
from .schemas import Friends
from .config import (
    user_collection,
    FriendCollection,
    ConversationCollection,
    JWT_ACCESS_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    ALGORITHM,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt() -> str:
    return os.urandom(10).hex()


def hash_password(password: str, salt: str) -> str:
    hashed_password = pwd_context.hash(password + salt)
    return hashed_password


def verify_password(password_hash: str, password_plain: str, salt: str):
    return pwd_context.verify(password_plain + salt, password_hash)


async def create_user(user: UserRegistration):
    if await user_collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="username already exist"
        )

    if await user_collection.find_one({"email": user.email}):

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The email address you entered is already in use. Please try a different email.",
        )
    salt = generate_salt()
    user.password = hash_password(user.password, salt)

    user_data = User(**user.dict())
    user_data.hashing_salt = salt

    created = await user_collection.insert_one(
        user_data.model_dump(by_alias=True, exclude=["id"])
    )

    return {"message": "User created successfully"}


def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=3)

    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, key=JWT_ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt


async def create_friends(user1_id: ObjectId, user2_id: ObjectId):
    friend_for_1 = Friends(user_id=user1_id, friends_id=user2_id)
    friend_for_2 = Friends(user_id=user2_id, friends_id=user1_id)

    # TODO: check if the users are already friend

    friend1 = await FriendCollection.insert_one(friend_for_1.model_dump(exclude=["id"]))
    friend2 = await FriendCollection.insert_one(friend_for_2.model_dump(exclude=["id"]))

    print(friend1)
    return friend1


async def is_friends():
    pass


async def get_friends_list(id: ObjectId):
    # Pipeline to get users from user_id in friends collection
    pipeline = [
        {"$match": {"user_id": id}},
        {"$addFields": {"friendsObjectId": {"$toObjectId": "$friends_id"}}},
        {
            "$lookup": {
                "from": "users",
                "localField": "friendsObjectId",
                "foreignField": "_id",
                "as": "friend",
            }
        },
        {"$sort": {"friend.firstname": 1}},
        {"$unwind": "$friend"},
        {"$replaceRoot": {"newRoot": "$friend"}},
    ]

    try:
        cursor = FriendCollection.aggregate(pipeline)
        friends = await cursor.to_list(length=None)

        return friends

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error fetching users list",
        )


async def get_user_form_conversation(conv_id: ObjectId, user_id: ObjectId):
    try:
        conversation = await ConversationCollection.find_one({"_id": conv_id})

        if not conversation:
            raise WebSocketException(
                code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
                reason="Invalid conversation id",
            )

        if not user_id in conversation["participants"]:
            raise WebSocketException(
                code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
                reason="User not a participant in the conversation",
            )

        return next(id for id in conversation["participants"] if id != user_id)

    except Exception as e:
        raise WebSocketException(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )
