from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
import datetime
from pyrogram.enums import ButtonStyle


from vgx.database.db_chedul import _db as db
from vgx.module import sessions
from vgx import app, scheduler


def get_wizard_kb(data):
    """Generates the Creation Dashboard"""
    # Visual Toggles
    pin = "✅" if data.get('pin') else "❌"
    dl = "✅" if data.get('del_last') else "❌"
    
    # Interval formatting
    mins = data.get('interval', 0)
    int_txt = f"{mins}m" if mins > 0 else "One-Time"

    # Auto Delete formatting
    ad = data.get('auto_del', 0)
    ad_txt = f"{ad}s" if ad > 0 else "Off"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Content", callback_data="wiz_set_content", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🎯 Target", callback_data="wiz_set_target", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton(f"📌 Pin: {pin}", callback_data="wiz_toggle_pin", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(f"♻️ Del Last: {dl}", callback_data="wiz_toggle_dellast", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton(f"⏲ Interval: {int_txt}", callback_data="wiz_set_interval", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(f"⏳ Auto-Del: {ad_txt}", callback_data="wiz_set_autodel", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("✅ SAVE & START", callback_data="wiz_save", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("❌ Cancel", callback_data="wiz_cancel", style=ButtonStyle.DANGER)
        ]
    ])

def get_job_controls(job_id, paused):
    """Generates controls for an active job"""
    pause_btn = "▶️ Resume" if paused else "⏸ Pause"
    pause_data = f"mngr_resume_{job_id}" if paused else f"mngr_pause_{job_id}"
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(pause_btn, callback_data=pause_data),
            InlineKeyboardButton("📝 Edit Msg", callback_data=f"mngr_edit_{job_id}", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🕒 Custom Mins", callback_data="wiz_set_custom_int", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🗑 Delete or Clear", callback_data=f"mngr_delete_{job_id}", style=ButtonStyle.DANGER)
        ],
        [InlineKeyboardButton("🔙 Back to List", callback_data="myjobs_refresh", style=ButtonStyle.SUCCESS)]
    ])





@Client.on_message(filters.private & filters.command("myjobs"))
async def list_jobs(c, m):
    jobs = await db.get_user_jobs(m.from_user.id)
    btn_list = []
    async for j in jobs:
        status = "⏸" if j.get('paused') else "▶️"
        chat = str(j.get('target_chat'))[:10]
        btn_list.append([
            InlineKeyboardButton(
                f"{status} {chat} | {j.get('interval', 0)}m", 
                callback_data=f"mngr_view_{j['_id']}"
            )
        ])
    
    if not btn_list:
        return await m.reply("📭 No active schedules found.")
        
    await m.reply("📋 **Your Scheduled Jobs:**", reply_markup=InlineKeyboardMarkup(btn_list))


