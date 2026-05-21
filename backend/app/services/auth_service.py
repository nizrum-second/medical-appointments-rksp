from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def truncate_password(password: str) -> str:
    return password[:72] if password else ""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )


def register_user(user_data: UserCreate, db: Session) -> User:
    existing_user = (
        db.query(User).filter(User.email == user_data.email).first()
    )
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    if user_data.role != "patient":
        raise HTTPException(
            status_code=400, detail="Only patient registration is allowed"
        )

    hashed_password = get_password_hash(truncate_password(user_data.password))
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone or "",
        role="patient",
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(user_data: UserLogin, db: Session) -> dict:
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(
        user_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


def update_user_profile(
    user_data: UserUpdate, current_user: User, db: Session
) -> User:
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.phone is not None:
        current_user.phone = user_data.phone
    if user_data.email is not None:
        existing = (
            db.query(User)
            .filter(User.email == user_data.email, User.id != current_user.id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Email already taken")
        current_user.email = user_data.email
    if user_data.password:
        current_user.hashed_password = get_password_hash(
            truncate_password(user_data.password)
        )

    db.commit()
    db.refresh(current_user)
    return current_user
