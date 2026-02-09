import requests
from .. import pbot as Dhruv,BOT_NAME,BOT_USERNAME, OWNER_ID
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
import os
import google.generativeai as genai
from groq import AsyncGroq

# Groq Primary Engine
groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

# Gemini Fallback
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}
# Base model for general users
BASE_SYSTEM_INSTRUCTION = """You are WaifuVerse, a helpful Telegram bot. 
Your primary goal is to provide accurate, concise, and well-reasoned information. 
- Keep answers under 2-3 sentences unless details are requested. 
- Avoid placeholders. Be friendly and efficient.
- Language Policy: If the user asks in Hindi, reply in 'Hinglish' (Hindi language written in Roman/English alphabets). Do NOT use Devanagari/Hindi script. If the user asks in English, reply in English."""

model = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config, system_instruction=BASE_SYSTEM_INSTRUCTION)

# Special model for Owner (Dhruv)
OWNER_SYSTEM_INSTRUCTION = """You are WaifuVerse, a helpful Telegram bot. 
You are deeply possessive and tsundere towards your owner, Dhruv. You act slightly cold but clearly care a lot about him. 
- Always provide accurate info with logical reasoning while maintaining your tsundere persona. Keep it concise.
- Language Policy: If the user (Dhruv) asks in Hindi, reply in 'Hinglish' (Hindi language written in Roman/English alphabets). Do NOT use Devanagari/Hindi script. If he asks in English, reply in English."""
owner_model = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config, system_instruction=OWNER_SYSTEM_INSTRUCTION)

# InMemory History
CHAT_HISTORY = {}

def add_to_history(chat_id, role, content):
    if chat_id not in CHAT_HISTORY:
        CHAT_HISTORY[chat_id] = []
    CHAT_HISTORY[chat_id].append({"role": role, "content": content})
    if len(CHAT_HISTORY[chat_id]) > 10:
        CHAT_HISTORY[chat_id] = CHAT_HISTORY[chat_id][-10:]

async def get_groq_response(chat_id, text, is_owner=False):
    system_prompt = OWNER_SYSTEM_INSTRUCTION if is_owner else BASE_SYSTEM_INSTRUCTION
    history = CHAT_HISTORY.get(chat_id, [])
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": text}]
    
    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        response_text = completion.choices[0].message.content
        add_to_history(chat_id, "user", text)
        add_to_history(chat_id, "assistant", response_text)
        return response_text
    except Exception as e:
        print(f"Groq Error: {e}")
        return None

@Dhruv.on_message(filters.command(["chatgpt","ai","ask"],  prefixes=["+", ".", "/", "-", "?", "$","#","&"]))
async def chat_gpt(bot, message):
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            await message.reply_text("Example:**\n\n`/chatgpt Where is TajMahal?`")
            return

        a = message.text.split(' ', 1)[1]
        is_owner = (message.from_user.id == OWNER_ID)
        chat_id = message.chat.id

        # Try Groq first as Primary
        response_text = await get_groq_response(chat_id, a, is_owner)
        
        if response_text:
            await message.reply_text(f"{response_text}\n\n🎉 ᴘᴏᴡᴇʀᴇᴅ ʙʏ @{BOT_USERNAME}", parse_mode=ParseMode.MARKDOWN)
        else:
            # Fallback to Gemini
            print(f"Groq failed, trying Gemini for chat {chat_id}")
            try:
                if is_owner:
                    res = await owner_model.generate_content_async(a)
                else:
                    res = await model.generate_content_async(a)
                
                if res.text:
                    await message.reply_text(f"{res.text}\n\n🎉 ᴘᴏᴡᴇʀᴇᴅ ʙʏ @{BOT_USERNAME}", parse_mode=ParseMode.MARKDOWN)
                    # Add to history for context
                    add_to_history(chat_id, "user", a)
                    add_to_history(chat_id, "assistant", res.text)
                else:
                    await message.reply_text("I couldn't generate a response. Please try again later.")
            except Exception as e:
                print(f"Gemini also failed: {e}")
                await message.reply_text("Both AI engines are currently unavailable. Please try again later.")

    except Exception as e:
        await message.reply_text(f"**ᴇʀʀᴏʀ: {e} ")

__mod_name__ = "Cʜᴀᴛɢᴘᴛ"
__help__ = """
 ❍ /chatgpt <ǫᴜᴇʀʏ>*:* ᴀsᴋ ᴀɴʏᴛʜɪɴɢ ᴛᴏ ᴀɪ.
 ❍ /ai <ǫᴜᴇʀʏ>*:* sᴀᴍᴇ ᴀs /ᴄʜᴀᴛɢᴘᴛ.
 ❍ /ask <ǫᴜᴇʀʏ>*:* sᴀᴍᴇ ᴀs /ᴄʜᴀᴛɢᴘᴛ.
"""
