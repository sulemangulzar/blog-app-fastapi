from datetime import datetime, timedelta, timezone

import jwt
from app.src.config import security_settings


def create_access_token(
    data: dict,
    expiry: timedelta = timedelta(days=1),
):
    token = jwt.encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + expiry,
        },
        key=security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )

    return token


def decode_token(token: str):
    payload = jwt.decode(
        jwt=token,
        key=security_settings.JWT_SECRET,
        algorithms=[security_settings.JWT_ALGORITHM],
    )

    return payload
