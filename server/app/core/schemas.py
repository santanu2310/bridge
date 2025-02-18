from typing import Optional, List, Any, Callable, Literal, Union
from datetime import datetime
from bson import ObjectId
from typing_extensions import Annotated
from enum import Enum, unique
from pydantic import BaseModel, Field, EmailStr, FileUrl
from pydantic_core import core_schema


class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            try:
                return ObjectId(input_value)
            except Exception as e:
                raise ValueError(f"Invalid ObjectId: {input_value}") from e

        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )


PyObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]


@unique
class Friends_Status(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class Message_Status(str, Enum):
    send = "send"
    recieved = "received"
    seen = "seen"


class PacketType(str, Enum):
    ping = "ping"
    pong = "pong"
    message = "message"


class SyncMessageType(str, Enum):
    message_status = "message_status"
    online_status = "online_status"
    friend_update = "friend_update"
    friend_request = "friend_request"


class FileType(str, Enum):
    video = "video"
    image = "image"
    audio = "audio"
    document = "document"
    attachment = "attachment"


# class User(BaseModel):
#     id: Optional[PyObjectId] = Field(alias="_id", default=None)
#     username: str
#     full_name: str | None = None
#     email: EmailStr
#     password: str | None = None
#     bio: str | None = None
#     profile_picture: str | None = None
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     hashing_salt: str | None = None


class UserAuth(BaseModel):
    id: Optional[PyObjectId] = Field(validation_alias="_id", default=None)
    username: str
    email: EmailStr
    password: str
    hashing_salt: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserAuthOut(BaseModel):
    id: PyObjectId = Field(validation_alias="_id")
    username: str
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfile(BaseModel):
    id: Optional[PyObjectId] = Field(validation_alias="_id", default=None)
    auth_id: PyObjectId
    full_name: str
    bio: str | None = None
    profile_picture: str | None = None
    banner_picture: Optional[FileUrl] = None
    location: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRegistration(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: PyObjectId = Field(alias="_id", serialization_alias="id")
    username: str
    full_name: str | None = None
    email: EmailStr
    bio: str | None = None
    profile_picture: str | None = None
    banner_picture: Optional[FileUrl] = None
    location: str | None = None
    created_at: datetime | None = None


class UpdatebleUser(BaseModel):
    bio: str | None = None
    profile_picture: str | None = None
    banner_picture: Optional[FileUrl] = None
    location: str | None = None


class Friends(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    friends_id: PyObjectId
    update_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FriendRequestIn(BaseModel):
    username: str
    message: str | None = None


class FriendRequestDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    sender_id: PyObjectId
    receiver_id: PyObjectId
    message: str | None = None
    status: Friends_Status = Friends_Status.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FriendRequestOut(BaseModel):
    id: str
    user: UserOut
    message: str | None
    status: Friends_Status
    created_time: datetime


class Conversation(BaseModel):
    id: Optional[PyObjectId] = Field(
        alias="_id", default=None, serialization_alias="id"
    )
    participants: List[PyObjectId]
    start_date: datetime = Field(default_factory=datetime.utcnow)
    last_message_date: datetime = Field(default_factory=datetime.utcnow)


class FileInfo(BaseModel):
    type: FileType
    name: Optional[str] = None
    key: Optional[str] = None
    temp_file_id: Optional[str] = None
    size: Optional[int] = None


class Message(BaseModel):
    id: Optional[PyObjectId] = Field(validation_alias="_id", default=None)
    temp_id: str | None = None  # exclued this while inserting to database
    conversation_id: PyObjectId
    sender_id: PyObjectId
    receiver_id: Optional[PyObjectId] = None
    message: str
    attachment: Optional[FileInfo] = None
    sending_time: datetime = Field(default_factory=datetime.utcnow)
    received_time: Optional[datetime] = None
    seen_time: Optional[datetime] = None
    status: Message_Status = Message_Status.send


class MessageNoAlias(Message):
    id: Optional[PyObjectId] = Field(default=None, serialization_alias="_id")


class ConversationResponse(Conversation):
    messages: List[Message]


class FileData(BaseModel):
    temp_file_id: Optional[str] = None
    name: Optional[str] = None


class MessageData(BaseModel):
    message: str
    receiver_id: str | None
    conversation_id: str | None
    temp_id: str | None
    attachment: Optional[FileData] = None


class MessagePacket(BaseModel):
    type: PacketType
    data: Optional[Union[Message, MessageData]] = None


class MessageEvent(BaseModel):
    message_id: str
    timestamp: datetime


class BaseMessage(BaseModel):
    type: str


class OnlineStatusMessage(BaseMessage):
    type: str = SyncMessageType.online_status.value
    user_id: str
    status: Literal["online", "offline"]


class MessageStatusUpdate(BaseMessage):
    type: str = SyncMessageType.message_status.value
    data: List[MessageEvent]
    status: Message_Status


class FriendUpdateMessage(BaseMessage):
    type: str = SyncMessageType.friend_update.value
    full_name: Optional[str]
    bio: Optional[str]
    profile_picture: Optional[str]


class FriendRequestMessage(BaseMessage):
    type: str = SyncMessageType.friend_request.value
    request_id: str
    user: UserOut
    message: Optional[str]
    status: Friends_Status
    created_time: datetime


# Combined Message Model for Websocket Handeling
SyncSocketMessage = Union[
    OnlineStatusMessage, FriendUpdateMessage, FriendRequestMessage, MessageStatusUpdate
]


class SyncPacket(BaseModel):
    type: PacketType
    data: Optional[SyncSocketMessage] = None
