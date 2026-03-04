from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.models.users import UserRole

class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
