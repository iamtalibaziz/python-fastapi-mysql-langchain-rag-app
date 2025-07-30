from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, error_messages={"min_length": "First name cannot be empty"})
    last_name: str = Field(..., min_length=1, error_messages={"min_length": "Last name cannot be empty"})
    email: str = Field(..., min_length=1, error_messages={"min_length": "Email cannot be empty"})
    password: str = Field(..., min_length=1, error_messages={"min_length": "Password cannot be empty"})

    @validator('password')
    def strong_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    status: str
    is_verified: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=1, error_messages={"min_length": "Email cannot be empty"})

class ResetPasswordRequest(BaseModel):
    reset_token: str = Field(..., min_length=1, error_messages={"min_length": "Reset token cannot be empty"})
    new_password: str = Field(..., min_length=1, error_messages={"min_length": "New password cannot be empty"})

class SignInRequest(BaseModel):
    email: str = Field(..., min_length=1, error_messages={"min_length": "Email cannot be empty"})
    password: str = Field(..., min_length=1, error_messages={"min_length": "Password cannot be empty"})

class UserUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, error_messages={"min_length": "First name cannot be empty"})
    last_name: str | None = Field(None, min_length=1, error_messages={"min_length": "Last name cannot be empty"})
    email: str | None = Field(None, min_length=1, error_messages={"min_length": "Email cannot be empty"})

class SignInResponse(BaseModel):
    access_token: str
    token_type: str
    user: User


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, error_messages={"min_length": "Old password cannot be empty"})
    new_password: str = Field(..., min_length=1, error_messages={"min_length": "New password cannot be empty"})
