import os

UPLOAD_DIR = "user_files/uploads"
RISK_SUMMARY_DIR = "user_files/risk_summaries"
MODEL_TO_BE_USED = os.getenv("MODEL_TO_BE_USED")
ACCESS_TOKEN_COOKIE_OPTIONS = {
    "key": "access_token",
    "httponly": True,
    "samesite": "none",
    "secure": True,
}
REFRESH_TOKEN_COOKIE_OPTIONS = {
    "key": "refresh_token",
    "httponly": True,
    "samesite": "none",
    "secure": True,
}
