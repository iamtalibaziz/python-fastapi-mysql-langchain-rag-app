from sqlalchemy.orm import Session
from ..helpers import user_helper
from ..schemas import user_schema
from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..configs.database import get_db
from ..configs.config import settings
from ..helpers.exceptions import CustomException
from app.middleware.verify_access_token import verify_access_token

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_by_email(db: Session, email: str):
    return user_helper.get_user_by_email(db, email)

def create_user(db: Session, user: user_schema.UserCreate):
    return user_helper.create_user(db, user)

def create_reset_token(db: Session, user: user_schema.User):
    reset_token = secrets.token_urlsafe(32)
    return user_helper.create_reset_token(db, user, reset_token)

def get_user_by_reset_token(db: Session, token: str):
    return user_helper.get_user_by_reset_token(db, token)

def reset_password(db: Session, user: user_schema.User, new_password: str):
    return user_helper.reset_password(db, user, new_password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str):
    user = user_helper.get_user_by_email(db, email=email)
    if not user:
        raise CustomException(message="Incorrect email or password", status_code=status.HTTP_401_UNAUTHORIZED)
    if not verify_password(password, user.hashed_password):
        raise CustomException(message="Incorrect email or password", status_code=status.HTTP_401_UNAUTHORIZED)
    return user
