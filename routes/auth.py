from fastapi import APIRouter, HTTPException, Response, Request
from schemas.auth_schema import SignupRequest, LoginRequest
from services.auth_service import create_user, login_user, regenerate_tokens, logout

auth_router = APIRouter()
from config.constants import ACCESS_TOKEN_COOKIE_OPTIONS, REFRESH_TOKEN_COOKIE_OPTIONS


@auth_router.post("/signup")
async def signup(data: SignupRequest):
    print("Sign up requested")
    user_email = data.user_email.strip()
    user_name = data.user_name.strip()
    user_password = data.user_password.strip()
    if not user_email or not user_name or not user_password:
        raise HTTPException(
            status_code=400,
            detail="Please fill in required fields",
        )
    return await create_user(data)


@auth_router.post("/login")
async def login(data: LoginRequest, response: Response):
    print("Log in requested")
    user_email = data.user_email.strip()
    user_password = data.user_password.strip()

    if not user_email or not user_password:
        raise HTTPException(
            status_code=400,
            detail="Please fill in required fields",
        )

    tokens = await login_user(data)

    response.set_cookie(value=tokens["access_token"], **ACCESS_TOKEN_COOKIE_OPTIONS)

    response.set_cookie(value=tokens["refresh_token"], **REFRESH_TOKEN_COOKIE_OPTIONS)

    return {"message": "Login successful"}


@auth_router.get("/refresh-token")
async def refresh_token(request: Request, response: Response):
    print("refresh token requested")
    tokens = await regenerate_tokens(request)

    response.set_cookie(value=tokens["access_token"], **ACCESS_TOKEN_COOKIE_OPTIONS)

    response.set_cookie(value=tokens["refresh_token"], **REFRESH_TOKEN_COOKIE_OPTIONS)

    return {"message": "Token refreshed"}


@auth_router.post("/logout")
async def logout_user(request: Request, response: Response):
    print("Logout requested")

    await logout(request)

    response.delete_cookie(**ACCESS_TOKEN_COOKIE_OPTIONS)

    response.delete_cookie(**REFRESH_TOKEN_COOKIE_OPTIONS)

    return {"message": "Logged Out Successfully"}
