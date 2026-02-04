"""MIT License

Copyright (c) 2023-24 Noob-Mukesh

          GITHUB: NOOB-MUKESH
          TELEGRAM: @MR_SUKKUN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
from pyrogram import filters
from pyrogram.types import  Message
from pyrogram.types import InputMediaPhoto
from .. import pbot as  Dhruv,BOT_USERNAME
import requests
from pyrogram.enums import ChatAction,ParseMode

@Dhruv.on_message(filters.command("imagine"))
async def imagine_(b, message: Message):
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:

        text =message.text.split(None, 1)[1]
    dhruv=await message.reply_text( "`Please wait...,\n\nGenerating prompt .. ...`")
    try:
        await b.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        
        from urllib.parse import quote
        import random
        encoded_prompt = quote(text)
        
        generated_path = "waifuverse_image.jpg"
        success = False
        
        # Method 1: Pollinations (High Quality)
        try:
            seed = random.randint(1, 1000000)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1024&height=1024&nologo=True"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=30)
            # Pollinations returns binary image directly
            if response.status_code == 200:
                with open(generated_path, 'wb') as f:
                    f.write(response.content)
                success = True
        except Exception as e:
            print(f"Pollinations Error: {e}")

        # Method 2: Hercai (Stable Fallback)
        if not success:
            try:
                # Hercai v3 Stable
                url = f"https://hercai.onrender.com/v3/text2img?prompt={encoded_prompt}"
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("url")
                    if image_url:
                        img_res = requests.get(image_url, timeout=30)
                        with open(generated_path, 'wb') as f:
                            f.write(img_res.content)
                        success = True
            except Exception as e:
                print(f"Hercai Error: {e}")

        if success:
            caption = f"""
💘 sᴜᴄᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ !
✨ ᴘʀᴏᴍᴘᴛ: {text}
🥀 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ: {message.from_user.mention}
"""
            await message.reply_photo(generated_path, caption=caption, quote=True)
            await dhruv.delete()
            if os.path.exists(generated_path):
                os.remove(generated_path)
        else:
            await dhruv.edit_text("❌ All AI image servers are currently busy or down. Please try again in a few minutes.")

    except Exception as e:
        await dhruv.edit_text(f"Error: {e}")
    
# -----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
__mod_name__ = "Aɪ ɪᴍᴀɢᴇ"
__help__ = """
 ❍ /imagine <ᴘʀᴏᴍᴘᴛ>*:* ɢᴇɴᴇʀᴀᴛᴇ ᴀɪ ɪᴍᴀɢᴇ ғʀᴏᴍ ᴛᴇxᴛ.
 ❍ /aiimage <ᴘʀᴏᴍᴘᴛ>*:* sᴀᴍᴇ ᴀs /ɪᴍᴀɢɪɴᴇ.
"""
