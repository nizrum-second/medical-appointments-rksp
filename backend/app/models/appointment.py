from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.sql import func
from ..database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    status = Column(
        Enum(
            "pending",
            "confirmed",
            "completed",
            "cancelled",
            name="appointment_status",
        ),
        default="confirmed",
    )
    complaints = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
