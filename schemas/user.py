from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints, field_validator
from argon2 import PasswordHasher
import re

strippedStr = Annotated[str, StringConstraints(strip_whitespace=True)]

class Name(BaseModel):
    fname: strippedStr
    sname: strippedStr

class UserCreate(BaseModel):
    username: strippedStr = Field(min_length=3, frozen=True)
    password: str = Field(min_length=8, max_length=128)
    name: Name

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if not re.search(r'[0-9]', value):
            raise ValueError("Password must contain at least 1 number.")
        if not re.search(r'[A-Z]', value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r'[ !"#$%&\'()*+,-./:;<=>?@\[\]^_`{|}~]', value):
            raise ValueError("Password must contain at least one special character.")
        if re.search(" ", value):
            raise ValueError("Password must not contains spaces.")
        
        return value

class UserResponse(BaseModel):
    id: str = Field()
    username: str = Field()
    name: Name