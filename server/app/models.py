from typing import Optional
from bson import ObjectId
from datetime import datetime
from typing_extensions import Annotated
from pydantic import BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from .schemas import PyObjectId

# PyObjectId = Annotated[str, BeforeValidator(str)]


# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v, *args, **kwargs):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return ObjectId(v)

#     @classmethod
#     def __get_pydantic_json_schema__(cls, field_schema):
#         field_schema.update(type="string")

#     def __str__(self):
#         # This ensures the ObjectId will be converted to a string when serialized
#         return str(self)


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    full_name: str | None = None
    email: EmailStr
    password: str = None
    bio: str | None = None
    profile_picture: str = None
    created_at: datetime = datetime.now()
    hashing_salt: str = None


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
