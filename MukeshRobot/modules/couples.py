import random
import os
import traceback
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from io import BytesIO

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import PeerIdInvalid, UserNotParticipant

from MukeshRobot import pbot
from MukeshRobot.utils.mongo import get_couple, save_couple

# Constants for image generation
PFP_SIZE = (400, 400)
CANVAS_SIZE = (1000, 500)

async def generate_couple_image(c1_pfp_path, c2_pfp_path):
    # Create a sleek semi-dark background
    canvas = Image.new("RGB", CANVAS_SIZE, (20, 20, 20))
    
    def get_pfp(path):
        try:
            if path and os.path.exists(path):
                img = Image.open(path).convert("RGBA").resize(PFP_SIZE)
                return img
        except Exception as e:
            print(f"PFP Load Error: {e}")
        # High-quality Placeholder (Pink-ish Gray)
        img = Image.new("RGBA", PFP_SIZE, (60, 50, 60))
        return img

    p1 = get_pfp(c1_pfp_path)
    p2 = get_pfp(c2_pfp_path)

    # Paste PFPs
    canvas.paste(p1, (50, 50), p1)
    canvas.paste(p2, (550, 50), p2)

    # DRAW A LARGE PREMIUM HEART IN THE MIDDLE
    draw = ImageDraw.Draw(canvas, "RGBA")
    
    def draw_heart(draw, x, y, size):
        # We'll use a larger size and a better pink
        # Bottom Triangle
        draw.polygon([(x - size, y), (x + size, y), (x, y + size)], fill=(255, 20, 147, 255))
        # Top two circles
        radius = size
        draw.ellipse([x - size, y - size, x, y + 20], fill=(255, 20, 147, 255))
        draw.ellipse([x, y - size, x + size, y + 20], fill=(255, 20, 147, 255))

    # Center is 500, 250. Let's place heart there.
    draw_heart(draw, 500, 200, 100) 

    img_bin = BytesIO()
    canvas.save(img_bin, "JPEG", quality=100)
    img_bin.seek(0)
    return img_bin

async def resolve_user(chat_id, user_id):
    """Reliably fetch a fresh user object"""
    try:
        # Prioritize get_users as it usually has the full object if indexed
        return await pbot.get_users(user_id)
    except:
        try:
            member = await pbot.get_chat_member(chat_id, user_id)
            return member.user
        except:
            return None

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
            status_msg = await message.reply_text("🔍 ꜱᴄᴀɴɴɪɴɢ ᴄʜᴀᴛ ꜰᴏʀ ᴄᴏᴜᴘʟᴇꜱ...")
            # Step 1: Scan members
            list_of_users = []
            async for member in pbot.get_chat_members(chat_id, limit=300):
                u = member.user
                if not u.is_bot and not u.is_deleted and u.first_name:
                    list_of_users.append(u)
            
            if len(list_of_users) < 2:
                return await status_msg.edit("ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴀᴄᴛɪᴠᴇ ᴜsᴇʀs ʜᴇʀᴇ.")
            
            # Step 2: Randomly Select
            c1_selected = random.choice(list_of_users)
            c2_selected = random.choice(list_of_users)
            while c1_selected.id == c2_selected.id:
                c2_selected = random.choice(list_of_users)
            
            bond = random.randint(30, 100)
            
            # Step 3: PFP Fetching
            p1_path = await pbot.download_media(c1_selected.photo.big_file_id) if (c1_selected and getattr(c1_selected, "photo", None)) else None
            p2_path = await pbot.download_media(c2_selected.photo.big_file_id) if (c2_selected and getattr(c2_selected, "photo", None)) else None
            
            img = await generate_couple_image(p1_path, p2_path)
            
            if p1_path and os.path.exists(p1_path): os.remove(p1_path)
            if p2_path and os.path.exists(p2_path): os.remove(p2_path)

            caption = f"""<b>ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ :</b> {today}
 
 {c1_selected.mention} + {c2_selected.mention} = 💗
 <b>ʙᴏɴᴅ :</b> {bond}%

 ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12 ᴀᴍ {tomorrow}"""
            
            await status_msg.delete()
            await pbot.send_photo(chat_id, photo=img, caption=caption, parse_mode=ParseMode.HTML)
             
            couple_data = {"c1_id": c1_selected.id, "c2_id": c2_selected.id, "bond": bond}
            await save_couple(chat_id, today, couple_data)

        else:
            c1_id = int(is_selected["c1_id"])
            c2_id = int(is_selected["c2_id"])
            bond = is_selected.get("bond", random.randint(60, 100))
            
            c1 = await resolve_user(chat_id, c1_id)
            c2 = await resolve_user(chat_id, c2_id)
            
            c1_mention = c1.mention if c1 else f"<a href='tg://user?id={c1_id}'>User 1</a>"
            c2_mention = c2.mention if c2 else f"<a href='tg://user?id={c2_id}'>User 2</a>"
            
            p1_path = await pbot.download_media(c1.photo.big_file_id) if (c1 and getattr(c1, "photo", None)) else None
            p2_path = await pbot.download_media(c2.photo.big_file_id) if (c2 and getattr(c2, "photo", None)) else None
            
            img = await generate_couple_image(p1_path, p2_path)
            
            if p1_path and os.path.exists(p1_path): os.remove(p1_path)
            if p2_path and os.path.exists(p2_path): os.remove(p2_path)

            caption = f"""<b>ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ :</b> {today}
 
 {c1_mention} + {c2_mention} = 💗
 <b>ʙᴏɴᴅ :</b> {bond}%
 
 ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12 ᴀᴍ {tomorrow}"""
            
            await pbot.send_photo(chat_id, photo=img, caption=caption, parse_mode=ParseMode.HTML)

    except Exception as e:
        print(f"Error in couples: {e}")
        traceback.print_exc()
        await message.reply_text(f"ᴇʀʀᴏʀ: {e}")

__help__ = """
ᴄʜᴏᴏsᴇ ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ

 ❍ /couples *:* ᴄʜᴏᴏsᴇ 2 ᴜsᴇʀs ᴀɴᴅ sᴇɴᴅ ᴛʜᴇɪʀ ɴᴀᴍᴇ ᴀs ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ.
"""

__mod_name__ = "Cᴏᴜᴘʟᴇ"
