import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException

from schemas import TokenPayload

load_dotenv()
JWT_KEY = os.getenv("SECRET_KEY")
if not JWT_KEY:
    raise RuntimeError("'SECRET_KEY' environment variable is missing.")

SECRET_KEY: str = JWT_KEY
ALGORITHM = "HS256"

def create_access_token(user_id: str) -> str:
    now = datetime.now(UTC)
    expiry_time = now + timedelta(minutes=15)

    token_payload = TokenPayload(
        sub=user_id,
        iat=int(now.timestamp()),
        exp=int(expiry_time.timestamp())
        )

    encoded_jwt = jwt.encode(payload=token_payload.model_dump() , key=SECRET_KEY , algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str) -> dict[str, Any]:
    try:
        decoded_jwt = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        raise HTTPException( 401, "Token has expired." ) from None
    except jwt.InvalidTokenError:
        raise HTTPException( 401, "Token is invalid." ) from None
