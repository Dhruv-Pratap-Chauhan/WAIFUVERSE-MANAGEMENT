import html
import json
import re
import os
import google.generativeai as genai
from groq import Groq
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

import MukeshRobot.modules.sql.chatbot_sql as sql
from MukeshRobot import BOT_ID, BOT_NAME, BOT_USERNAME, dispatcher, OWNER_ID
from MukeshRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from MukeshRobot.modules.log_channel import gloggable

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}
# System instructions for the model
BASE_SYSTEM_INSTRUCTION = """You are WaifuVerse, a helpful Telegram bot. 
Your primary goal is to provide accurate, concise, and well-reasoned information. 
- Keep answers under 2-3 sentences unless details are requested. 
- Avoid placeholders. Be friendly and efficient.
- If asked, the owner of this bot is Dhruv.
- Language Policy: If the user asks in Hindi, reply in 'Hinglish' (Hindi language written in Roman/English alphabets). Do NOT use Devanagari/Hindi script. If the user asks in English, reply in English."""

model = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config, system_instruction=BASE_SYSTEM_INSTRUCTION)

# Groq client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# InMemory History
CHAT_HISTORY = {}

def add_to_history(chat_id, role, content):
    if chat_id not in CHAT_HISTORY:
        CHAT_HISTORY[chat_id] = []
    CHAT_HISTORY[chat_id].append({"role": role, "content": content})
    if len(CHAT_HISTORY[chat_id]) > 10:
        CHAT_HISTORY[chat_id] = CHAT_HISTORY[chat_id][-10:]

def get_groq_response(chat_id, text):
    history = CHAT_HISTORY.get(chat_id, [])
    messages = [{"role": "system", "content": BASE_SYSTEM_INSTRUCTION}] + history + [{"role": "user", "content": text}]
    
    try:
        completion = groq_client.chat.completions.create(
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

@user_admin_no_reply
@gloggable
def chatbot_disable(update: Update, context: CallbackContext) -> str:
    query: CallbackQuery = update.callback_query
    user: User = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Chat = update.effective_chat
        is_disabled = sql.disable_chatbot(chat.id)
        if is_disabled:
            is_disabled = sql.disable_chatbot(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ᴀɪ ᴅɪꜱᴀʙʟᴇᴅ\n"
                f"<b>ᴀᴅᴍɪɴ :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin_no_reply
@gloggable
def chatbot_enable(update: Update, context: CallbackContext) -> str:
    query: CallbackQuery = update.callback_query
    user: User = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Chat = update.effective_chat
        is_disabled = sql.enable_chatbot(chat.id)
        if is_disabled:
            is_disabled = sql.enable_chatbot(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ᴀɪ ᴇɴᴀʙʟᴇ\n"
                f"<b>ᴀᴅᴍɪɴ :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin
@gloggable
def chatbot_settings(update: Update, context: CallbackContext):
    message = update.effective_message
    msg = "• ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data="add_chat({})"),
                InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data="rm_chat({})"),
            ],
        ]
    )
    message.reply_text(
        text=msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


def is_chatbot_triggered(context: CallbackContext, message):
    reply_message = message.reply_to_message
    text = message.text.lower()
    if "waifuverse" in text:
        return True
    elif BOT_USERNAME in message.text.upper():
        return True
    elif reply_message:
        if reply_message.from_user.id == BOT_ID:
            return True
    else:
        return False


def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_disabled = sql.is_chatbot_disabled(chat_id)
    if is_disabled:
        return

    if message.text and not message.document:
        if not is_chatbot_triggered(context, message):
            return
        bot.send_chat_action(chat_id, action="typing")
        try:
            
            
            # Try Groq first as Primary
            response_text = get_groq_response(chat_id, message.text)
            
            if response_text:
                message.reply_text(response_text)
            else:
                # Fallback to Gemini
                print(f"Groq failed, trying Gemini for chatbot in {chat_id}")
                try:
                    res = model.generate_content(message.text)
                    
                    if res.text:
                        message.reply_text(res.text)
                        # Add to history
                        add_to_history(chat_id, "user", message.text)
                        add_to_history(chat_id, "assistant", res.text)
                    else:
                        # Silently fail
                        pass
                except Exception as e:
                    print(f"Gemini also failed: {e}")
                    pass
        except Exception as e:
            print(f"Chatbot failed: {e}")
            pass

CHATBOTK_HANDLER = CommandHandler("chatbot", chatbot_settings, run_async=True)
ADD_CHAT_HANDLER = CallbackQueryHandler(chatbot_enable, pattern=r"add_chat", run_async=True)
RM_CHAT_HANDLER = CallbackQueryHandler(chatbot_disable, pattern=r"rm_chat", run_async=True)
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
    run_async=True,
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    CHATBOT_HANDLER,
]
