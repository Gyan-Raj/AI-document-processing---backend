from fastapi import Request, HTTPException
from utils.helper import validate_token


# This is a dependency, not ASGI middleware — no call_next
async def auth_required(request: Request):
    print(request.cookies, "cookies")
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="No token found")

    payload = validate_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    request.state.user_email = payload["user_email"]
    request.state.user_id = payload["user_id"]
