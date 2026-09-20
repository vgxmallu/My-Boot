from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from bson.objectid import ObjectId

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URL)
        self.db = self.client[Config.DB_NAME]
        self.jobs = self.db.jobs
        
    # FIX: Changed from `async def` to `def`
    def __getattr__(self, name):
        # Prevent Pyrogram and internal Python checks from breaking
        if name == "handlers" or name.startswith("__"):
            raise AttributeError(f"'Database' object has no attribute '{name}'")
            
        # This will synchronously return the Motor method, 
        # which you can then await normally in your code.
        return getattr(self.db, name)

    async def add_job(self, data):
        return await self.jobs.insert_one(data)

    async def get_job(self, job_id):
        try:
            return await self.jobs.find_one({"_id": ObjectId(job_id)})
        except:
            return None

    async def get_user_jobs(self, user_id):
        # Returns jobs created by specific user (returns an async cursor)
        return self.jobs.find({"user_id": user_id})

    async def get_all_jobs(self):
        # Returns an async cursor
        return self.jobs.find({})
        
    async def update_job(self, job_id, data):
        await self.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": data})

    async def delete_job(self, job_id):
        await self.jobs.delete_one({"_id": ObjectId(job_id)})

    # Toggles Pause/Resume
    async def toggle_pause(self, job_id, is_paused):
        await self.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {"paused": is_paused}})

# BEST PRACTICE: Naming it '_db' instead of 'db' makes Pyrogram's 
# plugin loader ignore it completely, boosting startup speed.
# (If you must use 'db = Database()', the __getattr__ fix above will still prevent the crash).
_db = Database()