async def run_job(job_id):
    # 1. Fetch Job Data
    job = await db.get_job(job_id)
    if not job: 
        return
    
    # 2. Check Pause Status
    if job.get('paused'):
        return 

    chat_id = job['target_chat']
    
    # 3. Extract Content Variables Safely (From Top Snippet)
    # This prevents KeyErrors if fields are missing
    txt = job.get('text', "")
    m_type = job.get('media_type')
    fid = job.get('file_id')

    try:
        # --- A. DELETE LAST MESSAGE FEATURE ---
        if job.get('del_last') and job.get('last_msg_id'):
            try: 
                await app.delete_messages(chat_id, job['last_msg_id'])
            except: 
                pass # Message might be too old or already deleted

        # --- B. SEND CONTENT (Merged Logic) ---
        sent = None
        
        if m_type == 'photo':
            sent = await app.send_photo(chat_id, fid, caption=txt)
        elif m_type == 'video':
            sent = await app.send_video(chat_id, fid, caption=txt)
        elif m_type == 'sticker':
            # Stickers do not support captions
            sent = await app.send_sticker(chat_id, fid)
        else:
            # Default to Text
            sent = await app.send_message(chat_id, txt, disable_web_page_preview=True)

        # --- C. SAVE MESSAGE ID (For 'Delete Last' feature) ---
        if sent:
            await db.update_job(job_id, {"last_msg_id": sent.id})

        # --- D. PIN MESSAGE FEATURE ---
        if job.get('pin') and sent:
            try: 
                await sent.pin(disable_notification=False)
            except: 
                pass

        # --- E. AUTO-DELETE FEATURE ---
        # If auto_del is set (e.g., 60 seconds), schedule a deletion task
        if job.get('auto_del', 0) > 0 and sent:
            scheduler.add_job(
                app.delete_messages, "date",
                run_date=datetime.datetime.now() + datetime.timedelta(seconds=job['auto_del']),
                args=[chat_id, sent.id]
            )

    except Exception as e:
        print(f"❌ Job Error: {e}")

    # 4. RECURSION (Schedule Next Run)
    interval = job.get('interval', 0)
    
    if interval > 0:
        # Calculate next run time
        next_run = datetime.datetime.now() + datetime.timedelta(minutes=interval)
        
        # Update DB
        await db.update_job(job_id, {"next_run": next_run})
        
        # Reschedule in APScheduler
        scheduler.add_job(
            run_job, "date",
            run_date=next_run,
            args=[job_id], id=job_id,
            replace_existing=True
        )
    else:
        # One-time job finished: Clean up from DB
        await db.delete_job(job_id)



@Client.on_callback_query(filters.regex("^close$"))
async def col_callback(client, query):
    await query.answer("❌ Closed ❌")
    await asyncio.sleep(1)
    await query.message.delete()
# In plugins/manager.py
@Client.on_callback_query(filters.regex(r"^mngr_edit_"))
async def trigger_edit_msg(c, q):
    job_id = q.data.split("_")[2]
    uid = q.from_user.id
    
    # Store in session that we are editing an EXISTING job
    sessions[uid] = {
        "step": "editing_existing_job",
        "job_id": job_id
    }
    
    await q.answer("📝 Send the NEW text/media for this job.")
    await q.message.reply("📤 **Please send the new Content (Text/Photo/Video/Sticker).\n\nThis will replace the current message of the scheduled job.")
    


@Client.on_callback_query(filters.regex(r"^mngr_"))
async def manager_callbacks(c, q):
    action, job_id = q.data.split("_")[1], q.data.split("_")[2]
    
    # 1. VIEW JOB
    if action == "view":
        job = await db.get_job(job_id)
        if not job: return await q.answer("Job not found", show_alert=True)
        
        txt = (
            f"🆔 `{job_id}`\n"
            f"🎯 Target: `{job['target_chat']}`\n"
            f"⏲ Interval: {job.get('interval')}m\n"
            f"📌 Pin: {job.get('pin')}\n"
            f"📂 Type: {job.get('media_type')}"
        )
        await q.message.edit_text(txt, reply_markup=get_job_controls(job_id, job.get('paused')))

    # 2. PAUSE / RESUME
    elif action in ["pause", "resume"]:
        is_paused = (action == "pause")
        await db.toggle_pause(job_id, is_paused)
        
        # Update UI
        job = await db.get_job(job_id)
        await q.message.edit_reply_markup(get_job_controls(job_id, job.get('paused')))
        await q.answer(f"Job {action}d!")

    # 3. DELETE
    elif action == "delete":
        await db.delete_job(job_id)
        try: scheduler.remove_job(job_id)
        except: pass
        await q.message.edit_text("🗑 **Job Deleted.**")

@Client.on_callback_query(filters.regex("^myjobs_refresh$"))
async def refresh_list(c, q):
    # Triggers the /myjobs list again
    # We can just delete and ask user to run command, or re-run logic.
    # Simple way:
    await q.message.delete()
    await q.message.reply("🔄 Please run /myjobs again to refresh.")
