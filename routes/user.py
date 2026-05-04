# ✅ Clean version
from fastapi import APIRouter, Request
from services.user_service import get_me

user_router = APIRouter()


@user_router.get("/get-me")
async def get_me_route(request: Request):
    print("get me route requested")
    userInfo = await get_me(request)
    return {"message": "User fetched successfully", "data": userInfo}
