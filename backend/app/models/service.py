from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Numeric,
    Table,
    ForeignKey,
    Text
)
from sqlalchemy.sql import func
from ..database import Base

# Association table for many-to-many relationship between doctors and services
doctor_services = Table(
    "doctor_services",
    Base.metadata,
    Column("doctor_id", Integer, ForeignKey("doctors.id")),
    Column("service_id", Integer, ForeignKey("services.id")),
)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    duration = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
