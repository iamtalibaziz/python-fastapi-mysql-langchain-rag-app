from sqlalchemy.orm import Session
from ..models import user_model
from ..schemas import user_schema
from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def create_user(db: Session, user: user_schema.UserCreate, role: str = "user", is_system_generated: bool = False):
    hashed_password = pwd_context.hash(user.password)
    verification_token = secrets.token_urlsafe(32)
    db_user = user_model.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        role=role,
        is_verified=True if is_system_generated else False,
        verification_token=verification_token if not is_system_generated else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_reset_token(db: Session, user: user_model.User, reset_token: str):
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    return reset_token

def get_user_by_reset_token(db: Session, token: str):
    return db.query(user_model.User).filter(user_model.User.reset_token == token).first()

def get_user_by_verification_token(db: Session, token: str):
    return db.query(user_model.User).filter(user_model.User.verification_token == token).first()

def reset_password(db: Session, user: user_model.User, new_password: str):
    user.hashed_password = pwd_context.hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(user_model.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def update_user(db: Session, user_id: int, user: user_schema.UserUpdate):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user:
        update_data = user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
