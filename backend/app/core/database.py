import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger("industrial_twin.database")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db_wrapper = Database()

async def connect_to_mongo():
    """Connect to MongoDB instance using Motor client."""
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGO_URI}...")
        db_wrapper.client = AsyncIOMotorClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=3000
        )
        db_wrapper.db = db_wrapper.client[settings.MONGO_DB_NAME]
        logger.info(f"Successfully configured MongoDB database '{settings.MONGO_DB_NAME}'")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Allow service to start even if MongoDB is temporarily unavailable
        db_wrapper.client = None
        db_wrapper.db = None

async def close_mongo_connection():
    """Close MongoDB connection gracefully."""
    if db_wrapper.client:
        logger.info("Closing MongoDB connection...")
        db_wrapper.client.close()
        db_wrapper.client = None
        db_wrapper.db = None
        logger.info("MongoDB connection closed.")

def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Dependency / Helper to retrieve current database handle."""
    return db_wrapper.db
