from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from bson.objectid import ObjectId

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URL)
        self.db = self.client[Config.DB_NAME]
        self.jobs = self.db.jobs
    async def __getattr__(self, name):
        if name == "handlers":
            raise AttributeError("'Database' object has no attribute 'handlers'")
        return getattr(self.db, name)

    async def add_job(self, data):
        return await self.jobs.insert_one(data)

    async def get_job(self, job_id):
        try:
            return await self.jobs.find_one({"_id": ObjectId(job_id)})
        except:
            return None

    async def get_user_jobs(self, user_id):
        # Returns jobs created by specific user
        return self.jobs.find({"user_id": user_id})

    async def get_all_jobs(self):
        return self.jobs.find({})
        
    async def update_job(self, job_id, data):
        await self.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": data})

    async def delete_job(self, job_id):
        await self.jobs.delete_one({"_id": ObjectId(job_id)})

    # Toggles Pause/Resume
    async def toggle_pause(self, job_id, is_paused):
        await self.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {"paused": is_paused}})

db = Database()
