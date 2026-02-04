import requests
from .. import pbot as Dhruv,BOT_NAME,BOT_USERNAME, OWNER_ID
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
import os
import google.generativeai as genai
from groq import AsyncGroq

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

# Groq Fallback
groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

async def get_groq_response(text, is_owner=False):
    system_prompt = OWNER_SYSTEM_INSTRUCTION if is_owner else BASE_SYSTEM_INSTRUCTION
    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.9,
            max_tokens=512,
            top_p=1,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        return None
@Dhruv.on_message(filters.command(["chatgpt","ai","ask"],  prefixes=["+", ".", "/", "-", "?", "$","#","&"]))
async def chat_gpt(bot, message):
    
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            await message.reply_text(
            "Example:**\n\n`/chatgpt Where is TajMahal?`")
        else:
            a = message.text.split(' ', 1)[1]
            is_owner = (message.from_user.id == OWNER_ID)
            
            try:
                if is_owner:
                    response = await owner_model.generate_content_async(a)
                else:
                    response = await model.generate_content_async(a)

                if response.text:
                    await message.reply_text(f"{response.text}\n\n🎉ᴘᴏᴡᴇʀᴇᴅ ʙʏ @{BOT_USERNAME}", parse_mode=ParseMode.MARKDOWN)
                else:
                    raise Exception("Gemini returned empty response")
            except Exception as e:
                # Fallback to Groq
                print(f"Gemini failed, trying Groq: {e}")
                res_text = await get_groq_response(a, is_owner)
                if res_text:
                    await message.reply_text(f"{res_text}\n\n🎉ᴘᴏᴡᴇʀᴇᴅ ʙʏ @{BOT_USERNAME}", parse_mode=ParseMode.MARKDOWN)
                else:
                    await message.reply_text("I couldn't generate a response. Please try again later.")
    except Exception as e:
        await message.reply_text(f"**ᴇʀʀᴏʀ: {e} ")

__mod_name__ = "Cʜᴀᴛɢᴘᴛ"
__help__ = """
 ❍ /chatgpt <ǫᴜᴇʀʏ>*:* ᴀsᴋ ᴀɴʏᴛʜɪɴɢ ᴛᴏ ᴀɪ.
 ❍ /ai <ǫᴜᴇʀʏ>*:* sᴀᴍᴇ ᴀs /ᴄʜᴀᴛɢᴘᴛ.
 ❍ /ask <ǫᴜᴇʀʏ>*:* sᴀᴍᴇ ᴀs /ᴄʜᴀᴛɢᴘᴛ.
"""
