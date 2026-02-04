
import importlib
import re
import time
import asyncio
import traceback
import json
import html
from platform import python_version as y
from sys import argv

from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

from MukeshRobot.modules.no_sql import get_served_chats, get_served_users
from MukeshRobot import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)
from MukeshRobot.modules import ALL_MODULES
from MukeshRobot.modules.helper_funcs.chat_status import is_user_admin
from MukeshRobot.modules.helper_funcs.misc import paginate_modules


# =========================================================================================================================================
#                                                           CONSTANTS & CONFIG
# =========================================================================================================================================

START_IMG_PATH = "MukeshRobot/resources/start_img.jpg"
HELP_IMG_PATH = "MukeshRobot/resources/help_img.jpg"

PM_START_TEX = """ 
**ᴏ-ᴏʜ, ɪᴛ's ʏᴏᴜ, {}?** 🙄 
**ɢɪᴠᴇ ᴍᴇ ᴀ sᴇᴄᴏɴᴅ, ᴏᴋᴀʏ? ᴅᴏɴ'ᴛ ʀᴜsʜ ᴍᴇ!** 😤 
"""

PM_START_TEXT = """ 
**ʜᴇʏ** [{}](tg://user?id={})! 🥀
**ɪ'ᴍ** [{}]({}) **ʜᴇʀᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘs!**

**ʜɪᴛ ʜᴇʟᴘ ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ... ʙᴀᴋᴀ!** 😤
"""

buttons = [
    [
        InlineKeyboardButton(text="📚 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="Main_help"),
        InlineKeyboardButton(text="💬 sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"),
    ],
    [
        InlineKeyboardButton(text="➕ ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{dispatcher.bot.username}?startgroup=true"),
    ],
]

HELP_MAIN_MENU = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="📕 ᴍᴀɴᴀɢᴇᴍᴇɴᴛ", callback_data="mgmt_help"),
        ],
        [
            InlineKeyboardButton(text="🎯 ᴛᴏʏᴢ", callback_data="fun_help"),
            InlineKeyboardButton(text="🤖 ᴀɪ-ʟᴀʙ", callback_data="ai_help"),
        ],
        [
            InlineKeyboardButton(text="💡 ᴛᴏᴏʟs", callback_data="tools_help"),
            InlineKeyboardButton(text="🏮 ᴀɴɪᴍᴇ", callback_data="anime_help"),
        ],
        [InlineKeyboardButton(text="• ʜᴏᴍᴇ •", callback_data="mukesh_back")]
    ]
)

