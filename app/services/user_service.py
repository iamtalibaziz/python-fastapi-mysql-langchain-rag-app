from sqlalchemy.orm import Session
from ..helpers import user_helper
from ..schemas import user_schema
from ..helpers.exceptions import CustomException
from fastapi import status

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return user_helper.get_users(db, skip=skip, limit=limit)

def get_user(db: Session, user_id: int):
    db_user = user_helper.get_user(db, user_id=user_id)
    if db_user is None:
        raise CustomException(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
    return db_user

def update_user(db: Session, user_id: int, user: user_schema.UserUpdate):
    db_user = user_helper.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise CustomException(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = user_helper.delete_user(db, user_id=user_id)
    if db_user is None:
        raise CustomException(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
    return db_user
