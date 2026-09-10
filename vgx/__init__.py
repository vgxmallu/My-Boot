from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import Config
import logging
from pyrogram.types import BotCommand

# Setup Logging
logging.basicConfig(level=logging.INFO)
# Initialize Scheduler
scheduler = AsyncIOScheduler()




# Initialize Bot
app = Client(
    "scheduler_bot_session",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="vgx") # Automatically loads files in plugins/
)
