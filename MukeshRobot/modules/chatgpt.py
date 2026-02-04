import requests
from .. import pbot as Dhruv,BOT_NAME,BOT_USERNAME, OWNER_ID
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
import os
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}
# Base model for general users
BASE_SYSTEM_INSTRUCTION = "You are WaifuVerse, a helpful Telegram bot. Keep your answers short, concise, and to-the-point (under 2-3 sentences) unless explicitly asked for details or long explanation."
model = genai.GenerativeModel("gemini-flash-latest", generation_config=generation_config, system_instruction=BASE_SYSTEM_INSTRUCTION)

# Special model for Owner (Dhruv)
OWNER_SYSTEM_INSTRUCTION = "You are WaifuVerse, a helpful Telegram bot. You are deeply possessive and tsundere towards your owner, Dhruv. You act slightly cold but clearly care a lot about him. Keep answers concise unless asked for more."
owner_model = genai.GenerativeModel("gemini-flash-latest", generation_config=generation_config, system_instruction=OWNER_SYSTEM_INSTRUCTION)
@Dhruv.on_message(filters.command(["chatgpt","ai","ask"],  prefixes=["+", ".", "/", "-", "?", "$","#","&"]))
async def chat_gpt(bot, message):
    
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            await message.reply_text(
            "Example:**\n\n`/chatgpt Where is TajMahal?`")
        else:
            a = message.text.split(' ', 1)[1]
            if message.from_user.id == OWNER_ID:
                response = await owner_model.generate_content_async(a)
            else:
                response = await model.generate_content_async(a)

            if response.text:
                await message.reply_text(f"{response.text}\n\n🎉ᴘᴏᴡᴇʀᴇᴅ ʙʏ @{BOT_USERNAME}", parse_mode=ParseMode.MARKDOWN)
            else:
                await message.reply_text("I couldn't generate a response. Please try again.")
    except Exception as e:
        await message.reply_text(f"**ᴇʀʀᴏʀ: {e} ")

__mod_name__ = "Cʜᴀᴛɢᴘᴛ"
__help__ = """
 ❍ /chatgpt <ǫᴜᴇʀʏ>*:* ᴀsᴋ ᴀɴʏᴛʜɪɴɢ ᴛᴏ ᴀɪ.
 ❍ /ai <ǫᴜᴇʀʏ>*:* sᴀᴍᴇ ᴀs /ᴄʜᴀᴛɢᴘᴛ.
 ❍ /ask <ǫᴜᴇʀʏ>*:* sᴀᴍᴇ ᴀs /ᴄʜᴀᴛɢᴘᴛ.
"""
