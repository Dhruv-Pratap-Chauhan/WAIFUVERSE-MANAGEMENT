from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from MukeshRobot import dispatcher, SUPPORT_CHAT
from MukeshRobot.modules.helper_funcs.chat_status import dev_plus

SUDO_TEXT = """
✨ **ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴄᴏᴍᴍᴀɴᴅs** ✨

ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ sᴘᴇᴄɪᴀʟ ᴜsᴇʀs, ʙᴏᴛ sᴇᴛᴛɪɴɢs, ᴀɴᴅ ᴜsᴇ ᴀᴅᴠᴀɴᴄᴇᴅ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏᴏʟs.
"""

def sudo_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 ᴜsᴇʀs", callback_data="sudo_users"),
            InlineKeyboardButton("⚙️ ᴄᴏɴᴛʀᴏʟ", callback_data="sudo_control"),
        ],
        [
            InlineKeyboardButton("🛠 ᴛᴏᴏʟs", callback_data="sudo_tools"),
            InlineKeyboardButton("🛡 ʀᴇᴍᴏᴛᴇ", callback_data="sudo_remote"),
        ],
        [
            InlineKeyboardButton("📣 ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="sudo_broadcast"),
            InlineKeyboardButton("🚫 ɢʙᴀɴ​", callback_data="sudo_gban"),
        ],
        [
            InlineKeyboardButton("🧤 ᴍᴏᴅᴜʟᴇs", callback_data="sudo_disable"),
            InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"),
        ],
        [InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="sudo_close")]
    ])

@dev_plus
def sudo_cmds(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        SUDO_TEXT,
        reply_markup=sudo_buttons(),
        parse_mode=ParseMode.MARKDOWN
    )

