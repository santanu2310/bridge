from typing import Optional, List, Any, Callable, Literal, Union
from datetime import datetime
from bson import ObjectId
from typing_extensions import Annotated
from enum import Enum, unique
from pydantic import BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
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
    recieve = "recieve"
    read = "read"


class UserOut(BaseModel):
    id: Optional[PyObjectId] = Field(
        alias="_id", default=None, serialization_alias="id"
    )
    username: str
    full_name: str | None = None
    email: EmailStr
    bio: str | None = None
    profile_picture: str | None = None
    created_at: datetime | None = None


class UpdatebleUser(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_picture: str | None = None


class Friends(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    friends_id: PyObjectId
    update_at: datetime = datetime.now()
    created_at: datetime = datetime.now()


class FriendRequestIn(BaseModel):
    username: str
    message: str | None = None


class FriendRequestDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    sender_id: PyObjectId
    reciever_id: PyObjectId
    message: str | None = None
    status: Friends_Status = Friends_Status.pending
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class FriendRequestOut(BaseModel):
    id: str
    user: UserOut
    message: str | None
    status: Friends_Status
    created_time: datetime


class Conversation(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    participants: List[PyObjectId]
    unseen_message_ids: List[PyObjectId] = []
    start_date: datetime = Field(default_factory=datetime.now)
    last_message_date: datetime = Field(default_factory=datetime.now)


class Message(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    temp_id: str | None = None  # exclued this while inserting to database
    conversation_id: PyObjectId
    sender_id: PyObjectId
    reciever_id: Optional[PyObjectId] = None
    message: str
    sending_time: datetime = datetime.now()
    status: Message_Status = Message_Status.send


class ConversationResponse(Conversation):
    messages: List[Message]


class MessageData(BaseModel):
    message: str
    reciever_id: str | None
    conversation_id: str | None
    temp_id: str | None


class BaseMessage(BaseModel):
    type: str


class OnlineStatusMessage(BaseMessage):
    type: Literal["online_status"]
    user_id: str
    status: Literal["online", "offline"]


class FriendUpdateMessage(BaseMessage):
    type: Literal["friend_update"]
    full_name: Optional[str]
    bio: Optional[str]
    profile_picture: Optional[str]


class FriendRequestMessage(BaseMessage):
    type: Literal["friend_request"]
    request_id: str
    user: UserOut
    message: Optional[str]
    status: Friends_Status
    created_time: datetime


# Combined Message Model for Websocket Handeling
SyncSocketMessage = Union[
    OnlineStatusMessage, FriendUpdateMessage, FriendRequestMessage
]
