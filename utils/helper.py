import jwt
from datetime import datetime, timedelta
import bcrypt
import hashlib
from fastapi import HTTPException
from config.env_constants import ACCESS_SECRET, REFRESH_SECRET

ALGORITHM = "HS256"
ACCESS_TOKEN = "ACCESS_TOKEN"
REFRESH_TOKEN = "REFRESH_TOKEN"


def create_token(data: dict, token_type: str = "ACCESS_TOKEN"):
    payload = data.copy()

    if token_type == "REFRESH_TOKEN":
        payload["exp"] = datetime.utcnow() + timedelta(days=10)
        secret = REFRESH_SECRET
    else:
        payload["exp"] = datetime.utcnow() + timedelta(days=1)
        secret = ACCESS_SECRET

    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def validate_token(token: str, token_type: str = "ACCESS_TOKEN"):
    print("validating token")
    try:
        if token_type == "REFRESH_TOKEN":
            payload = jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])
        else:
            payload = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def hash_refresh_token(entity: str):
    return hashlib.sha256(entity.encode()).hexdigest()


def verify_hash_refresh_token(entity: str, hashed_entity: str):
    return hashlib.sha256(entity.encode()).hexdigest() == hashed_entity


def bcrypt_entity(entity: str) -> str:
    return bcrypt.hashpw(entity.encode(), bcrypt.gensalt()).decode()


def verify_bcrypted_entity(entity: str, hashed_entity: str) -> bool:
    return bcrypt.checkpw(entity.encode(), hashed_entity.encode())
