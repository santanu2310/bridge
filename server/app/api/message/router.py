from typing import Annotated, List, Optional
import uuid
from bson import ObjectId
from datetime import datetime
import boto3  # type: ignore
from botocore.client import Config  # type: ignore
from botocore.exceptions import ClientError  # type: ignore
from fastapi import APIRouter, Depends, status, Body, HTTPException, Query

from app.core.config import settings
from app.core.db import (
    AsyncDatabase,
    get_async_database,
    SyncDatabase,
    get_sync_database,
)
from app.deps import get_user_from_access_token_http
from app.core.schemas import (
    UserAuthOut,
    MessageData,
    Message,
    FileInfo,
    FileType,
)
from .services import get_or_create_conversation
from app.tasks import process_media_message

router = APIRouter()


@router.get("/updated-status")
async def get_message_status_updates(
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    last_updated: Optional[datetime] = Query(
        None, description="conversation which have message after this date"
    ),
    db: AsyncDatabase = Depends(get_async_database),
):
    try:
        # Query the database for messages sent by the user that have been received or seen after `last_updated`
        cursor = db.message.find(
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


@router.get("/upload-url")
async def create_presigned_post(
    user: UserAuthOut = Depends(get_user_from_access_token_http),
):
    conditions = [
        ["content-length-range", 0, 20971520],  # 20 MB limit
    ]

    unique_id = str(uuid.uuid4())

    # Generate a presigned S3 POST URL
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name="ap-south-1",
        config=Config(signature_version="s3v4"),
    )

    try:
        response = s3_client.generate_presigned_post(
            settings.BUCKET_NAME,
            f"temp/{unique_id}",
            Conditions=conditions,
            ExpiresIn=360,
        )

    except ClientError as e:
        print(f"{e=}")
        return None

    # The response contains the presigned URL and required fields
    return response


@router.get("/download-url")
async def create_presigned_download_url(
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    key: str = Query(description="Key of the file"),
):
    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="'key' is required"
        )
    # Generate a S3 Slient
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name="ap-south-1",
        config=Config(signature_version="s3v4"),
    )
    try:
        # Generate a presigned GET URL
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.BUCKET_NAME, "Key": key},
            ExpiresIn=600,
        )

        return response

    except ClientError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/media-message")
async def handle_media_message(
    data: Annotated[MessageData, Body(...)],
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    if not data.attachment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    # Check for conversation Id
    if not data.conversation_id:
        if not data.receiver_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        # Get the conversation Id and add it to data
        data.conversation_id = await get_or_create_conversation(
            db, user_id=user.id, friend_id=ObjectId(data.receiver_id)
        )

    attachment = FileInfo(
        type=FileType.attachment,
        temp_file_id=data.attachment.temp_file_id,
        name=data.attachment.name,
    )
    # Create a message instance
    message = Message(
        sender_id=user.id,
        conversation_id=ObjectId(data.conversation_id),
        message=data.message,
        temp_id=data.temp_id,
        attachment=attachment,
    )

    # Store the message instance to database collection
    message_response = await db.message.insert_one(message.model_dump(exclude={"id"}))
    process_media_message.delay(str(message_response.inserted_id))
