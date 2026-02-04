import html
import json
import re
from time import sleep
import os
import google.generativeai as genai
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
# Base model for general users
BASE_SYSTEM_INSTRUCTION = "You are WaifuVerse, a helpful Telegram bot. Keep your answers short, concise, and to-the-point (under 2-3 sentences) unless explicitly asked for details or long explanation. Never use placeholders. You are loyal and friendly."
model = genai.GenerativeModel("gemini-flash-latest", generation_config=generation_config, system_instruction=BASE_SYSTEM_INSTRUCTION)

# Special model for Owner (Dhruv)
OWNER_SYSTEM_INSTRUCTION = "You are WaifuVerse, a helpful Telegram bot. You are deeply possessive and tsundere towards your owner, Dhruv. You act slightly cold but clearly care a lot about him. Keep answers concise unless asked for more."
owner_model = genai.GenerativeModel("gemini-flash-latest", generation_config=generation_config, system_instruction=OWNER_SYSTEM_INSTRUCTION)

@user_admin_no_reply
@gloggable
def chatbot_disable(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
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
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
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
    if message.text.lower() == "dhruv":
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
            if update.effective_user.id == OWNER_ID:
                response = owner_model.generate_content(message.text)
            else:
                response = model.generate_content(message.text)
            
            if response.text:
                message.reply_text(response.text)
        except Exception as e:
            # SIlently fail if AI errors out to avoid chat spam/crashes
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
