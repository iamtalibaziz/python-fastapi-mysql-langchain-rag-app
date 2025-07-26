from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas import user_schema
from app.services import user_service
from app.configs.database import get_db
from typing import List
from app.helpers.response_helper import success_response, error_response
from app.utils.logger import logger
from app.helpers.exceptions import CustomException
from app.middleware.verify_access_token import verify_access_token
from app.middleware.role_checker import role_checker
from app.services import auth_service

router = APIRouter()

@router.get("/me/")
async def read_users_me(current_user: user_schema.User = Depends(verify_access_token)):
    return success_response(data=user_schema.User.from_orm(current_user))

@router.get("/", dependencies=[Depends(role_checker("admin"))])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = user_service.get_users(db, skip=skip, limit=limit)
        return success_response(data=[user_schema.User.from_orm(user) for user in users])
    except CustomException as e:
        return error_response(message=e.message, status_code=e.status_code, errors=e.errors)
    except Exception as e:
        logger.error(f"Error reading users: {e}")
        raise e

@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    try:
        db_user = user_service.get_user(db, user_id=user_id)
        return success_response(data=user_schema.User.from_orm(db_user))
    except CustomException as e:
        return error_response(message=e.message, status_code=e.status_code, errors=e.errors)
    except Exception as e:
        logger.error(f"Error reading user {user_id}: {e}")
        raise e

@router.put("/{user_id}")
def update_user(user_id: int, user: user_schema.UserUpdate, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    try:
        db_user = user_service.update_user(db, user_id=user_id, user=user)
        return success_response(data=user_schema.User.from_orm(db_user))
    except CustomException as e:
        return error_response(message=e.message, status_code=e.status_code, errors=e.errors)
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise e

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    try:
        db_user = user_service.delete_user(db, user_id=user_id)
        return success_response(data=user_schema.User.from_orm(db_user))
    except CustomException as e:
        return error_response(message=e.message, status_code=e.status_code, errors=e.errors)
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise e