def sudo_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == "sudo_users":
        text = """
👤 **ᴜsᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**
 ❍ /sudolist - ʟɪsᴛs ᴀʟʟ ᴅʀᴀɢᴏɴs
 ❍ /supportlist - ʟɪsᴛs ᴀʟʟ ᴅᴇᴍᴏɴs
 ❍ /tigers - ʟɪsᴛs ᴀʟʟ ᴛɪɢᴇʀs
 ❍ /wolves - ʟɪsᴛs ᴀʟʟ ᴡᴏʟᴠᴇs
 ❍ /devlist - ʟɪsᴛs ᴀʟʟ ᴅᴇᴠs
 ❍ /addsudo - ᴀᴅᴅ ᴅʀᴀɢᴏɴ
 ❍ /removesudo - ʀᴇᴍᴏᴠᴇ ᴅʀᴀɢᴏɴ
 ❍ /adddemon - ᴀᴅᴅ ᴅᴇᴍᴏɴ
 ❍ /removedemon - ʀᴇᴍᴏᴠᴇ ᴅᴇᴍᴏɴ
 ❍ /addtiger - ᴀᴅᴅ ᴛɪɢᴇʀ
 ❍ /removetiger - ʀᴇᴍᴏᴠᴇ ᴛɪɢᴇʀ
 ❍ /addwolf - ᴀᴅᴅ ᴡᴏʟғ
 ❍ /removewolf - ʀᴇᴍᴏᴠᴇ ᴡᴏʟғ
 ❍ /getchats - ɢᴇᴛ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs
"""
    elif data == "sudo_control":
        text = """
⚙️ **ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ**
 ❍ /reboot - ʀᴇsᴛᴀʀᴛ ʙᴏᴛ
 ❍ /gitpull - ᴘᴜʟʟ ᴜᴘᴅᴀᴛᴇs
 ❍ /leave <ɪᴅ> - ʟᴇᴀᴠᴇ ᴄʜᴀᴛ
 ❍ /lockdown - ᴛᴏɢɢʟᴇ ʟᴏɢɪɴ
 ❍ /ping - ᴄʜᴇᴄᴋ ᴘɪɴɢ
 ❍ /speedtest - ᴄʜᴇᴄᴋ sᴇʀᴠᴇʀ sᴘᴇᴇᴅ
"""
    elif data == "sudo_tools":
        text = """
🛠 **ᴅᴇᴠ ᴛᴏᴏʟs**
 ❍ /eval - ᴇᴠᴀʟᴜᴀᴛᴇ ᴄᴏᴅᴇ (ᴘʏʀᴏɢʀᴀᴍ)
 ❍ /exec - ᴇxᴇᴄᴜᴛᴇ ᴄᴏᴅᴇ (ᴛᴇʟᴇᴛʜᴏɴ)
 ❍ /sh - sʜᴇʟʟ ᴀᴄᴄᴇss
 ❍ /dbcleanup - ᴄʟᴇᴀɴ ᴅʙ
 ❍ /logs - ɢᴇᴛ ʙᴏᴛ ʟᴏɢs
 ❍ /debug [on/off] - ᴛᴏɢɢʟᴇ ᴅᴇʙᴜɢ
"""
    elif data == "sudo_remote":
        text = """
🛡 **ʀᴇᴍᴏᴛᴇ ᴄᴏɴᴛʀᴏʟ**
 ❍ /rban - ʀᴇᴍᴏᴛᴇ ʙᴀɴ
 ❍ /runban - ʀᴇᴍᴏᴛᴇ ᴜɴʙᴀɴ
 ❍ /rpunch - ʀᴇᴍᴏᴛᴇ ᴘᴜɴᴄʜ
 ❍ /rmute - ʀᴇᴍᴏᴛᴇ ᴍᴜᴛᴇ
 ❍ /runmute - ʀᴇᴍᴏᴛᴇ ᴜɴᴍᴜᴛᴇ
"""
    elif data == "sudo_gban":
        text = """
🚫 **ɢʟᴏʙᴀʟ ʙᴀɴ**
 ❍ /gban - ɢʟᴏʙᴀʟʟʏ ʙᴀɴ ᴜsᴇʀ
 ❍ /ungban - ᴜɴ-ɢʙᴀɴ ᴜsᴇʀ
 ❍ /gbanlist - ʟɪsᴛ ᴀʟʟ ɢʙᴀɴɴᴇᴅ
"""
    elif data == "sudo_broadcast":
        text = """
📣 **ʙʀᴏᴀᴅᴄᴀsᴛ (ᴏᴡɴᴇʀ ᴏɴʟʏ)**
 ❍ /broadcastusers - ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴜsᴇʀs
 ❍ /broadcastgroups - ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ɢʀᴏᴜᴘs
 ❍ *ᴀʟɪᴀsᴇs:* /buser, /bchat
"""
    elif data == "sudo_disable":
        text = """
🧤 **ᴍᴏᴅᴜʟᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**
 ❍ /disable - ᴅɪsᴀʙʟᴇ ᴄᴍᴅ
 ❍ /enable - ᴇɴᴀʙʟᴇ ᴄᴍᴅ
 ❍ /disablemodule - ᴅɪsᴀʙʟᴇ ᴍᴏᴅ
 ❍ /enablemodule - ᴇɴᴀʙʟᴇ ᴍᴏᴅ
 ❍ /listcmds - ʟɪsᴛ ᴛᴏɢɢʟᴇᴀʙʟᴇ
 ❍ /cmds - sʜᴏᴡ ᴅɪsᴀʙʟᴇᴅ
"""
    elif data == "sudo_back":
        query.message.edit_text(SUDO_TEXT, reply_markup=sudo_buttons(), parse_mode=ParseMode.MARKDOWN)
        return
    elif data == "sudo_close":
        query.message.delete()
        return

    query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◁ ʙᴀᴄᴋ", callback_data="sudo_back")]]),
        parse_mode=ParseMode.MARKDOWN
    )

SUDO_HANDLER = CommandHandler(["sudocmds", "dev"], sudo_cmds, run_async=True)
SUDO_CALLBACK_HANDLER = CallbackQueryHandler(sudo_callback, pattern=r"sudo_.*")

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUDO_CALLBACK_HANDLER)

__mod_name__ = "Sudocmds"
__handlers__ = [SUDO_HANDLER, SUDO_CALLBACK_HANDLER]
