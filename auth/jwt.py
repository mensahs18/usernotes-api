import os
from datetime import UTC, datetime, timedelta
from uuid import UUID

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


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(UTC)
    expiry_time = now + timedelta(minutes=15)

    token_payload = TokenPayload(
        sub=user_id, iat=int(now.timestamp()), exp=int(expiry_time.timestamp())
    )

    encoded_jwt = jwt.encode(
        payload=token_payload.model_dump(mode="json"),
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def verify_access_token(token: str) -> TokenPayload:
    try:
        decoded_jwt = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=UUID(decoded_jwt["sub"]), exp=decoded_jwt["exp"], iat=decoded_jwt["iat"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired.") from None
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token is invalid.") from None
