from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints, field_validator
import re

strippedStr = Annotated[str, StringConstraints(strip_whitespace=True)]

usernameStr = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)]

class Name(BaseModel):
    fname: strippedStr
    sname: strippedStr

class UserCreate(BaseModel):
    username: usernameStr = Field(
        description="3-32 characters, letters, numbers, hyphens and underscores only"
    )
    password: str = Field(
        description="8-128 characters. Must include uppercase, lowercase, a number and special characters. No spaces."
    )
    name: Name

    @field_validator('username')
    @classmethod
    def validate_username(cls, value):
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if len(value) > 32:
            raise ValueError("Username cannot be longer than 32 characters.")
        
        if not re.match(r'^[a-z0-9_-]+$', value):
            raise ValueError("Username may only contain letters, numbers, hyphens and underscores.")

        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if len(value) > 128:
            raise ValueError("Password cannot be longer than 128 characters.")
        if re.search(" ", value):
            raise ValueError("Password must not contain spaces.")

        #Composition rules over length, design choice
        if not re.search(r'[0-9]', value):
            raise ValueError("Password must contain at least 1 number.")
        if not re.search(r'[A-Z]', value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r'[^\w\s]', value):
            raise ValueError("Password must contain at least one special character.")

        
        return value

class UserResponse(BaseModel):
    id: str = Field()
    username: str = Field()
    name: Name