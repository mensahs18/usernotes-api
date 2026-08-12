from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
