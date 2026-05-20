from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Time,
    ForeignKey,
    Enum,
)
from sqlalchemy.sql import func
from ..database import Base


class ScheduleTemplate(Base):
    __tablename__ = "schedule_templates"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    day_of_week = Column(Integer)  # 0-6, Monday to Sunday
    start_time = Column(Time)
    end_time = Column(Time)
    is_working = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        Enum("free", "booked", "blocked", "completed", name="slot_status"),
        default="free",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
