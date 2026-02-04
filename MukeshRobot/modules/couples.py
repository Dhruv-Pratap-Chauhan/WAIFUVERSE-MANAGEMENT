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
    canvas = Image.new("RGB", CANVAS_SIZE, (18, 18, 18))
    
    def get_pfp(path):
        try:
            if path and os.path.exists(path):
                img = Image.open(path).convert("RGBA").resize(PFP_SIZE)
                return img
        except:
            pass
        # High-quality Placeholder
        img = Image.new("RGBA", PFP_SIZE, (50, 50, 50))
        return img

    p1 = get_pfp(c1_pfp_path)
    p2 = get_pfp(c2_pfp_path)

    # Paste PFPs
    canvas.paste(p1, (50, 50), p1)
    canvas.paste(p2, (550, 50), p2)

    # DRAW A LARGE PREMIUM HEART IN THE MIDDLE
    draw = ImageDraw.Draw(canvas, "RGBA")
    
    # Custom Heart Drawing Logic (Vector style)
    def draw_heart(draw, x, y, size, fill):
        # Two circles
        radius = size // 2
        draw.ellipse([x - size, y - size, x, y], fill=fill) # Left
        draw.ellipse([x, y - size, x + size, y], fill=fill) # Right
        # Triangle bottom
        draw.polygon([(x - size, y - radius//2), (x + size, y - radius//2), (x, y + size)], fill=fill)

    # Vivid Pink Heart
    draw_heart(draw, 500, 230, 90, (255, 51, 153, 255))

    img_bin = BytesIO()
    canvas.save(img_bin, "JPEG", quality=100)
    img_bin.seek(0)
    return img_bin

async def resolve_user(chat_id, user_id):
    """Reliably fetch a fresh user object"""
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        if member and member.user:
            return member.user
    except:
        try:
            return await pbot.get_users(user_id)
        except:
            return None
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
            # Step 1: Scan members (Filter Bots & Deleted accounts)
            list_of_users = []
            async for member in pbot.get_chat_members(chat_id, limit=300):
                u = member.user
                if not u.is_bot and not u.is_deleted:
                    # Filter generic "Deleted Account" names just in case
                    if u.first_name and "Deleted Account" not in u.first_name:
                        list_of_users.append(u)
            
            if len(list_of_users) < 2:
                return await status_msg.edit("ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴀᴄᴛɪᴠᴇ ᴜsᴇʀs ʜᴇʀᴇ (ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ 2).")
            
            # Step 2: Randomly Select
            c1_selected = random.choice(list_of_users)
            c2_selected = random.choice(list_of_users)
            while c1_selected.id == c2_selected.id:
                c2_selected = random.choice(list_of_users)
            
            bond = random.randint(30, 100)
            
            # Step 3: Ensure data is fresh
            c1 = await resolve_user(chat_id, c1_selected.id) or c1_selected
            c2 = await resolve_user(chat_id, c2_selected.id) or c2_selected

            p1_path = await pbot.download_media(c1.photo.big_file_id) if (c1 and getattr(c1, "photo", None)) else None
            p2_path = await pbot.download_media(c2.photo.big_file_id) if (c2 and getattr(c2, "photo", None)) else None
            
            img = await generate_couple_image(p1_path, p2_path)
            
            if p1_path and os.path.exists(p1_path): os.remove(p1_path)
            if p2_path and os.path.exists(p2_path): os.remove(p2_path)

            caption = f"""<b>ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ :</b> {today}
 
 {c1.mention} + {c2.mention} = 💗
 <b>ʙᴏɴᴅ :</b> {bond}%

 ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12 ᴀᴍ {tomorrow}"""
            
            await status_msg.delete()
            await pbot.send_photo(chat_id, photo=img, caption=caption, parse_mode=ParseMode.HTML)
             
            couple_data = {"c1_id": c1.id, "c2_id": c2.id, "bond": bond}
            await save_couple(chat_id, today, couple_data)

        else:
            # Re-fetch from stored IDs
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
