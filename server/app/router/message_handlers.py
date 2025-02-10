from typing import Annotated
import uuid
from bson import ObjectId
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    Depends,
    status,
    Body,
    HTTPException,
    Query
)

from ..config import (
    MessageCollection,
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
    BUCKET_NAME,
)
from ..deps import get_user_from_access_token
from ..schemas import (
    UserOut,
    MessageData,
    Message,
    FileInfo,
    FileType,
)
from ..utils import get_or_create_conversation
from ..tasks import process_media_message

router = APIRouter()


@router.get("/upload-url")
async def create_presigned_post(user: UserOut = Depends(get_user_from_access_token)):
    conditions = [
        ["content-length-range", 0, 20971520],  # 20 MB limit
    ]

    unique_id = str(uuid.uuid4())

    # Generate a presigned S3 POST URL
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="ap-south-1",
        config=Config(signature_version="s3v4"),
    )
    try:
        response = s3_client.generate_presigned_post(
            BUCKET_NAME,
            f"temp/{unique_id}",
            Conditions=conditions,
            ExpiresIn=360,
        )

    except ClientError as e:
        print(e)
        return None

    # The response contains the presigned URL and required fields
    return response

@router.get("/download-url")
async def create_presigned_download_url(user: UserOut = Depends(get_user_from_access_token), key: str = Query(description="Key of the file")):

    if not key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'key' is required")
    # Generate a S3 Slient
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="ap-south-1",
        config=Config(signature_version="s3v4"),
    )
    try:
        # Generate a presigned GET URL
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': key},
                                                    ExpiresIn=600)

        return response
        
    except ClientError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)



@router.post("/media-message")
async def handle_media_message(
    data: Annotated[MessageData, Body(...)],
    user: UserOut = Depends(get_user_from_access_token),
):
    # Check for conversation Id
    if not data.conversation_id:
        if not data.receiver_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        # Get the conversation Id and add it to data
        data.conversation_id = get_or_create_conversation(
            user_id=user.id, friend_id=ObjectId(data.receiver_id)
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
    message_response = await MessageCollection.insert_one(
        message.model_dump(exclude=["id"])
    )
    process_media_message.delay(str(message_response.inserted_id))
    print(f"{str(message_response.inserted_id)=}")
