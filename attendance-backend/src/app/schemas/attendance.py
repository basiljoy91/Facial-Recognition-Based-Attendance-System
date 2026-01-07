from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class AttendanceDecision(BaseModel):
    status: str
    confidence: float
    liveness_score: Optional[int]
    user_id: int
    timestamp: datetime


class AttendanceLogOut(BaseModel):
    id: int
    user_id: int
    date: date
    type: str
    timestamp: datetime
    confidence: int
    liveness_score: Optional[int]
    manual_override: bool

    class Config:
        from_attributes = True

