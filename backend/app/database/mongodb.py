"""MongoDB client connection manager for AgentShield AI.
Uses PyMongo with connection pooling and graceful offline/memory fallback.
"""
import logging
from typing import Optional, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MongoDBManager:
    """Manages PyMongo client and database access with connection pooling."""

    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._is_connected: bool = False

    def connect(self) -> bool:
        """Establish connection to MongoDB Atlas or local MongoDB."""
        try:
            self._client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2000,
                maxPoolSize=50,
                minPoolSize=5,
            )
            # Ping database to confirm connection
            self._client.admin.command("ping")
            self._db = self._client[settings.MONGODB_DATABASE]
            self._is_connected = True
            logger.info("Successfully connected to MongoDB: %s", settings.MONGODB_DATABASE)
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            logger.warning("MongoDB unavailable at %s: %s. Running in graceful offline mode.", settings.MONGODB_URI, str(e))
            self._is_connected = False
            return False

    def disconnect(self):
        """Close active database client connection."""
        if self._client:
            self._client.close()
            self._is_connected = False
            logger.info("Closed MongoDB connection.")

    def get_db(self) -> Optional[Database]:
        """Return the active database instance."""
        if not self._is_connected or self._db is None:
            self.connect()
        return self._db

    def get_collection(self, collection_name: str) -> Any:
        """Return collection object if connected."""
        db = self.get_db()
        if db is not None:
            return db[collection_name]
        return None

    def is_healthy(self) -> bool:
        """Probe database connectivity."""
        if not self._client:
            return False
        try:
            self._client.admin.command("ping")
            return True
        except Exception:
            return False


# Singleton instance
mongo_manager = MongoDBManager()
