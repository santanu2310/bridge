import os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import MongoClient

from celery import Celery

# take environment variables from .env.
load_dotenv()

# MONGODB_URL = os.environ["MONGODB_URL"]
LOCAL_MONGOD_URL = os.environ["LOCAL_MONGOD_URL"]

client = motor.motor_asyncio.AsyncIOMotorClient(LOCAL_MONGOD_URL)
db = client.get_database("bridge")

user_collection = db.get_collection("users")
FriendRequestCollection = db.get_collection("friend_request")
FriendCollection = db.get_collection("friends")
ConversationCollection = db.get_collection("conversation")
MessageCollection = db.get_collection("message")


# Synchronous DB connection

sync_client = MongoClient(LOCAL_MONGOD_URL)
sync_db = sync_client.get_database("bridge")

SyncMessageCollection = sync_db.get_collection("message")
SyncConversationCollection = sync_db.get_collection("conversation")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# JWT secrets
JWT_ACCESS_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]
ALGORITHM = "HS256"

# Redis
# REDIS_CLIENT = aioredis.Redis(host="localhost", port=6379, decode_responses=True)

# Kafka
KAFKA_CONNECTION = "localhost:9092"

# AWS
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
BUCKET_NAME = os.environ["BUCKET_NAME"]


celery_app = Celery("tasks", broker="redis://localhost:6379")
