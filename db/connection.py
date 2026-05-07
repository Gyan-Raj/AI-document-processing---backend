from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy import text

# from config.env_constants import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

POSTGRESQL_NEON_URL = os.getenv("POSTGRESQL_NEON_URL")

# ⚠️ Important: URL encoding for password
from urllib.parse import quote_plus

# encoded_password = quote_plus(DB_PASSWORD)
#
# DATABASE_URL = (
#     f"mysql+aiomysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# )
DATABASE_URL = POSTGRESQL_NEON_URL.replace("postgresql://", "postgresql+asyncpg://")
DATABASE_URL = DATABASE_URL.replace("sslmode=require", "ssl=require")
DATABASE_URL = DATABASE_URL.split("&channel_binding")[0]
print("DATABASE_URL:", DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def check_db_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connected successfully")
    except Exception as e:
        print("❌ Database connection failed:", e)
