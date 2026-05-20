from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional

from ..dependencies import get_db, get_current_admin
from ..models.user import User
from ..models.doctor import Doctor
from ..models.schedule import TimeSlot, ScheduleTemplate
from ..models.appointment import Appointment
from ..models.service import Service, doctor_services
from ..schemas.user import UserResponse, UserRoleUpdate
from ..schemas.doctor import (
    DoctorCreate,
    DoctorResponse,
    DoctorWithUserResponse,
)
from ..schemas.appointment import AppointmentDetailResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.put("/users/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Изменить роль пользователя (только для администратора)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Cannot change your own role"
        )

    user.role = role_data.role
    db.commit()
    db.refresh(user)

    if role_data.role == "doctor":
        existing_doctor = (
            db.query(Doctor).filter(Doctor.user_id == user.id).first()
        )
        if not existing_doctor:
            doctor = Doctor(
                user_id=user.id,
                specialization="Не указана",
                cabinet_number="000",
                appointment_duration=30,
            )
            db.add(doctor)
            db.commit()

    return user


@router.get("/doctors", response_model=List[DoctorWithUserResponse])
def get_all_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Получить всех врачей (только для администратора)"""
    doctors = db.query(Doctor).filter(Doctor.is_active == True).all()

    result = []
    for doctor in doctors:
        user = db.query(User).filter(User.id == doctor.user_id).first()
        if user:
            result.append(
                {
                    "id": doctor.id,
                    "user_id": doctor.user_id,
                    "specialization": doctor.specialization,
                    "cabinet_number": doctor.cabinet_number,
                    "appointment_duration": doctor.appointment_duration,
                    "is_active": doctor.is_active,
                    "created_at": doctor.created_at,
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone": user.phone,
                }
            )

    return result


@router.post("/doctors", response_model=DoctorResponse)
def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    doctor = Doctor(**doctor_data.dict())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    for key, value in doctor_data.dict().items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/doctors/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.is_active = False
    db.commit()
    return {"message": "Doctor deactivated successfully"}


@router.post("/doctors/{doctor_id}/schedule/template")
def set_schedule_template(
    doctor_id: int,
    day_of_week: int,
    start_time: str,
    end_time: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    template = ScheduleTemplate(
        doctor_id=doctor_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
    )
    db.add(template)
    db.commit()
    return {"message": "Schedule template created"}


@router.post("/doctors/{doctor_id}/slots/generate")
def generate_slots(
    doctor_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    templates = (
        db.query(ScheduleTemplate)
        .filter(
            ScheduleTemplate.doctor_id == doctor_id,
            ScheduleTemplate.is_working == True,
        )
        .all()
    )

    if not templates:
        raise HTTPException(
            status_code=400,
            detail="No schedule template found for this doctor",
        )

    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()
        template = next(
            (t for t in templates if t.day_of_week == day_of_week), None
        )

        if template:
            slot_start = datetime.combine(current_date, template.start_time)
            slot_end = datetime.combine(current_date, template.end_time)

            while slot_start < slot_end:
                slot_end_time = slot_start + timedelta(
                    minutes=30
                )  # Default 30 min slots

                existing = (
                    db.query(TimeSlot)
                    .filter(
                        TimeSlot.doctor_id == doctor_id,
                        TimeSlot.start_time == slot_start,
                    )
                    .first()
                )

                if not existing:
                    slot = TimeSlot(
                        doctor_id=doctor_id,
                        start_time=slot_start,
                        end_time=slot_end_time,
                        status="free",
                    )
                    db.add(slot)

                slot_start = slot_end_time

        current_date += timedelta(days=1)

    db.commit()
    return {"message": f"Slots generated from {start_date} to {end_date}"}


@router.get("/appointments", response_model=List[AppointmentDetailResponse])
def get_all_appointments(
    doctor_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    query = db.query(Appointment)

    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status:
        query = query.filter(Appointment.status == status)
    if start_date:
        query = query.filter(Appointment.created_at >= start_date)
    if end_date:
        query = query.filter(
            Appointment.created_at <= end_date + timedelta(days=1)
        )

    appointments = query.order_by(Appointment.created_at.desc()).all()

    result = []
    for app in appointments:
        patient = db.query(User).filter(User.id == app.patient_id).first()
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
                "patient_name": patient.full_name if patient else "",
                "patient_phone": patient.phone if patient else "",
            }
        )

    return result


@router.put("/appointments/{appointment_id}/confirm")
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    appointment = (
        db.query(Appointment).filter(Appointment.id == appointment_id).first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = "confirmed"
    db.commit()

    return {"message": "Appointment confirmed"}


@router.put("/appointments/{appointment_id}/reschedule")
def reschedule_appointment(
    appointment_id: int,
    new_time_slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    appointment = (
        db.query(Appointment).filter(Appointment.id == appointment_id).first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    old_slot = (
        db.query(TimeSlot)
        .filter(TimeSlot.id == appointment.time_slot_id)
        .first()
    )
    if old_slot:
        old_slot.status = "free"

    new_slot = (
        db.query(TimeSlot).filter(TimeSlot.id == new_time_slot_id).first()
    )
    if not new_slot or new_slot.status != "free":
        raise HTTPException(
            status_code=400, detail="New time slot not available"
        )

    appointment.time_slot_id = new_time_slot_id
    appointment.status = "confirmed"
    new_slot.status = "booked"

    db.commit()

    return {"message": "Appointment rescheduled successfully"}


@router.get("/reports/doctors-load")
def get_doctors_load(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
    result = []

    for doctor in doctors:
        total_slots = (
            db.query(TimeSlot)
            .filter(
                TimeSlot.doctor_id == doctor.id,
                TimeSlot.start_time >= start_date,
                TimeSlot.start_time <= end_date + timedelta(days=1),
            )
            .count()
        )

        booked_slots = (
            db.query(TimeSlot)
            .filter(
                TimeSlot.doctor_id == doctor.id,
                TimeSlot.start_time >= start_date,
                TimeSlot.start_time <= end_date + timedelta(days=1),
                TimeSlot.status.in_(["booked", "completed"]),
            )
            .count()
        )

        completed_appointments = (
            db.query(Appointment)
            .filter(
                Appointment.doctor_id == doctor.id,
                Appointment.status == "completed",
                Appointment.created_at >= start_date,
                Appointment.created_at <= end_date + timedelta(days=1),
            )
            .count()
        )

        doctor_user = db.query(User).filter(User.id == doctor.user_id).first()

        result.append(
            {
                "doctor_id": doctor.id,
                "doctor_name": doctor_user.full_name if doctor_user else "",
                "specialization": doctor.specialization,
                "total_slots": total_slots,
                "booked_slots": booked_slots,
                "occupancy_rate": (booked_slots / total_slots * 100)
                if total_slots > 0
                else 0,
                "completed_appointments": completed_appointments,
            }
        )

    return result


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    full_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Получить всех пользователей с фильтром по имени (только для администратора)"""
    query = db.query(User)

    if full_name:
        query = query.filter(User.full_name.ilike(f"%{full_name}%"))

    users = query.all()
    return users


