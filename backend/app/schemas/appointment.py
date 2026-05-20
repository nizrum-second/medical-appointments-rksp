from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AppointmentBase(BaseModel):
    doctor_id: int
    time_slot_id: int
    service_id: Optional[int] = None
    complaints: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    time_slot_id: int
    service_id: Optional[int] = None
    status: str
    complaints: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AppointmentDetailResponse(AppointmentResponse):
    doctor_name: str
    doctor_specialization: str
    doctor_cabinet: str
    time_start: datetime
    time_end: datetime
    service_name: Optional[str] = None
    patient_name: str
    patient_phone: str
