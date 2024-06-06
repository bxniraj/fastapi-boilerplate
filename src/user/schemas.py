from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str

class UserCreate(User):
    pass

class UserUpdate(User):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UpdatePassword(BaseModel):
    email: str
    old_password: str
    new_password: str