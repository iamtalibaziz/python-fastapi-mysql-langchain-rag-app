from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas import user_schema, response_schema
from app.services import auth_service
from app.configs.database import get_db
from datetime import datetime
from app.helpers.response_helper import success_response
from app.utils.logger import logger
from app.helpers.exceptions import CustomException

router = APIRouter()

@router.post("/signup", response_model=response_schema.SingleResponse[user_schema.User], responses={200: {"model": response_schema.SingleResponse[user_schema.User]}, 400: {"model": response_schema.ErrorResponse}, 422: {"model": response_schema.ValidationErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def signup(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = auth_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise CustomException(message="Email already registered", status_code=status.HTTP_400_BAD_REQUEST)
    new_user = auth_service.create_user(db=db, user=user)
    return success_response(data=user_schema.User.from_orm(new_user))

@router.post("/signin", response_model=response_schema.SingleResponse[user_schema.SignInResponse], responses={200: {"model": response_schema.SingleResponse[user_schema.SignInResponse]}, 400: {"model": response_schema.ErrorResponse}, 422: {"model": response_schema.ValidationErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def signin(request: user_schema.SignInRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, email=request.email, password=request.password)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}
    )
    return success_response(data={"access_token": access_token, "token_type": "Bearer", "user": user_schema.User.from_orm(user)})

@router.post("/forgot-password", response_model=response_schema.SingleResponse[dict], responses={200: {"model": response_schema.SingleResponse[dict]}, 404: {"model": response_schema.ErrorResponse}, 422: {"model": response_schema.ValidationErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def forgot_password(request: user_schema.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = auth_service.get_user_by_email(db, email=request.email)
    if not user:
        raise CustomException(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
    reset_token = auth_service.create_reset_token(db, user)
    # In a real application, you would send this token to the user's email
    return success_response(data={"reset_token": reset_token})

@router.post("/reset-password", response_model=response_schema.SingleResponse[dict], responses={200: {"model": response_schema.SingleResponse[dict]}, 400: {"model": response_schema.ErrorResponse}, 422: {"model": response_schema.ValidationErrorResponse}, 500: {"model": response_schema.ErrorResponse}})
def reset_password(request: user_schema.ResetPasswordRequest, db: Session = Depends(get_db)):
    user = auth_service.get_user_by_reset_token(db, token=request.reset_token)
    if not user or user.reset_token_expires < datetime.utcnow():
        raise CustomException(message="Invalid or expired token", status_code=status.HTTP_400_BAD_REQUEST)
    auth_service.reset_password(db, user, request.new_password)
    return success_response(data={"message": "Password updated successfully"})
