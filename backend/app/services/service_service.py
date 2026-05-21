from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.service import Service, doctor_services
from ..models.doctor import Doctor


def get_services(db: Session):
    return db.query(Service).filter(Service.is_active == True).all()


def create_service(service_data, db: Session):
    service = Service(**service_data.dict())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def update_service(service_id: int, service_data, db: Session):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    for key, value in service_data.dict().items():
        setattr(service, key, value)

    db.commit()
    db.refresh(service)
    return service


def delete_service(service_id: int, db: Session):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.is_active = False
    db.commit()
    return {"message": "Service deactivated"}


def assign_service_to_doctor(doctor_id: int, service_id: int, db: Session):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    service = db.query(Service).filter(Service.id == service_id).first()

    if not doctor or not service:
        raise HTTPException(
            status_code=404, detail="Doctor or service not found"
        )

    existing = db.execute(
        doctor_services.select().where(
            doctor_services.c.doctor_id == doctor_id,
            doctor_services.c.service_id == service_id,
        )
    ).first()

    if not existing:
        db.execute(
            doctor_services.insert().values(
                doctor_id=doctor_id, service_id=service_id
            )
        )
        db.commit()

    return {"message": "Service assigned to doctor"}


def remove_service_from_doctor(doctor_id: int, service_id: int, db: Session):
    db.execute(
        doctor_services.delete().where(
            doctor_services.c.doctor_id == doctor_id,
            doctor_services.c.service_id == service_id,
        )
    )
    db.commit()
    return {"message": "Service removed from doctor"}
