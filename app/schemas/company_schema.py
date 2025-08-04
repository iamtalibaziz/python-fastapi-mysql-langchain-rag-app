from pydantic import BaseModel

class CompanyResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True
