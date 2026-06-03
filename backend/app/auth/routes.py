from fastapi import APIRouter, Response, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.database import get_collection
from app.auth.utils import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication System"])

class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterSchema):
    users_collection = get_collection("users")
    
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user accounts with this email address already exists."
        )
        
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "password": hash_password(user_data.password)
    }
    
    result = await users_collection.insert_one(new_user)
    return {"status": "success", "message": "User registered successfully.", "uid": str(result.inserted_id)}


@router.post("/login")
async def login_user(login_data: UserLoginSchema, response: Response):
    users_collection = get_collection("users")
    
    user = await users_collection.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email credentials or incorrect account password."
        )
        
    token = create_access_token(data={"sub": str(user["_id"])})
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400,
        expires=86400,
        samesite="lax",
        secure=False
    )
    
    return {
        "status": "success", 
        "user": {"username": user["username"], "email": user["email"]}
    }


@router.post("/logout")
async def logout_user(response: Response, current_user: dict = Depends(get_current_user)):
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    return {"status": "success", "message": "Logged out successfully."}


@router.get("/me")
async def check_session_validity(current_user: dict = Depends(get_current_user)):
    """ Allows the frontend dashboard to check if a valid session cookie exists. """
    return {
        "authenticated": True, 
        "user": {"username": current_user["username"], "email": current_user["email"]}
    }