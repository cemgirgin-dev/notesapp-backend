import os
from datetime import timedelta

# Basic application configuration with environment variable overrides for sensitive settings.
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-to-a-secure-value")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./notes.db")


def access_token_expiry() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
