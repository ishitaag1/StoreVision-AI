from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB connection URI
    MONGO_DETAILS: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()