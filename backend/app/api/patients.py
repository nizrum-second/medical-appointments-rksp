from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date, timedelta
from typing import List, Optional

from ..dependencies import get_db, get_current_patient
from ..models.user import User
from ..models.doctor import Doctor
from ..models.schedule import TimeSlot
from ..models.appointment import Appointment
from ..models.service import Service, doctor_services
from ..schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentDetailResponse,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/doctors")
def get_doctors(
    specialization: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    query = db.query(Doctor).filter(Doctor.is_active == True)
    if specialization:
        query = query.filter(
            Doctor.specialization.ilike(f"%{specialization}%")
        )

    doctors = query.all()
    result = []
    for doctor in doctors:
        user = db.query(User).filter(User.id == doctor.user_id).first()
        result.append(
            {
                "id": doctor.id,
                "full_name": user.full_name if user else "",
                "specialization": doctor.specialization,
                "cabinet_number": doctor.cabinet_number,
                "appointment_duration": doctor.appointment_duration,
            }
        )
    return result


@router.get("/doctors/{doctor_id}/slots")
def get_free_slots(
    doctor_id: int,
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    start_datetime = datetime.combine(date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    slots = (
        db.query(TimeSlot)
        .filter(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.start_time >= start_datetime,
            TimeSlot.start_time < end_datetime,
            TimeSlot.status == "free",
        )
        .order_by(TimeSlot.start_time)
        .all()
    )

    return slots


@router.post("/appointments", response_model=AppointmentResponse)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    slot = (
        db.query(TimeSlot)
        .filter(
            TimeSlot.id == appointment_data.time_slot_id,
            TimeSlot.status == "free",
        )
        .first()
    )

    if not slot:
        raise HTTPException(
            status_code=400, detail="Time slot is not available"
        )

    existing = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == current_user.id,
            Appointment.time_slot_id == appointment_data.time_slot_id,
            Appointment.status.in_(["pending", "confirmed"]),
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already have an appointment at this time",
        )

    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=appointment_data.doctor_id,
        time_slot_id=appointment_data.time_slot_id,
        service_id=appointment_data.service_id,
        complaints=appointment_data.complaints,
        status="confirmed",
    )

    slot.status = "booked"

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


@router.get("/appointments", response_model=List[AppointmentDetailResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == current_user.id)
        .order_by(Appointment.created_at.desc())
        .all()
    )

    result = []
    for app in appointments:
        doctor = db.query(Doctor).filter(Doctor.id == app.doctor_id).first()
        doctor_user = (
            db.query(User).filter(User.id == doctor.user_id).first()
            if doctor
            else None
        )
        slot = (
            db.query(TimeSlot).filter(TimeSlot.id == app.time_slot_id).first()
        )
        service = (
            db.query(Service).filter(Service.id == app.service_id).first()
            if app.service_id
            else None
        )

        result.append(
            {
                "id": app.id,
                "patient_id": app.patient_id,
                "doctor_id": app.doctor_id,
                "time_slot_id": app.time_slot_id,
                "service_id": app.service_id,
                "status": app.status,
                "complaints": app.complaints,
                "created_at": app.created_at,
                "updated_at": app.updated_at,
                "doctor_name": doctor_user.full_name if doctor_user else "",
                "doctor_specialization": doctor.specialization
                if doctor
                else "",
                "doctor_cabinet": doctor.cabinet_number if doctor else "",
                "time_start": slot.start_time if slot else None,
                "time_end": slot.end_time if slot else None,
                "service_name": service.name if service else None,
                "patient_name": current_user.full_name,
                "patient_phone": current_user.phone or "",
            }
        )

    return result


@router.delete("/appointments/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == current_user.id,
        )
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=400, detail="Cannot cancel this appointment"
        )

    appointment.status = "cancelled"

    slot = (
        db.query(TimeSlot)
        .filter(TimeSlot.id == appointment.time_slot_id)
        .first()
    )
    if slot:
        slot.status = "free"

    db.commit()

    return {"message": "Appointment cancelled successfully"}


@router.post("/appointments/{appointment_id}/rebook")
def rebook_appointment(
    appointment_id: int,
    new_time_slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    old_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == current_user.id,
            Appointment.status == "completed",
        )
        .first()
    )

    if not old_appointment:
        raise HTTPException(
            status_code=404, detail="Completed appointment not found"
        )

    new_slot = (
        db.query(TimeSlot)
        .filter(TimeSlot.id == new_time_slot_id, TimeSlot.status == "free")
        .first()
    )

    if not new_slot:
        raise HTTPException(
            status_code=400, detail="New time slot is not available"
        )

    new_appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=old_appointment.doctor_id,
        time_slot_id=new_time_slot_id,
        service_id=old_appointment.service_id,
        complaints=old_appointment.complaints,
        status="pending",
    )

    new_slot.status = "booked"
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@router.get("/services/{service_id}/doctors")
def get_doctors_by_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Получить всех врачей, предоставляющих конкретную услугу"""
    # Проверяем, существует ли услуга
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.is_active == True)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Получаем врачей через связь many-to-many
    doctors = (
        db.query(Doctor)
        .join(doctor_services, Doctor.id == doctor_services.c.doctor_id)
        .filter(
            doctor_services.c.service_id == service_id,
            Doctor.is_active == True,
        )
        .all()
    )

    result = []
    for doctor in doctors:
        user = db.query(User).filter(User.id == doctor.user_id).first()
        result.append(
            {
                "id": doctor.id,
                "full_name": user.full_name if user else "",
                "specialization": doctor.specialization,
                "cabinet_number": doctor.cabinet_number,
                "appointment_duration": doctor.appointment_duration,
            }
        )

    return result


@router.get("/doctors/{doctor_id}/services")
def get_services_by_doctor_patient(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Получить все услуги, предоставляемые конкретным врачом (для пациента)"""
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id, Doctor.is_active == True)
        .first()
    )
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    services = (
        db.query(Service)
        .join(doctor_services, Service.id == doctor_services.c.service_id)
        .filter(
            doctor_services.c.doctor_id == doctor_id, Service.is_active == True
        )
        .all()
    )

    return services
