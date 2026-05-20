from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta

from ..dependencies import get_db, get_current_doctor
from ..models.user import User
from ..models.doctor import Doctor
from ..models.appointment import Appointment
from ..models.schedule import TimeSlot

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/schedule")
def get_my_schedule(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    slots = (
        db.query(TimeSlot)
        .filter(
            TimeSlot.doctor_id == doctor.id,
            TimeSlot.start_time >= start_datetime,
            TimeSlot.start_time < end_datetime,
        )
        .order_by(TimeSlot.start_time)
        .all()
    )

    result = []
    for slot in slots:
        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.time_slot_id == slot.id,
                Appointment.status.in_(["pending", "confirmed", "completed"]),
            )
            .first()
        )

        patient_info = None
        if appointment:
            patient = (
                db.query(User)
                .filter(User.id == appointment.patient_id)
                .first()
            )
            patient_info = {
                "patient_id": patient.id,
                "patient_name": patient.full_name,
                "patient_phone": patient.phone,
                "complaints": appointment.complaints,
                "appointment_status": appointment.status,
                "service_id": appointment.service_id,
            }

        result.append(
            {
                "slot_id": slot.id,
                "appointment_id": appointment.id if appointment else None,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "status": slot.status,
                "patient": patient_info,
            }
        )

    return result


@router.get("/patients")
def get_my_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status.in_(["confirmed", "completed"]),
        )
        .order_by(Appointment.created_at.desc())
        .all()
    )

    result = []
    for app in appointments:
        patient = db.query(User).filter(User.id == app.patient_id).first()
        slot = (
            db.query(TimeSlot).filter(TimeSlot.id == app.time_slot_id).first()
        )

        result.append(
            {
                "appointment_id": app.id,
                "patient_name": patient.full_name,
                "patient_phone": patient.phone,
                "appointment_date": slot.start_time if slot else None,
                "complaints": app.complaints,
                "status": app.status,
                "created_at": app.created_at,
            }
        )

    return result


@router.put("/appointments/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.doctor_id == doctor.id,
        )
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=400, detail="Cannot complete cancelled appointment"
        )

    appointment.status = "completed"

    slot = (
        db.query(TimeSlot)
        .filter(TimeSlot.id == appointment.time_slot_id)
        .first()
    )
    if slot:
        slot.status = "completed"

    db.commit()

    return {"message": "Appointment marked as completed"}


@router.put("/appointments/{appointment_id}/cancel")
def cancel_appointment_doctor(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.doctor_id == doctor.id,
        )
        .first()
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status == "completed":
        raise HTTPException(
            status_code=400, detail="Cannot cancel completed appointment"
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

    return {"message": "Appointment cancelled"}


@router.get("/profile")
def get_my_doctor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Получить профиль врача (специализация, кабинет и т.д.)"""
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    return {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "specialization": doctor.specialization,
        "cabinet_number": doctor.cabinet_number,
        "appointment_duration": doctor.appointment_duration,
        "is_active": doctor.is_active,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone,
    }
