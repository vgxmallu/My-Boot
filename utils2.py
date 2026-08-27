from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
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



