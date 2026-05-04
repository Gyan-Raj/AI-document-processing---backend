import jwt
from datetime import datetime, timedelta
import os
import bcrypt
import hashlib
from fastapi import HTTPException
import pdfplumber

ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET_KEY")
REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET_KEY")
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


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF, page by page."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # some pages are images — skip them
                full_text += page_text + "\n"
    return full_text
