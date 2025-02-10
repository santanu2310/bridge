from bson import ObjectId
from typing import Annotated
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import ReturnDocument

from ..config import (
    user_collection,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

from ..schemas import UserRegistration, UserOut, UpdatebleUser
from ..utils import (
    create_user,
    create_access_token,
    verify_password,
    create_refresh_token,
)
from ..deps import get_user_from_refresh_token, get_user_from_access_token

router = APIRouter()


@router.post("/register")
async def user_register(user: UserRegistration = Body(...)):
    try:
        created = await create_user(user)
        return JSONResponse(content=created, status_code=status.HTTP_201_CREATED)

    except HTTPException as e:
        raise e


@router.post("/get-token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await user_collection.find_one({"username": form_data.username})

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

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"])}, expire_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
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
async def get_me(user: UserOut = Depends(get_user_from_access_token)):
    return user


@router.post("/refresh-token")
async def get_refresh_token(user: UserOut = Depends(get_user_from_refresh_token)):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expire_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
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
    user: UserOut = Depends(get_user_from_access_token),
):
    cleaned_data = data.dict(exclude_none=True)

    if not cleaned_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update"
        )

    try:
        user_data = await user_collection.find_one_and_update(
            {"_id": ObjectId(user.id)},
            update={"$set": cleaned_data},
            return_document=ReturnDocument.AFTER,
        )

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User details not found"
            )

        return UserOut(**user_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
