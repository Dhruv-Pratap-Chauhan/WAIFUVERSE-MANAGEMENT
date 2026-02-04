import random
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode

from MukeshRobot import pbot
from MukeshRobot.utils.mongo import get_couple, save_couple

# Constants for image generation
PFP_SIZE = (400, 400)
CANVAS_SIZE = (1000, 500)

async def generate_couple_image(c1_pfp_path, c2_pfp_path):
    # Create a dark background
    canvas = Image.new("RGB", CANVAS_SIZE, (15, 15, 15))
    
    # Load and resize PFPs
    try:
        p1 = Image.open(c1_pfp_path).convert("RGBA").resize(PFP_SIZE)
    except:
        p1 = Image.new("RGBA", PFP_SIZE, (100, 100, 100))
        
    try:
        p2 = Image.open(c2_pfp_path).convert("RGBA").resize(PFP_SIZE)
    except:
        p2 = Image.new("RGBA", PFP_SIZE, (100, 100, 100))

    # Paste PFPs
    canvas.paste(p1, (50, 50), p1)
    canvas.paste(p2, (550, 50), p2)

    # Draw a heart in the middle
    draw = ImageDraw.Draw(canvas)
    # Using a larger heart and pink color
    draw.text((470, 200), "💗", fill=(255, 105, 180)) 

    img_bin = BytesIO()
    canvas.save(img_bin, "JPEG")
    img_bin.seek(0)
    return img_bin

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
            async for i in pbot.get_chat_members(message.chat.id, limit=200):
                if not i.user.is_bot:
                    list_of_users.append(i.user)
            
            if len(list_of_users) < 2:
                return await message.reply_text("ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴜsᴇʀs ʜᴇʀᴇ (ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ 2).")
            
            c1_selected = random.choice(list_of_users)
            c2_selected = random.choice(list_of_users)
            while c1_selected.id == c2_selected.id:
                c1_selected = random.choice(list_of_users)
            
            # Fetch full user objects to ensure PFPs are accessible
            try:
                c1 = await pbot.get_users(c1_selected.id)
                c2 = await pbot.get_users(c2_selected.id)
            except Exception as e:
                print(f"Error fetching full user objects: {e}")
                c1, c2 = c1_selected, c2_selected

            bond = random.randint(1, 100)
            
            # Download PFPs
            p1_path = await pbot.download_media(c1.photo.big_file_id) if (c1 and hasattr(c1, 'photo') and c1.photo) else None
            p2_path = await pbot.download_media(c2.photo.big_file_id) if (c2 and hasattr(c2, 'photo') and c2.photo) else None
            
            img = await generate_couple_image(p1_path or "", p2_path or "")
            
            # Cleanup temp files
            if p1_path and os.path.exists(p1_path): os.remove(p1_path)
            if p2_path and os.path.exists(p2_path): os.remove(p2_path)

            caption = f"""<b>ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :</b> {today}
 
 {c1.mention} + {c2.mention} = 💗
 <b>ʙᴏɴᴅ :</b> {bond}%

 ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12 ᴀᴍ {tomorrow}"""
            
            await pbot.send_photo(message.chat.id, photo=img, caption=caption, parse_mode=ParseMode.HTML)
             
            couple_data = {"c1_id": c1.id, "c2_id": c2.id, "bond": bond}
            await save_couple(chat_id, today, couple_data)

        else:
            c1_id = int(is_selected["c1_id"])
            c2_id = int(is_selected["c2_id"])
            bond = is_selected.get("bond", random.randint(1, 100))
            
            try:
                c1 = await pbot.get_users(c1_id)
                c2 = await pbot.get_users(c2_id)
                c1_mention = c1.mention
                c2_mention = c2.mention
                
                p1_path = await pbot.download_media(c1.photo.big_file_id) if (c1 and hasattr(c1, 'photo') and c1.photo) else None
                p2_path = await pbot.download_media(c2.photo.big_file_id) if (c2 and hasattr(c2, 'photo') and c2.photo) else None
                img = await generate_couple_image(p1_path or "", p2_path or "")
                
                if p1_path and os.path.exists(p1_path): os.remove(p1_path)
                if p2_path and os.path.exists(p2_path): os.remove(p2_path)
                
            except Exception:
                c1_mention = f"<a href='tg://user?id={c1_id}'>User 1</a>"
                c2_mention = f"<a href='tg://user?id={c2_id}'>User 2</a>"
                img = await generate_couple_image("", "")

            caption = f"""<b>ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :</b> {today}
 
 {c1_mention} + {c2_mention} = 💗
 <b>ʙᴏɴᴅ :</b> {bond}%
 
 ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12 ᴀᴍ {tomorrow}"""
            
            await pbot.send_photo(message.chat.id, photo=img, caption=caption, parse_mode=ParseMode.HTML)

    except Exception as e:
        print(f"Error in couples: {e}")
        await message.reply_text(f"ᴇʀʀᴏʀ: {e}")


__help__ = """
ᴄʜᴏᴏsᴇ ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ

 ❍ /couples *:* ᴄʜᴏᴏsᴇ 2 ᴜsᴇʀs ᴀɴᴅ sᴇɴᴅ ᴛʜᴇɪʀ ɴᴀᴍᴇ ᴀs ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ.
"""

__mod_name__ = "Cᴏᴜᴘʟᴇ"
