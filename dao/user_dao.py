from sqlalchemy import text


async def get_user_by_email(session, email):
    query = text("SELECT * FROM users WHERE user_email = :email")
    result = await session.execute(query, {"email": email})
    return result.mappings().first()


async def get_user_by_id(session, user_id):
    query = text("SELECT * FROM users WHERE id = :id")
    result = await session.execute(query, {"id": user_id})
    return result.mappings().first()


async def create_user_db(session, data, hashed_password):
    query = text("""
        INSERT INTO users (user_name, user_email, user_password)
        VALUES (:name, :email, :password)
    """)

    await session.execute(
        query,
        {"name": data.user_name, "email": data.user_email, "password": hashed_password},
    )


async def update_user_refresh_token(session, user_id, token):
    query = text("""
        UPDATE users
        SET refresh_token = :token
        WHERE id = :id
    """)
    await session.execute(query, {"token": token, "id": user_id})
