import jwt
from datetime import datetime
from typing import Annotated
from bson import ObjectId
from fastapi import HTTPException, status, Cookie, Depends
from app.core.schemas import UserAuthOut
from app.core.config import settings
from app.core.db import (
    AsyncDatabase,
    get_async_database,
    get_async_database_from_socket,
)


async def get_user_from_refresh_token(
    refresh_token: Annotated[str, Cookie(alias="refresh_t")],
    db: AsyncDatabase = Depends(get_async_database),
) -> UserAuthOut:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.user_auth.find_one({"_id": ObjectId(payload["sub"])})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return UserAuthOut(**user)


async def _get_user_from_access_token(
    access_token: str,
    db: AsyncDatabase,
) -> UserAuthOut:
    try:
        payload = jwt.decode(
            access_token,
            settings.JWT_ACCESS_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.user_auth.find_one({"_id": ObjectId(payload["sub"])})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return UserAuthOut(**user)


async def get_user_from_access_token_http(
    access_token: Annotated[str, Cookie(alias="access_t")],
    db: AsyncDatabase = Depends(get_async_database),
) -> UserAuthOut:
    return await _get_user_from_access_token(access_token=access_token, db=db)


async def get_user_from_access_token_ws(
    access_token: Annotated[str, Cookie(alias="access_t")],
    db: AsyncDatabase = Depends(get_async_database_from_socket),
) -> UserAuthOut:
    return await _get_user_from_access_token(access_token=access_token, db=db)


__all__ = [
    "get_user_from_refresh_token",
    "get_user_from_access_token_http",
    "get_user_from_access_token_ws",
]
