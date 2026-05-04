# services/user_service.py
from db.connection import AsyncSessionLocal
from dao.user_dao import get_user_by_id
from fastapi import HTTPException


async def get_me(request):
    userId = request.state.user_id  # ✅ already validated by middleware, just read it

    async with AsyncSessionLocal() as session:
        userInfo = await get_user_by_id(session, userId)

        if not userInfo:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_name": userInfo["user_name"],
            "user_email": userInfo["user_email"],
            "userId": userInfo["id"],
        }
