from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

    def __init__(self):
        self.client = None

    def connect(self):
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise e

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    async def check_mongodb_health(self):
        try:
            if not self.client:
                self.connect()
            # The ismaster command is cheap and does not require auth.
            await self.client.admin.command('ismaster')
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False

db = Database()
db.connect()

# Access database
ofwa_dash_db = db.client["ofwa_dash"]

# Pick a collection to operate on
users_collection = ofwa_dash_db["users"]
datasets_collection = ofwa_dash_db["datasets"]
analysis_logs_collection = ofwa_dash_db["analysis_logs"]
