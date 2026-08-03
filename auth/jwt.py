from fastapi import HTTPException
from schemas import TokenPayload
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("'SECRET_KEY' environment variable is missing.")
ALGORITHM = "HS256"

def create_access_token(user_id):
    now = datetime.now(timezone.utc)
    expiry_time = now + timedelta(minutes=15)

    token_payload = TokenPayload(
        sub=str(user_id),
        iat=int(now.timestamp()),
        exp=int(expiry_time.timestamp())
        )
    
    encoded_jwt = jwt.encode(payload=token_payload.model_dump() , key=SECRET_KEY , algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token):
    try:
        decoded_jwt = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt 
    except jwt.ExpiredSignatureError:
        raise HTTPException( 401, "Token has expired." )
    except jwt.InvalidTokenError:
        raise HTTPException( 401, "Token is invalid." )