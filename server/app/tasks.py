import asyncio
import boto3  # type: ignore
from datetime import datetime
from bson import ObjectId
from botocore.exceptions import ClientError  # type: ignore
from botocore.client import Config  # type: ignore
from app.core.config import create_celery_client, settings
from app.core.schemas import Message
from app.core.db import create_sync_client, SyncDatabase
from app.utils import get_file_extension, publish_user_message

celery_app = create_celery_client()


@celery_app.task
def process_media_message(message_id: str):
    print("started the task...")
    with create_sync_client() as sync_client:
        db = SyncDatabase(sync_client, settings.DATABASE_NAME)
        try:
            # Getting the message from message from id and maping it
            message_response = db.message.find_one({"_id": ObjectId(message_id)})
            message = Message.model_validate(message_response)

            if not message.attachment:
                raise
            # Creating a s3 client
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY,
                region_name="ap-south-1",
                config=Config(signature_version="s3v4"),
            )

            # Generating the key
            present_time = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
            key = "attachment/Bridge_Atachment_" + present_time

            # Transfereing the data
            s3_client.copy_object(
                Bucket=settings.BUCKET_NAME,
                CopySource={
                    "Bucket": settings.BUCKET_NAME,
                    "Key": message.attachment.temp_file_id,
                },
                Key=key,
            )

            # Geting the file
            size = s3_client.head_object(
                Bucket=settings.BUCKET_NAME,
                Key=key,
            ).get("ContentLength", 0)

            # Updating the message data related to attachment
            message.attachment.name = (
                "Bridge_Atachment "
                + present_time
                + "."
                + get_file_extension(message.attachment.name)
            )
            message.attachment.size = size
            message.attachment.key = key

            # Updating the message in database
            db.message.update_one(
                {"_id": message.id},
                {"$set": {"attachment": message.attachment.model_dump()}},
            )

            # Publish the message to kafak
            asyncio.run(publish_user_message(message))
        except ClientError as e:
            print(f"Error copying object: {e}")
