from pydantic import BaseModel, EmailStr

class User(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: EmailStr
    password: str

class UserCreate(User):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str
