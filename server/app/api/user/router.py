from typing import Annotated
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.schemas import UserRegistration, UserOut, UpdatebleUser, UserAuthOut
from app.utils import verify_password

from app.deps import get_user_from_refresh_token, get_user_from_access_token_http
from app.core.db import get_async_database, AsyncDatabase
from app.core.config import settings

from .services import (
    create_user,
    update_user_profile,
    create_access_token,
    create_refresh_token,
    get_full_user,
)

router = APIRouter()


@router.post("/register")
async def user_register(
    user: UserRegistration = Body(...), db: AsyncDatabase = Depends(get_async_database)
):
    try:
        created = await create_user(db, user)
        return JSONResponse(content=created, status_code=status.HTTP_201_CREATED)

    except HTTPException as e:
        raise e


@router.post("/get-token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncDatabase = Depends(get_async_database),
):
    user = await db.user_auth.find_one({"username": form_data.username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User name not found"
        )

    if not verify_password(user["password"], form_data.password, user["hashing_salt"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expire_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user["_id"])}, expire_delta=refresh_token_expires
    )

    a_expires = datetime.now(timezone.utc) + access_token_expires
    r_expires = datetime.now(timezone.utc) + refresh_token_expires

    response = JSONResponse(content=None)
    response.set_cookie(
        key="access_t",
        value=access_token,
        httponly=False,
        expires=a_expires,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_t",
        value=refresh_token,
        httponly=True,
        expires=r_expires,
        samesite="lax",
    )

    return response


@router.get("/me")
async def get_me(
    user: UserOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    user_data = await get_full_user(db=db, user_id=user.id)
    return user_data


@router.post("/refresh-token")
async def get_refresh_token(user: UserAuthOut = Depends(get_user_from_refresh_token)):
    print(user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expire_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expire_delta=refresh_token_expires
    )

    a_expires = datetime.now(timezone.utc) + access_token_expires
    r_expires = datetime.now(timezone.utc) + refresh_token_expires

    response = JSONResponse(content=None)
    response.set_cookie(
        key="access_t",
        value=access_token,
        httponly=False,
        expires=a_expires,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_t",
        value=refresh_token,
        httponly=True,
        expires=r_expires,
        samesite="lax",
    )

    return response


@router.patch("/update")
async def update_user_data(
    data: Annotated[UpdatebleUser, Body()],
    user: UserAuthOut = Depends(get_user_from_access_token_http),
    db: AsyncDatabase = Depends(get_async_database),
):
    print(data)
    return await update_user_profile(db, data, user.id)
