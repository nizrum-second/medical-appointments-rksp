from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db, get_current_admin
from ..models.service import Service, doctor_services
from ..models.doctor import Doctor
from ..models.user import User
from ..schemas.service import ServiceCreate, ServiceResponse

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=List[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.is_active == True).all()
    return services


@router.post("/", response_model=ServiceResponse)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = Service(**service_data.dict())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    for key, value in service_data.dict().items():
        setattr(service, key, value)

    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.is_active = False
    db.commit()
    return {"message": "Service deactivated"}


@router.post("/doctors/{doctor_id}/services/{service_id}")
def assign_service_to_doctor(
    doctor_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    service = db.query(Service).filter(Service.id == service_id).first()

    if not doctor or not service:
        raise HTTPException(
            status_code=404, detail="Doctor or service not found"
        )

    # Check if already assigned
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


@router.delete("/doctors/{doctor_id}/services/{service_id}")
def remove_service_from_doctor(
    doctor_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    db.execute(
        doctor_services.delete().where(
            doctor_services.c.doctor_id == doctor_id,
            doctor_services.c.service_id == service_id,
        )
    )
    db.commit()
    return {"message": "Service removed from doctor"}
