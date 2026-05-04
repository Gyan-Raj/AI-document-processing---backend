from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    user_name: str
    user_email: str
    user_password: str


class LoginRequest(BaseModel):
    user_email: str
    user_password: str
