"""Utilities for creating and decoding JWT access tokens.

This module keeps the code simple and readable for beginners.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

import jwt
from fastapi import HTTPException

from app.src.config import security_settings


def create_access_token(
    data: dict,
    expiry: timedelta = timedelta(hours=1),
):
    token = jwt.encode(
        payload={
            **data,
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + expiry,
        },
        key=security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )

    return token


def decode_token(token: str) -> Optional[dict]:
    """Decode a JWT access token and return its payload.

    This function is forgiving of common mistakes beginners make:
    - Accepts `Authorization` header value like `Bearer <token>`.
    - Removes surrounding quotes and internal whitespace/newlines.
    - Returns `None` on error so callers can respond with 401.
    """

    # If token is not a string, bail out early
    if not isinstance(token, str):
        return None

    # Trim spaces and remove a leading "Bearer " if present
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]

    # Remove surrounding quotes like '"..."' or "'...'"
    if (token.startswith('"') and token.endswith('"')) or (
        token.startswith("'") and token.endswith("'")
    ):
        token = token[1:-1]

    # Remove internal whitespace/newlines (useful when tokens wrap)
    token = re.sub(r"\s+", "", token)

    # If the header contains extra text (commas, repeated 'Bearer', etc.),
    # extract the first substring that looks like a JWT: three base64url
    # segments separated by dots. This makes the function tolerant to
    # pasted/wrapped tokens or clients that append extra values.
    jwt_match = re.search(r"([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)", token)
    if jwt_match:
        token = jwt_match.group(1)

    try:
        payload = jwt.decode(
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token Expired")
    except jwt.PyJWTError:
        return None
