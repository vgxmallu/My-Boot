from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.private & filters.command("start"))
async def start(c, m):
    await m.reply(
        "**Hey i am Bot**\n\n"
        "Commands:\n"
    )
