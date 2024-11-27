from fastapi import Depends, HTTPException, status, Request, Cookie

import jwt
from datetime import datetime
from typing import Union, Any, Annotated
from bson import ObjectId

from .models import User
from .schemas import UserOut
from .config import (
    JWT_REFRESH_SECRET_KEY,
    JWT_ACCESS_SECRET_KEY,
    ALGORITHM,
    user_collection,
)


async def get_user_from_refresh_token(request: Request) -> UserOut:
    try:
        token = request.cookies.get("refresh_t")
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])

        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_collection.find_one({"_id": ObjectId(payload["sub"])})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return UserOut(**user)


async def get_user_from_access_token(
    access_token: Annotated[str | None, Cookie(alias="access_t")]
) -> UserOut:
    try:
        payload = jwt.decode(
            access_token, JWT_ACCESS_SECRET_KEY, algorithms=[ALGORITHM]
        )

        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_collection.find_one({"_id": ObjectId(payload["sub"])})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return UserOut(**user)
