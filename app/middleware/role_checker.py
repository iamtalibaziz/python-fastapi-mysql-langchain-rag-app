from fastapi import Depends, status
from app.schemas import user_schema
from app.middleware.verify_access_token import verify_access_token
from app.helpers.exceptions import CustomException

def role_checker(required_role: str):
    def check_role(current_user: user_schema.User = Depends(verify_access_token)):
        if current_user.role != required_role:
            raise CustomException(
                message="The user doesn't have enough privileges",
                status_code=status.HTTP_403_FORBIDDEN
            )
        return current_user
    return check_role