HELP_STRINGS = f"""
» *{BOT_NAME}  ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟʟᴏᴡ ᴛᴏ ᴛʜᴇ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀʙᴏᴜᴛ sᴘᴇᴄɪғɪᴄs ᴄᴏᴍᴍᴀɴᴅ*"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

# =========================================================================================================================================
#                                                            MODULE LOADING
# =========================================================================================================================================

MGMT_MODULES = [
    "admin", "bans", "muting", "locks", "welcome", "reporting", "log_channel",
    "blacklist", "cust_filters", "flood", "approve", "cleaner", "notes", 
    "rules", "zombies", "antiban", "blacklist_stickers", "nightmode", 
    "unbanall", "purge", "tagall", "blacklistusers", "connection", "disable"
]
FUN_MODULES = ["fun", "dicegame", "truth_dare", "animation", "couples", "sexy", "shayri"]
AI_MODULES = ["aiimage", "chatgpt"]
ANIME_MODULES = ["anime", "animez"]

MGMT_HELPABLE = {}
FUN_HELPABLE = {}
TOOLS_HELPABLE = {}
AI_HELPABLE = {}
ANIME_HELPABLE = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("MukeshRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        mod_key = imported_module.__mod_name__.lower()
        HELPABLE[mod_key] = imported_module
        
        m_name = module_name.lower()
        if m_name in MGMT_MODULES:
            MGMT_HELPABLE[mod_key] = imported_module
        elif m_name in FUN_MODULES:
            FUN_HELPABLE[mod_key] = imported_module
        elif m_name in AI_MODULES:
            AI_HELPABLE[mod_key] = imported_module
        elif m_name in ANIME_MODULES:
            ANIME_HELPABLE[mod_key] = imported_module
        else:
            # All other helpable modules go to Tools
            TOOLS_HELPABLE[mod_key] = imported_module

    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# =========================================================================================================================================
#                                                           HELPER FUNCTIONS
# =========================================================================================================================================

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = HELP_MAIN_MENU
    dispatcher.bot.send_photo(
        chat_id=chat_id,
        photo=open(HELP_IMG_PATH, 'rb'),
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(chat_name),
                reply_markup=InlineKeyboardMarkup(paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


# =========================================================================================================================================
#                                                           CALLBACK HANDLERS
# =========================================================================================================================================

def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    # Category matches
    category_mod_match = re.match(r"(.+?)_help_module\((.+?)\)", query.data)
    category_match = re.match(r"(.+?)_help_prev\((.+?)\)", query.data)
    category_next_match = re.match(r"(.+?)_help_next\((.+?)\)", query.data)
    category_back_match = re.match(r"(.+?)_help_back", query.data)

    try:
        if mod_match or category_mod_match:
            module = mod_match.group(1) if mod_match else category_mod_match.group(2)
            prefix = "help_back" if mod_match else f"{category_mod_match.group(1)}_help"
            
            if module not in HELPABLE:
                return

            text = (
                "» *ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ​​* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_caption(text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=prefix), InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}")]]
                ),
            )

        elif prev_match or category_match:
            if prev_match:
                curr_page = int(prev_match.group(1))
                dict_to_use = HELPABLE
                prefix = "help"
            else:
                curr_page = int(category_match.group(2))
                cat = category_match.group(1)
                prefix = f"{cat}_help"
                dict_to_use = MGMT_HELPABLE if cat == "mgmt" else FUN_HELPABLE if cat == "fun" else TOOLS_HELPABLE if cat == "tools" else AI_HELPABLE if cat == "ai" else ANIME_HELPABLE
            
            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, dict_to_use, prefix)
                ),
            )

        elif next_match or category_next_match:
            if next_match:
                next_page = int(next_match.group(1))
                dict_to_use = HELPABLE
                prefix = "help"
            else:
                next_page = int(category_next_match.group(2))
                cat = category_next_match.group(1)
                prefix = f"{cat}_help"
                dict_to_use = MGMT_HELPABLE if cat == "mgmt" else FUN_HELPABLE if cat == "fun" else TOOLS_HELPABLE if cat == "tools" else AI_HELPABLE if cat == "ai" else ANIME_HELPABLE

            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, dict_to_use, prefix)
                ),
            )

        elif back_match or category_back_match:
            if back_match:
                # Redirect old "Back" button to the main category menu
                query.message.edit_caption(f" ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ {BOT_NAME}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=HELP_MAIN_MENU
                )
                context.bot.answer_callback_query(query.id)
                return
            else:
                cat = category_back_match.group(1)
                prefix = f"{cat}_help"
                dict_to_use = MGMT_HELPABLE if cat == "mgmt" else FUN_HELPABLE if cat == "fun" else TOOLS_HELPABLE if cat == "tools" else AI_HELPABLE if cat == "ai" else ANIME_HELPABLE

            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, dict_to_use, prefix)
                ),
            )

        context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass


def Mukesh_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    
    if query.data == "mukesh_back":
        first_name = update.effective_user.first_name 
        query.message.edit_caption(
            PM_START_TEXT.format(
                escape_markdown(first_name),
                update.effective_user.id,
                BOT_NAME,
                f"https://t.me/{context.bot.username}"
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
        )


def MukeshRobot_Main_Callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "Main_help":
        query.message.edit_caption(f" ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ {BOT_NAME}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=HELP_MAIN_MENU,
        )
    elif query.data == "mgmt_help":
        query.message.edit_caption(HELP_STRINGS,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, MGMT_HELPABLE, "mgmt_help")
            ),
        )
    elif query.data == "fun_help":
        query.message.edit_caption(HELP_STRINGS,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, FUN_HELPABLE, "fun_help")
            ),
        )
    elif query.data == "tools_help":
        query.message.edit_caption(HELP_STRINGS,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, TOOLS_HELPABLE, "tools_help")
            ),
        )
    elif query.data == "ai_help":
        query.message.edit_caption(HELP_STRINGS,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, AI_HELPABLE, "ai_help")
            ),
        )
    elif query.data == "anime_help":
        # Direct help for Anime since it's a single merged module now
        text = (
            "» *ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ​​* *Aɴɪᴍᴇ* :\n"
            + ANIME_HELPABLE["anime"].__help__
        )
        query.message.edit_caption(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="Main_help"), InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}")]]
            ),
        )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◁",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text("""Hi there! There are quite a few settings for {} - go ahead and pick what "
                you're interested in.""".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(text=
                """Hi there! There are quite a few settings for {} - go ahead and pick what 
                you're interested in.""".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text("""Hi there! There are quite a few settings for {} - go ahead and pick what 
                you're interested in.""".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


# =========================================================================================================================================
#                                                            COMMAND HANDLERS
# =========================================================================================================================================

def start(update: Update, context: CallbackContext):
    args = context.args
    global uptime
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                    ),
                )
            elif args[0].lower() == "markdownhelp":
                IMPORTED["exᴛʀᴀs"].markdown_help_sender(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rᴜʟᴇs" in IMPORTED:
                IMPORTED["rᴜʟᴇs"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            
            usr = update.effective_user
            lol = update.effective_message.reply_text(
                PM_START_TEX.format(usr.first_name), parse_mode=ParseMode.MARKDOWN
            )
            time.sleep(0.3)
            lol.edit_text("💕")
            time.sleep(0.2)
            lol.edit_text("Waking up... 🥱")
            time.sleep(0.2)
            lol.delete()
            update.effective_message.reply_photo(
                open(START_IMG_PATH, 'rb'),
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    update.effective_user.id,
                    BOT_NAME,
                    f"https://t.me/{dispatcher.bot.username}"
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            open(START_IMG_PATH, 'rb'),
            caption="**ɪ'ᴍ ᴀᴡᴀᴋᴇ!** 😤\n\n**ɪғ ʏᴏᴜ ɴᴇᴇᴅ ʜᴇʟᴘ, ᴘᴍ ᴍᴇ. ᴅᴏɴ'ᴛ sᴘᴀᴍ ᴛʜᴇ ᴄʜᴀᴛ, ʙᴀᴋᴀ!** 💢",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="💬 ᴘᴍ ᴍᴇ", url=f"https://t.me/{dispatcher.bot.username}?start=help"),
                        InlineKeyboardButton(text="💬 sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"),
                    ],
                    [
                        InlineKeyboardButton(text="➕ ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{dispatcher.bot.username}?startgroup=true"),
                    ]
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
        )