@router.post("/users/{user_id}/make-doctor")
def make_user_doctor(
    user_id: int,
    specialization: str = "Общий врач",
    cabinet_number: str = "100",
    appointment_duration: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Назначить пользователя врачом"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_doctor = (
        db.query(Doctor).filter(Doctor.user_id == user_id).first()
    )
    if existing_doctor:
        raise HTTPException(status_code=400, detail="User is already a doctor")

    doctor = Doctor(
        user_id=user_id,
        specialization=specialization,
        cabinet_number=cabinet_number,
        appointment_duration=appointment_duration,
    )
    db.add(doctor)
    db.commit()

    return {
        "message": f"User {user.email} is now a doctor",
        "doctor_id": doctor.id,
    }


@router.get("/services/{service_id}/doctors")
def get_doctors_by_service_admin(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Получить всех врачей, предоставляющих конкретную услугу (для админа)"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    doctors = (
        db.query(Doctor)
        .join(doctor_services, Doctor.id == doctor_services.c.doctor_id)
        .filter(doctor_services.c.service_id == service_id)
        .all()
    )

    result = []
    for doctor in doctors:
        user = db.query(User).filter(User.id == doctor.user_id).first()
        result.append(
            {
                "id": doctor.id,
                "user_id": doctor.user_id,
                "full_name": user.full_name if user else "",
                "email": user.email if user else "",
                "phone": user.phone if user else "",
                "specialization": doctor.specialization,
                "cabinet_number": doctor.cabinet_number,
                "appointment_duration": doctor.appointment_duration,
                "is_active": doctor.is_active,
            }
        )

    return result


@router.get("/doctors/{doctor_id}/services")
def get_services_by_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Получить все услуги, предоставляемые конкретным врачом"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
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
