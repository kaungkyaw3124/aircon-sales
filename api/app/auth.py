import math
from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.clock import now
from app.config import settings
from app.db import get_db
from app.models import LoginFailure, User

router = APIRouter()

INVALID_CREDENTIALS = HTTPException(401, {"code": "invalid_credentials", "message": "Wrong username or password."})
UNAUTHORIZED = HTTPException(401, {"code": "unauthorized", "message": "Missing or invalid token."},
                             headers={"WWW-Authenticate": "Bearer"})
RATE_WINDOW = timedelta(minutes=15)
USERNAME_LIMIT, IP_LIMIT = 5, 20
TRUSTED_PROXIES = {ip.strip() for ip in settings.trusted_proxies.split(",") if ip.strip()}
# checked when the username is unknown, so a wrong username takes as long as a wrong password
DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt())


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


def make_token(user: User, issued_at: datetime, minutes: int = settings.jwt_expire_minutes) -> str:
    claims = {"sub": str(user.id), "role": user.role, "exp": issued_at + timedelta(minutes=minutes)}
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256")


def client_ip(request: Request) -> str:
    host = request.client.host if request.client else ""
    forwarded = request.headers.get("x-forwarded-for")
    # the last entry is the one our proxy added; earlier ones are whatever the client sent
    return forwarded.split(",")[-1].strip() if host in TRUSTED_PROXIES and forwarded else host


def retry_after(db: Session, at: datetime, username: str, ip: str) -> int | None:
    """Seconds until the oldest of the last `limit` failures leaves the window, if a limit is reached."""
    ends = []
    for column, value, limit in ((LoginFailure.username, username, USERNAME_LIMIT), (LoginFailure.ip, ip, IP_LIMIT)):
        nth = db.scalar(select(LoginFailure.failed_at)
                        .where(column == value, LoginFailure.failed_at > at - RATE_WINDOW)
                        .order_by(LoginFailure.failed_at.desc()).offset(limit - 1).limit(1))
        if nth:
            ends.append(nth + RATE_WINDOW)
    return max(1, math.ceil((max(ends) - at).total_seconds())) if ends else None


@router.post("/auth/login")
def login(body: LoginRequest, request: Request, db: Annotated[Session, Depends(get_db)],
          at: Annotated[datetime, Depends(now)]):
    # Postgres text can't hold NUL, and a huge key would overflow the btree index (500)
    key = body.username.replace("\x00", "")[:200]
    ip = client_ip(request)
    if (seconds := retry_after(db, at, key, ip)) is not None:
        raise HTTPException(429, {"code": "rate_limited", "message": "Too many login attempts. Try again in 15 minutes."},
                            headers={"Retry-After": str(seconds)})
    # no user has a NUL in the name (see above); querying it would raise
    user = None if "\x00" in body.username else db.scalars(select(User).where(User.username == body.username)).first()
    password = body.password.encode()
    # bcrypt rejects > 72 bytes, so no stored hash can match such a password: plain wrong credentials, not a 500
    ok = len(password) <= 72 and bcrypt.checkpw(password, user.password_hash.encode() if user else DUMMY_HASH)
    if not (user and ok and user.active):
        db.execute(delete(LoginFailure).where(LoginFailure.failed_at <= at - RATE_WINDOW))
        db.add(LoginFailure(username=key, ip=ip, failed_at=at))
        db.commit()
        raise INVALID_CREDENTIALS
    db.execute(delete(LoginFailure).where(LoginFailure.username == key))
    db.commit()
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
