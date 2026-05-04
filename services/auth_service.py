from db.connection import AsyncSessionLocal
from dao.user_dao import (
    get_user_by_email,
    get_user_by_id,
    create_user_db,
    update_user_refresh_token,
)
from utils.helper import (
    bcrypt_entity,
    verify_bcrypted_entity,
    hash_refresh_token,
    verify_hash_refresh_token,
    create_token,
    REFRESH_TOKEN,
    validate_token,
)
from fastapi import HTTPException


async def create_user(data):
    async with AsyncSessionLocal() as session:

        existing_user = await get_user_by_email(session, data.user_email)

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = bcrypt_entity(data.user_password)

        await create_user_db(session, data, hashed_password)

        await session.commit()

        return {"message": "User created successfully"}


async def login_user(data):
    async with AsyncSessionLocal() as session:

        existing_user = await get_user_by_email(session, data.user_email)

        if not existing_user:
            raise HTTPException(status_code=400, detail="User not found")

        hashed_password = existing_user["user_password"]  # if using raw SQL

        is_correct_password = verify_bcrypted_entity(
            data.user_password, hashed_password
        )

        if not is_correct_password:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # 🔐 Generate tokens
        access_token = create_token(
            {"user_email": existing_user["user_email"], "user_id": existing_user["id"]}
        )
        refresh_token = create_token(
            {"user_email": existing_user["user_email"], "user_id": existing_user["id"]},
            REFRESH_TOKEN,
        )
        hashed_refresh_token = hash_refresh_token(refresh_token)
        await update_user_refresh_token(
            session, existing_user["id"], hashed_refresh_token
        )
        await session.commit()

        return {"access_token": access_token, "refresh_token": refresh_token}


async def regenerate_tokens(request):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No token found")

    decrypt = validate_token(refresh_token, REFRESH_TOKEN)

    if not decrypt:
        raise HTTPException(status_code=401, detail="Invalid token")

    userId = decrypt["user_id"]

    async with AsyncSessionLocal() as session:
        userInfo = await get_user_by_id(session, userId)

        if not userInfo:
            raise HTTPException(status_code=404, detail="User not found")

        is_valid_refresh_token = verify_hash_refresh_token(
            refresh_token, userInfo["refresh_token"]
        )

        if not is_valid_refresh_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        # 🔐 Generate new tokens
        new_access_token = create_token(
            {"user_email": userInfo["user_email"], "user_id": userInfo["id"]}
        )
        new_refresh_token = create_token(
            {"user_email": userInfo["user_email"], "user_id": userInfo["id"]},
            REFRESH_TOKEN,
        )

        # 🔁 Rotate refresh token
        new_hash_refresh_token = hash_refresh_token(new_refresh_token)

        await update_user_refresh_token(session, userInfo["id"], new_hash_refresh_token)

        await session.commit()

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}


async def logout(request):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        print("No token found")
        raise HTTPException(status_code=401, detail="No token found")

    decrypt = validate_token(refresh_token, REFRESH_TOKEN)

    if not decrypt:
        print("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    userId = decrypt["user_id"]

    async with AsyncSessionLocal() as session:
        userInfo = await get_user_by_id(session, userId)
        print(userInfo, "userInfo")

        if not userInfo:
            print("User not found")
            raise HTTPException(status_code=404, detail="User not found")

        is_valid_refresh_token = verify_hash_refresh_token(
            refresh_token, userInfo["refresh_token"]
        )

        print(is_valid_refresh_token, "is_valid_refresh_token")
        if not is_valid_refresh_token:
            print("Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")

        # 🔥 invalidate refresh token
        await update_user_refresh_token(session, userInfo["id"], None)

        await session.commit()
