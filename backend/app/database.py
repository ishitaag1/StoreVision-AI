from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

async def connect_to_mongo():
    """
    Initializes the asynchronous MongoDB client pool.
    This should be called during the FastAPI startup lifespan event.
    """
    db_instance.client = AsyncIOMotorClient(settings.MONGO_DETAILS)
    db_instance.db = db_instance.client.get_default_database()
    print("⚡ Connected smoothly to MongoDB async client cluster.")

async def close_mongo_connection():
    """
    Closes the connection pool gracefully.
    This should be called during the FastAPI shutdown lifespan event.
    """
    if db_instance.client:
        db_instance.client.close()
        print("🛑 MongoDB connection pools terminated gracefully.")

def get_collection(collection_name: str):
    """
    Helper utility to quickly reference a specific MongoDB collection.
    
    Args:
        collection_name (str): Name of the target collection.
        
    Returns:
        Agile collection reference from the active database instance.
    """
    return db_instance.db[collection_name]