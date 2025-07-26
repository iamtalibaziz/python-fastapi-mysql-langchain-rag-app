from fastapi import Depends, status, Security
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from app.configs.config import settings
from app.schemas import user_schema
from app.services import auth_service
from app.configs.database import get_db
from sqlalchemy.orm import Session
from app.helpers.exceptions import CustomException

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def verify_access_token(db: Session = Depends(get_db), token: str = Security(api_key_header)):
    try:
        if not token:
            raise CustomException(message="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED)
        parts = token.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            raise CustomException(message="Invalid token format", status_code=status.HTTP_401_UNAUTHORIZED)
        token = parts[1]
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise CustomException(message="Could not validate credentials", status_code=status.HTTP_401_UNAUTHORIZED)
        token_data = user_schema.TokenData(email=email)
    except JWTError:
        raise CustomException(message="Could not validate credentials", status_code=status.HTTP_401_UNAUTHORIZED)
    user = auth_service.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise CustomException(message="Could not validate credentials", status_code=status.HTTP_401_UNAUTHORIZED)
    return user