def error_handler(update, context):
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)
    except TimedOut:
        print("no nono3")
    except NetworkError:
        print("no nono4")
    except ChatMigrated as err:
        print("no nono5")
        print(err)
    except TelegramError:
        print(error)


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat 
    args = update.effective_message.text.split(None, 1)

    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_photo(
                open(HELP_IMG_PATH, 'rb'),
                f"**ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ᴏғ {module.capitalize()}**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=" ʜᴇʟᴘ ​",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_photo(
            open(HELP_IMG_PATH, 'rb'),
            "**» ᴡʜᴇʀᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ?**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 ᴏᴩᴇɴ ɪɴ ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ",
                            url="https://t.me/{}?start=help".format(context.bot.username),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="👥 ᴏᴩᴇɴ ʜᴇʀᴇ",
                            callback_data="Main_help",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="help_back"),InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}")]]
            ),
        )

    else:
        # Match the category-based menu from /start
        update.effective_message.reply_photo(
            open(HELP_IMG_PATH, 'rb'),
            f" ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ {BOT_NAME}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=HELP_MAIN_MENU,
        )


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "**ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴛʜɪs ᴄʜᴀᴛ's sᴇᴛᴛɪɴɢs ᴀs ᴡᴇʟʟ ᴀs ʏᴏᴜʀs**"
            msg.reply_photo(
                open(START_IMG_PATH, 'rb'),
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴇᴛᴛɪɴɢs​",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "**ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs**"

    else:
        send_settings(chat.id, user.id, True)


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


# =========================================================================================================================================
#                                                           MAIN EXECUTOR
# =========================================================================================================================================

def main():
    global x
    x=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="➕ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ➕",
                            url=f"https://t.me/{dispatcher.bot.username}?startgroup=true"
                            )
                       ]
                ]
                     )
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@{SUPPORT_CHAT}",
                photo=open(START_IMG_PATH, 'rb'),
                caption=f"""
✨ㅤ{BOT_NAME} ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ.
━━━━━━━━━━━━━
**ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ Dhruv**
**ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ:** `{y()}`
**ʟɪʙʀᴀʀʏ ᴠᴇʀsɪᴏɴ:** `{telever}`
**ᴛᴇʟᴇᴛʜᴏɴ ᴠᴇʀsɪᴏɴ:** `{tlhver}`
**ᴩʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ:** `{pyrover}`
━━━━━━━━━━━━━
""",reply_markup=x,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)
    
    start_handler = CommandHandler(["start", "alive"], start, run_async=True)
    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*|.*_help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        Mukesh_about_callback, pattern=r"mukesh_", run_async=True
    )
    mukeshrobot_main_handler = CallbackQueryHandler(
        MukeshRobot_Main_Callback, pattern=r".*_help",run_async=True)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)
    
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(mukeshrobot_main_handler)
    dispatcher.add_error_handler(error_callback)
    
    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        pbot.start()
        telethn.start(bot_token=TOKEN)
        telethn.run_until_disconnected()


if __name__ == "__main__":
    main()
