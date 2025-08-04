from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.services.company_service import get_all_companies
from app.schemas.company_schema import CompanyResponse
from app.schemas.response_schema import ListResponse
from app.helpers.response_helper import success_response
from typing import List
from app.models import user_model
from app.middleware.verify_access_token import verify_access_token

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/", response_model=ListResponse[CompanyResponse])
def read_companies(db: Session = Depends(get_db), current_user: user_model.User = Depends(verify_access_token)):
    companies = get_all_companies(db, user_id=current_user.id)
    return success_response(data=companies)
