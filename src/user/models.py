import uuid
from enum import Enum
from database import Base
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String

str_uuid = lambda: str(uuid.uuid4())


class UserRoles(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True,index=True, default=str_uuid)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)
    password = Column(String, nullable=False)
    role = Column(String, default=UserRoles.USER.value)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True, default=None)


