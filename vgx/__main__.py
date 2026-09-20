import logging
import asyncio
from datetime import datetime
from pyrogram import idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from vgx import app, scheduler
from vgx.database.db_chedul import _db
from vgx.module.adv_cheduling import run_job



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SchedulerBot")


async def restore_jobs():
    """Reschedules jobs from DB on restart"""
    logger.info("♻️  Restoring Database Jobs...")
    count = 0
    jobs = await db.get_all_jobs()

    async for job in jobs:
        if job.get('paused'):
            continue

        # Check if missed timing
        run_at = job.get('next_run')
        if not run_at or run_at < datetime.now():
            run_at = datetime.now()  # Run immediately if missed

        scheduler.add_job(
            run_job,
            "date",
            run_date=run_at,
            args=[str(job['_id'])],
            id=str(job['_id']),
            replace_existing=True,
        )
        count += 1
    logger.info(f"✅ Restored {count} active jobs.")


async def main():
    # 1. Start APScheduler and Pyrogram Client asynchronously
    scheduler.start()
    await app.start()

    # 4. Restore DB Jobs
    asyncio.create_task(restore_jobs())
    print("🚀 Bot Started! Send /schedule")

    # 5. Keep client alive safely
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main()) 
