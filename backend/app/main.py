import asyncio

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from .logger import get_logger

from .api import (
    auth_router,
    patients_router,
    admins_router,
    doctors_router,
    services_router,
)
from .api.auth import get_password_hash, truncate_password
from .config import settings
from .database import engine, Base, SessionLocal
from .models.user import User
from .logger import setup_logging, get_logger, RequestIDMiddleware


setup_logging()
logger = get_logger(__name__)


app = FastAPI(title="Aboba228ZOV Clinic Appointment System API", version="1.0.0")
app.add_middleware(RequestIDMiddleware)


def init_database():
    """Инициализация базы данных и создание админа"""
    logger.info("Initializing database")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            logger.info(
                "Admin user already exists", admin_id=existing_admin.id
            )
            return

        admin_user = (
            db.query(User).filter(User.email == settings.admin_email).first()
        )
        if admin_user:
            admin_user.role = "admin"
            admin_user.hashed_password = get_password_hash(
                truncate_password(settings.admin_password)
            )
            admin_user.is_active = True
            logger.info(
                "Existing user promoted to admin", user_id=admin_user.id
            )
        else:
            admin_user = User(
                email=settings.admin_email,
                hashed_password=get_password_hash(
                    truncate_password(settings.admin_password)
                ),
                full_name="Администратор",
                phone="88888888888",
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            logger.info("Admin user created", email=settings.admin_email)

        db.commit()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    logger.warning(
        "Validation error", errors=exc.errors(), path=request.url.path
    )
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    if exc.status_code == 400:
        logger.warning("Bad request", detail=exc.detail, path=request.url.path)
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid request body - malformed JSON"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.on_event("startup")
def on_startup():
    logger.info(
        "Application starting", service="clinic-backend", version="1.0.0"
    )
    init_database()
    logger.info("Application started successfully")


@app.on_event("shutdown")
def on_shutdown():
    logger.info("Application shutting down")


@app.get("/")
def root(request: Request):
    logger.debug("Root endpoint called", path="/")
    return {"message": "Clinic Management System API", "status": "running"}


@app.get("/health")
def health_check(request: Request):
    logger.debug("Health check called")
    return {"status": "healthy"}


@app.get("/slow_request")
async def slow_endpoint():
    await asyncio.sleep(10)
    return {"message": "completed"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(admins_router)
app.include_router(doctors_router)
app.include_router(services_router)
