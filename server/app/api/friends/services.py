from bson import ObjectId
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from app.core.schemas import Friends, Friends_Status, UserOut
from app.core.db import AsyncDatabase
from app.api.user.services import get_full_user


async def are_friends(
    db: AsyncDatabase, user_id: ObjectId, friend_id: ObjectId
) -> bool:
    friend = await db.friends.find_one({"user_id": user_id, "friend_id": friend_id})
    print(f"{friend=}")
    if not friend:
        print("note friends")
        return False
    print("friends")
    return True


async def create_friends(db: AsyncDatabase, user1_id: ObjectId, user2_id: ObjectId):
    friend_for_1 = Friends(user_id=user1_id, friend_id=user2_id)
    friend_for_2 = Friends(user_id=user2_id, friend_id=user1_id)

    if await are_friends(db, user1_id, user2_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are already friends"
        )

    friend1 = await db.friends.insert_one(friend_for_1.model_dump(exclude={"id"}))
    await db.friends.insert_one(friend_for_2.model_dump(exclude={"id"}))

    return str(friend1.inserted_id)


async def get_friends_list(
    db: AsyncDatabase, id: ObjectId, updated_after: Optional[datetime] = None
):
    # Pipeline to get users from user_id in friends collection
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"user_id": id}},
        {"$addFields": {"friendsObjectId": {"$toObjectId": "$friend_id"}}},
        {
            "$lookup": {
                "from": "user_profile",
                "localField": "friendsObjectId",
                "foreignField": "auth_id",
                "as": "profile",
            }
        },
        {"$unwind": "$profile"},
        {
            "$lookup": {
                "from": "user_auth",
                "localField": "friendsObjectId",
                "foreignField": "_id",
                "as": "auth",
            }
        },
        {"$unwind": "$auth"},
        {"$addFields": {"mergedData": {"$mergeObjects": ["$profile", "$auth"]}}},
        {"$sort": {"profile.firstname": 1}},
        {"$replaceRoot": {"newRoot": "$mergedData"}},
    ]

    if updated_after:
        pipeline[0]["$match"]["update_at"] = {"$gt": updated_after}

    try:
        cursor = db.friends.aggregate(pipeline)
        friends = await cursor.to_list(length=None)

        return friends

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error fetching users list",
        )


async def reject_friend_request(db: AsyncDatabase, id: ObjectId, receiver_id: ObjectId):
    friend_request = await db.friend_request.find_one_and_update(
        {"_id": id, "receiver_id": receiver_id, "status": Friends_Status.pending.value},
        {"$set": {"status": Friends_Status.rejected.value}},
    )

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found."
        )

    return {"message": "Friend request rejected successfully."}


async def _get_friend(
    db: AsyncDatabase, user_id: ObjectId, friend_id: ObjectId
) -> UserOut:
    """
    Thid function checks if the users are already friend and return the friends details.

    Input:
        db -> database instance.
        user_id -> Id of the user requesting.
        friend_id -> Id of the friend whose data is being requested.
    """
    if not await db.friends.find_one({"user_id": user_id, "friend_id": friend_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You don't have friend with friend_id '{friend_id}'",
        )

    return await get_full_user(db=db, user_id=friend_id)
