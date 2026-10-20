from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clock import now
from app.config import settings
from app.db import get_db
from app.models import User

router = APIRouter()

INVALID_CREDENTIALS = HTTPException(401, {"code": "invalid_credentials", "message": "Wrong username or password."})
UNAUTHORIZED = HTTPException(401, {"code": "unauthorized", "message": "Missing or invalid token."},
                             headers={"WWW-Authenticate": "Bearer"})
# checked when the username is unknown, so a wrong username takes as long as a wrong password
DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt())


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


def make_token(user: User, issued_at: datetime, minutes: int = settings.jwt_expire_minutes) -> str:
    claims = {"sub": str(user.id), "role": user.role, "exp": issued_at + timedelta(minutes=minutes)}
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")


@router.post("/auth/login")
def login(body: LoginRequest, db: Annotated[Session, Depends(get_db)], at: Annotated[datetime, Depends(now)]):
    user = db.scalars(select(User).where(User.username == body.username)).first()
    ok = bcrypt.checkpw(body.password.encode(), user.password_hash.encode() if user else DUMMY_HASH)
    if not (user and ok and user.active):
        raise INVALID_CREDENTIALS
    return {
        "access_token": make_token(user, at),
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60,
        "user": {"id": user.id, "username": user.username, "full_name": user.full_name, "role": user.role},
    }


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if creds is None:
        raise UNAUTHORIZED
    try:
        claims = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=["HS256"],
                            options={"require": ["sub", "exp"]})
        user = db.get(User, int(claims["sub"]))
    except (jwt.PyJWTError, ValueError):
        raise UNAUTHORIZED
    if user is None or not user.active:
        raise UNAUTHORIZED
    return user
