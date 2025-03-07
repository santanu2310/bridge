import os
import uuid
from passlib.context import CryptContext  # type: ignore
from aiokafka import AIOKafkaProducer  # type: ignore
import boto3  # type: ignore
from botocore.client import Config  # type: ignore
from botocore.exceptions import ClientError  # type: ignore

from app.core.schemas import (
    Message,
)
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt() -> str:
    return os.urandom(10).hex()


def hash_password(password: str, salt: str) -> str:
    hashed_password = pwd_context.hash(password + salt)
    return hashed_password


def verify_password(password_hash: str, password_plain: str, salt: str):
    return pwd_context.verify(password_plain + salt, password_hash)


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
        producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_CONNECTION)
        await producer.start()
        data = message.model_dump_json(by_alias=True).encode("utf-8")

        await producer.send_and_wait("message", data)
        await producer.stop()
    except Exception as e:
        await producer.stop()
        print("Unable to publish message to kafka : ", e)


def create_presigned_upload_url():
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
