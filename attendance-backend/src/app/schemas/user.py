from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    full_name: str
    roll_no: Optional[str] = None
    password: str
    role: str = "STUDENT"


class UserOut(BaseModel):
    id: int
    external_id: str
    full_name: str
    roll_no: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

