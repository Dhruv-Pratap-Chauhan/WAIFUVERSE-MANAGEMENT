import random
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.enums import ChatType

from MukeshRobot import pbot
from MukeshRobot.utils.mongo import get_couple, save_couple





@pbot.on_message(filters.command(["couple", "couples"]))
async def couple(_, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘ.")
    
    try:
        chat_id = message.chat.id
        now = datetime.now()
        today = now.strftime("%d/%m/%Y")
        tomorrow = (now + timedelta(days=1)).strftime("%d/%m/%Y")

        is_selected = await get_couple(chat_id, today)
        if not is_selected:
            list_of_users = []
            async for i in pbot.get_chat_members(message.chat.id, limit=100):
                if not i.user.is_bot:
                    list_of_users.append(i.user.id)
            
            if len(list_of_users) < 2:
                return await message.reply_text("ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴜsᴇʀs ʜᴇʀᴇ (ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ 2).")
            
            c1_id = random.choice(list_of_users)
            c2_id = random.choice(list_of_users)
            while c1_id == c2_id:
                c1_id = random.choice(list_of_users)
            
            try:
                c1 = await pbot.get_users(c1_id)
                c2 = await pbot.get_users(c2_id)
                c1_mention = c1.mention
                c2_mention = c2.mention
            except Exception:
                c1_mention = f"<a href='tg://user?id={c1_id}'>User 1</a>"
                c2_mention = f"<a href='tg://user?id={c2_id}'>User 2</a>"

            couple_selection_message = f"""**ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :**

{c1_mention} + {c2_mention} = 💗
ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12 ᴀᴍ {tomorrow}"""
            await pbot.send_message(message.chat.id, text=couple_selection_message)
            
            couple_data = {"c1_id": c1_id, "c2_id": c2_id}
            await save_couple(chat_id, today, couple_data)

        else:
            c1_id = int(is_selected["c1_id"])
            c2_id = int(is_selected["c2_id"])
            
            try:
                c1 = await pbot.get_users(c1_id)
                c2 = await pbot.get_users(c2_id)
                c1_name = c1.mention
                c2_name = c2.mention
            except Exception:
                c1_name = f"<a href='tg://user?id={c1_id}'>User 1</a>"
                c2_name = f"<a href='tg://user?id={c2_id}'>User 2</a>"

            couple_selection_message = f"""ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :

{c1_name} + {c2_name} = 💗
ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12 ᴀᴍ {tomorrow}"""
            await pbot.send_message(message.chat.id, text=couple_selection_message)
    except Exception as e:
        print(f"Error in couples: {e}")
        await message.reply_text(f"ᴇʀʀᴏʀ: {e}")


__help__ = """
ᴄʜᴏᴏsᴇ ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ

 ❍ /couples *:* ᴄʜᴏᴏsᴇ 2 ᴜsᴇʀs ᴀɴᴅ sᴇɴᴅ ᴛʜᴇɪʀ ɴᴀᴍᴇ ᴀs ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ.
"""

__mod_name__ = "Cᴏᴜᴘʟᴇ"
