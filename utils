from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_settings_keyboard(session):
    s = session
    
    # Visual indicators
    pin_icon = "✅" if s.get("pin") else "❌"
    preview_icon = "✅" if s.get("preview") else "❌"
    repeat_txt = f"Every {s['repeat']}m" if s.get("repeat") else "Off ❌"
    time_txt = s.get("schedule_time").strftime("%H:%M") if s.get("schedule_time") else "Now ⚡"
    night_icon = "🌙 On" if s.get("night_mode") else "☀️ Off"

    buttons = [
        [
            InlineKeyboardButton(f"⏰ Time: {time_txt}", callback_data="set_time"),
            InlineKeyboardButton(f"🔄 Repeat: {repeat_txt}", callback_data="set_repeat")
        ],
        [
            InlineKeyboardButton(f"📌 Pin: {pin_icon}", callback_data="toggle_pin"),
            InlineKeyboardButton(f"🔗 Preview: {preview_icon}", callback_data="toggle_preview")
        ],
        [
            InlineKeyboardButton(f"🌃 Night Mode: {night_icon}", callback_data="toggle_night"),
            InlineKeyboardButton("🗑️ Auto-Delete", callback_data="set_autodel")
        ],
        [InlineKeyboardButton("✅ SAVE AND SCHEDULE", callback_data="save_job")]
    ]
    return InlineKeyboardMarkup(buttons)
