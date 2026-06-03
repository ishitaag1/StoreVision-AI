from pydantic import BaseModel, Field, EmailStr

class UserRegisterSchema(BaseModel):
    """
    Validates incoming request data for creating a new user account.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique display name")
    email: EmailStr = Field(..., description="Valid primary email address")
    password: str = Field(..., min_length=6, description="Secure account password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin_user",
                "email": "admin@storeintel.com",
                "password": "supersecurepassword123"
            }
        }

class UserLoginSchema(BaseModel):
    """
    Validates user credentials incoming during a login request.
    """
    email: EmailStr = Field(..., description="Registered account email address")
    password: str = Field(..., description="Account account password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@storeintel.com",
                "password": "supersecurepassword123"
            }
        }