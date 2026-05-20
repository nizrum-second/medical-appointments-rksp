from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DoctorBase(BaseModel):
    specialization: str
    cabinet_number: str
    appointment_duration: int = 30


class DoctorCreate(DoctorBase):
    user_id: int


class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorWithUserResponse(DoctorResponse):
    full_name: str
    email: str
    phone: Optional[str] = None
