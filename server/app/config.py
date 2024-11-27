import os
from dotenv import load_dotenv
import motor.motor_asyncio

# take environment variables from .env.
load_dotenv()

MONGODB_URL = os.environ["MONGODB_URL"]
LOCAL_MONGOD_URL = os.environ["LOCAL_MONGOD_URL"]

client = motor.motor_asyncio.AsyncIOMotorClient(LOCAL_MONGOD_URL)
db = client.get_database("bridge")

user_collection = db.get_collection("users")
FriendRequestCollection = db.get_collection("friend_request")
FriendCollection = db.get_collection("friends")
ConversationCollection = db.get_collection("conversation")
MessageCollection = db.get_collection("message")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# JWT secrets
JWT_ACCESS_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]
ALGORITHM = "HS256"


TIMEZONE = "Asia/Kolkata"
