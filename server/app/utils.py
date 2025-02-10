import os
import jwt
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status, WebSocketException
from passlib.context import CryptContext
from aiokafka import AIOKafkaProducer

from .models import User
from .schemas import Friends, UserRegistration, Conversation, Message
from .config import (
    user_collection,
    FriendCollection,
    ConversationCollection,
    JWT_ACCESS_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY,
    ALGORITHM,
    KAFKA_CONNECTION,
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
        print("find user using username")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="username already exist"
        )

    if await user_collection.find_one({"email": user.email}):
        print("find user")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The email address you entered is already in use. Please try a different email.",
        )
    salt = generate_salt()
    user.password = hash_password(user.password, salt)

    user_data = User(**user.dict())
    user_data.hashing_salt = salt

    created = await user_collection.insert_one(user_data.model_dump(exclude=["id"]))

    return {"message": "User created successfully"}


def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=3)

    to_encode.update({"exp": expire})

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

    return friend1


async def is_friends():
    pass


async def get_friends_list(id: ObjectId, updated_after: Optional[datetime] = None):
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

    if updated_after:
        pipeline[0]["$match"]["last_message_date"] = {"$gt": updated_after}

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

        if user_id not in conversation["participants"]:
            raise WebSocketException(
                code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
                reason="User not a participant in the conversation",
            )

        return next(id for id in conversation["participants"] if id != user_id)

    except Exception as e:
        print(e)
        raise WebSocketException(
            code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
        )


async def get_or_create_conversation(user_id: ObjectId, friend_id: ObjectId):
    # check if the users are friend or not
    friend = await FriendCollection.find_one(
        {"user_id": user_id, "friends_id": friend_id}
    )

    if not friend:
        raise WebSocketException(
            code=status.WS_1003_UNSUPPORTED_DATA, reason="Invalid reciever id"
        )

    # check if conversations between the user exist
    conversation = await ConversationCollection.find_one(
        {"participants": {"$all": [user_id, friend_id]}}
    )

    if conversation:
        # Return the conversation Id
        return conversation["_id"]

    else:
        # create a new conversation document
        conv_data = Conversation(participants=[user_id, friend_id])
        conversation_resp = await ConversationCollection.insert_one(
            conv_data.model_dump(exclude=["id"])
        )

        # Return the conversation Id
        return str(conversation_resp)


def get_file_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext[1:].lower() if ext else ""


async def publish_user_message(message: Message):
    """
    Notify Kafka about the online status of a user.

    Args:
        message: Message

    This function:
        1. Creates an AIOKafkaProducer instance to connect to the Kafka server.
        2. Encodes a message containing message data.
        3. Publishes the message to the "message" Kafka topic.
        4. Gracefully stops the Kafka producer after sending the message.

    If any error occurs during this process, it logs an error message.

    Raises:
        Prints an error message if the message could not be published to Kafka.
    """
    try:
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_CONNECTION)
        await producer.start()
        data = message.model_dump_json(by_alias=True).encode("utf-8")

        await producer.send_and_wait("message", data)
        await producer.stop()
    except Exception as e:
        await producer.stop()
        print("Unable to publish message to kafka : ", e)
