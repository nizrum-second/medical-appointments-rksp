from .auth import router as auth_router
from .patients import router as patients_router
from .admins import router as admins_router
from .doctors import router as doctors_router
from .services import router as services_router

__all__ = [
    "auth_router",
    "patients_router",
    "admins_router",
    "doctors_router",
    "services_router",
]
