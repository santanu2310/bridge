import io
import asyncio
from typing import Union
import boto3  # type: ignore
from datetime import datetime
from bson import ObjectId
import logging
from botocore.exceptions import ClientError  # type: ignore
from botocore.client import Config  # type: ignore
from PIL import Image
from app.core.config import create_celery_client, settings
from app.core.schemas import Message, MediaType
from app.core.db import create_sync_client, SyncDatabase
from app.utils import get_file_extension, publish_user_message

celery_app = create_celery_client()
logger = logging.getLogger(__name__)


@celery_app.task
def process_media_message(message_id: str):
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

            # Update the conversation last_message_date
            db.conversation.find_one_and_update(
                {"_id": message.conversation_id},
                {
                    "$set": {"last_message_date": message.sending_time},
                },
            )

            # Publish the message to kafak
            asyncio.run(publish_user_message(message))
        except ClientError as e:
            print(f"Error copying object: {e}")


@celery_app.task
def process_profile_media(file_id: str, user_id: str, media_type: MediaType):
    with create_sync_client() as sync_client:
        db = SyncDatabase(sync_client, settings.DATABASE_NAME)

        # TODO: Manage the s3_clienta and database globally
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name="ap-south-1",
            config=Config(signature_version="s3v4"),
        )

        try:
            # Getting the image from S3
            obj = s3_client.get_object(
                Bucket=settings.BUCKET_NAME,
                Key="temp/wallpaperflare.com_wallpaper(1).jpg",
            )
            image_data = obj["Body"].read()

            # Open the image using PIL.
            image: Union[Image.Image] = Image.open(io.BytesIO(image_data))
            width, height = image.size

            if width != height:
                # Crop image to a square aspect ratio if the original is rectangular.
                square_size = min(width, height)

                left = (width - square_size) // 2
                top = (height - square_size) // 2
                right = left + square_size
                bottom = top + square_size

                image = image.crop((left, top, right, bottom))

            # Change the resolution
            target_size = (480, 480)
            image.thumbnail(target_size)

            output_buffer = io.BytesIO()
            image.convert("RGB").save(output_buffer, format="WebP")

            output_buffer.seek(0)
            # image_bytes = output_buffer.read()

            new_key = f"{media_type}/{user_id}"
            # Step 3: Reupload the processed image back to S3.
            s3_client.upload_fileobj(
                output_buffer,
                settings.BUCKET_NAME,
                new_key,
                ExtraArgs={"ContentType": "image/jpeg"},
            )

            # Add the new image key to database
            db.user_profile.find_one_and_update(
                {"auth_id": ObjectId(user_id)}, {"$set": {media_type: new_key}}
            )

        except Exception as e:
            logger.info(e)

        # Delete the old image from S3.
        s3_client.delete_object(Bucket=settings.BUCKET_NAME, Key=file_id)
