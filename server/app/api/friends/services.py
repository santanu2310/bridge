from bson import ObjectId
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from app.core.schemas import Friends
from app.core.db import AsyncDatabase


async def are_friends(
    db: AsyncDatabase, user_id: ObjectId, friend_id: ObjectId
) -> bool:
    if await db.friends.find_one({"user_id": user_id, "friends_id": friend_id}):
        return True
    return False


async def create_friends(db: AsyncDatabase, user1_id: ObjectId, user2_id: ObjectId):
    friend_for_1 = Friends(user_id=user1_id, friends_id=user2_id)
    friend_for_2 = Friends(user_id=user2_id, friends_id=user1_id)

    if await are_friends(db, user1_id, user2_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are already friends"
        )

    friend1 = await db.friends.insert_one(friend_for_1.model_dump(exclude={"id"}))
    await db.friends.insert_one(friend_for_2.model_dump(exclude={"id"}))

    return friend1


async def get_friends_list(
    db: AsyncDatabase, id: ObjectId, updated_after: Optional[datetime] = None
):
    # Pipeline to get users from user_id in friends collection
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"user_id": id}},
        {"$addFields": {"friendsObjectId": {"$toObjectId": "$friends_id"}}},
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
        pipeline[0]["$match"]["last_message_date"] = {"$gt": updated_after}

    try:
        cursor = db.friends.aggregate(pipeline)
        friends = await cursor.to_list(length=None)

        return friends

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error fetching users list",
        )
