from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas import user_schema, response_schema
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

@router.get("/me/", response_model=response_schema.SingleResponse[user_schema.User], responses={401: {"model": response_schema.ErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
async def read_users_me(current_user: user_schema.User = Depends(verify_access_token)):
    return success_response(data=user_schema.User.from_orm(current_user))

@router.get("/", response_model=response_schema.ListResponse[user_schema.User], dependencies=[Depends(role_checker("admin"))], responses={401: {"model": response_schema.ErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_service.get_users(db, skip=skip, limit=limit)
    return success_response(data=[user_schema.User.from_orm(user) for user in users])

@router.get("/{user_id}", response_model=response_schema.SingleResponse[user_schema.User], responses={401: {"model": response_schema.ErrorResponse}, 404: {"model": response_schema.ErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def read_user(user_id: int, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    db_user = user_service.get_user(db, user_id=user_id)
    return success_response(data=user_schema.User.from_orm(db_user))

@router.put("/{user_id}", response_model=response_schema.SingleResponse[user_schema.User], responses={401: {"model": response_schema.ErrorResponse}, 404: {"model": response_schema.ErrorResponse}, 422: {"model": response_schema.ValidationErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def update_user(user_id: int, user: user_schema.UserUpdate, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    db_user = user_service.update_user(db, user_id=user_id, user=user)
    return success_response(data=user_schema.User.from_orm(db_user))

@router.delete("/{user_id}", response_model=response_schema.SingleResponse[user_schema.User], responses={401: {"model": response_schema.ErrorResponse}, 404: {"model": response_schema.ErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    db_user = user_service.delete_user(db, user_id=user_id)
    return success_response(data=user_schema.User.from_orm(db_user))

@router.post("/change-password", response_model=response_schema.SingleResponse[dict], responses={200: {"model": response_schema.SingleResponse[dict]}, 400: {"model": response_schema.ErrorResponse}, 401: {"model": response_schema.ErrorResponse}, 422: {"model": response_schema.ValidationErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def change_password(request: user_schema.ChangePasswordRequest, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    auth_service.change_password(db, user=current_user, old_password=request.old_password, new_password=request.new_password)
    return success_response(data={"message": "Password changed successfully"})
