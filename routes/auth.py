from fastapi import APIRouter, HTTPException, Response, Request
from schemas.auth_schema import SignupRequest, LoginRequest
from services.auth_service import create_user, login_user, regenerate_tokens, logout

auth_router = APIRouter()


@auth_router.post("/signup")
async def signup(data: SignupRequest):
    print("Sign up requested")
    return await create_user(data)


@auth_router.post("/login")
async def login(data: LoginRequest, response: Response):
    print("Log in requested")

    tokens = await login_user(data)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="none",
        secure=True,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="none",
        secure=True,
    )

    return {"message": "Login successful"}


@auth_router.get("/refresh-token")
async def refresh_token(request: Request, response: Response):
    print("refresh token requested")
    tokens = await regenerate_tokens(request)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="none",
        secure=True,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="none",
        secure=True,
    )

    return {"message": "Token refreshed"}


@auth_router.post("/logout")
async def logout_user(request: Request, response: Response):
    print("Logout requested")

    await logout(request)

    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="none",
        secure=True,
    )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="none",
        secure=True,
    )

    return {"message": "Logged Out Successfully"}
