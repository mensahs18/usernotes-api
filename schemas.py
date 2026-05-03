from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    fname: str
    sname: str