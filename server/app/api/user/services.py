import jwt
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import status
from fastapi.exceptions import HTTPException
from pymongo import ReturnDocument
from app.utils import generate_salt, hash_password
from app.core.db import AsyncDatabase
from app.core.schemas import (
    UserProfile,
    UserAuth,
    UserRegistration,
    UpdatebleUser,
    UserOut,
)
from app.core.config import settings


async def create_user(db: AsyncDatabase, user: UserRegistration):
    if await db.user_auth.find_one(
        {"$or": [{"username": user.username}, {"email": user.email}]}
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username or email already exist",
        )

    # Generate salt and hash the password
    salt = generate_salt()
    user.password = hash_password(user.password, salt)

    raw_user_data: Dict[str, Any] = user.model_dump()
    raw_user_data["hashing_salt"] = salt

    # Create the user data using your UserAuth Pydantic model
    user_data = UserAuth.model_validate(raw_user_data)

    print(user_data.model_dump())

    created = await db.user_auth.insert_one(user_data.model_dump(exclude={"id"}))

    profile_data = UserProfile(auth_id=created.inserted_id, full_name=user.full_name)
    await db.user_profile.insert_one(profile_data.model_dump(exclude={"id"}))

    return {"message": "User created successfully"}


async def get_full_user(db: AsyncDatabase, user_id: ObjectId) -> UserOut:
    pipeline: List[Dict[str, Any]] = [
        # Match the user_auth document by its _id (or another unique identifier)
        {"$match": {"_id": user_id}},
        # Lookup the profile document from the user_profile collection
        {
            "$lookup": {
                "from": "user_profile",
                "localField": "_id",  # _id from user_auth
                "foreignField": "auth_id",  # user_id in user_profile
                "as": "profile",
            }
        },
        # Unwind the profile array (if profile doesn't exist, preserve the original document)
        {"$unwind": {"path": "$profile", "preserveNullAndEmptyArrays": True}},
        # Merge the original user_auth document with the profile document
        {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$profile", "$$ROOT"]}}},
    ]

    cursor = db.user_auth.aggregate(pipeline=pipeline)
    user_response = await cursor.to_list(length=1)

    if not user_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return UserOut.model_validate(user_response[0])


async def update_user_profile(
    db: AsyncDatabase, data: UpdatebleUser, user_id: ObjectId
):
    cleaned_data = data.model_dump(exclude_none=True, exclude={"created_at"})

    if not cleaned_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update"
        )

    user_data = await db.user_profile.find_one_and_update(
        {"_id": ObjectId(user_id)},
        update={"$set": cleaned_data},
        return_document=ReturnDocument.AFTER,
    )

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User details not found"
        )

    return UserProfile(**user_data)


def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=3)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, key=settings.JWT_ACCESS_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, key=settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
