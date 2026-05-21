# main.py
import argparse
import sys
import asyncio
import socket

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.logging import setup_logging, get_logger
from app.core.middleware import (
    InputSanitizerMiddleware,
    RequestIDMiddleware,
    AccessLogMiddleware,
)
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.books.router import router as books_router
from app.modules.copies.router import router as copies_router
from app.modules.loans.router import router as loans_router
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import UserCreate
from app.modules.auth.repository import UserRepository, RoleRepository

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Clinic Appointment System",
    version="1.0.0",
    description="Клиент-серверное приложение для управления онлайн-записями пациентов",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(AccessLogMiddleware)
app.add_middleware(InputSanitizerMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(books_router, prefix="/api/v1/books", tags=["Books"])
app.include_router(copies_router, prefix="/api/v1/copies", tags=["Copies"])
app.include_router(loans_router, prefix="/api/v1/loans", tags=["Loans"])


@app.get("/")
async def root():
    return {
        "message": "Clinic Appointment System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/slow")
async def slow_endpoint():
    await asyncio.sleep(10)
    return {"message": "completed"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
        client=request.client.host if request.client else None,
    )
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error"}
    )


@app.on_event("shutdown")
async def shutdown():
    engine.dispose()


def run_server():
    """Запуск веб-сервера"""
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=None,
        access_log=False,
        timeout_graceful_shutdown=10,
        limit_concurrency=1000,
    )


def run_migrate():
    """Применить миграции Alembic и выйти"""
    import alembic.config

    alembic.config.main(argv=["upgrade", "head"])
    logger.info("Migrations applied successfully.")


def create_admin_user(
    email: str,
    password: str,
    first_name: str = "Admin",
    last_name: str = "User",
):
    """Создать администратора, если такого email ещё нет"""
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        existing = user_repo.get_by_email(email)
        if existing:
            logger.info("Admin user already exists.", email=email)
            return

        role_repo = RoleRepository(db)
        admin_role = role_repo.get_by_name("admin")
        if not admin_role:
            logger.error("Admin role not found. Run 'init-roles' or check DB.")
            sys.exit(1)

        # Создаём пользователя
        user_data = UserCreate(
            email=email,
            password=password,
            password_confirm=password,
            first_name=first_name,
            last_name=last_name,
            middle_name=None,
            phone=None,
        )

        auth_service = AuthService(db)
        from app.core.security import get_password_hash

        user_dict = user_data.dict(exclude={"password", "password_confirm"})
        user_dict["password_hash"] = get_password_hash(user_data.password)
        new_user = user_repo.create(user_dict)
        user_repo.add_role(new_user, admin_role)
        logger.info(f"Admin user {email} created.")
    except Exception as e:
        logger.error("Failed to create admin user", error=str(e))
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clinic Appointments System")
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    subparsers.add_parser("server", help="Start the web server")

    subparsers.add_parser("migrate", help="Run database migrations and exit")

    admin_parser = subparsers.add_parser(
        "create-admin", help="Create an admin user"
    )
    admin_parser.add_argument("--email", required=True, help="Admin email")
    admin_parser.add_argument(
        "--password", required=True, help="Admin password"
    )
    admin_parser.add_argument(
        "--first-name", default="Admin", help="First name"
    )
    admin_parser.add_argument("--last-name", default="User", help="Last name")

    args = parser.parse_args()

    if args.command == "server":
        run_server()
    elif args.command == "migrate":
        run_migrate()
    elif args.command == "create-admin":
        create_admin_user(
            email=args.email,
            password=args.password,
            first_name=args.first_name,
            last_name=args.last_name,
        )
    else:
        parser.print_help()
        sys.exit(1)
