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

import os
import random
import requests
from urllib.parse import quote
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from groq import AsyncGroq
from .. import pbot as Dhruv, BOT_USERNAME

# Groq Client for Prompt Enhancement
groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

async def enhance_prompt(prompt):
    """Refines the user prompt into a high-quality descriptive prompt using Groq."""
    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a specialized prompt engineer for AI image generators (like Midjourney or Stable Diffusion). Your task is to expand the user's short prompt into a high-quality, detailed description. Include specifics about lighting, camera angle, texture, artistic style (e.g., cinematic, photorealistic, anime), and mood. Keep the output between 40-70 words. Respond ONLY with the refined prompt itself."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150,
        )
        enhanced = completion.choices[0].message.content.strip()
        return enhanced if enhanced and len(enhanced) > 5 else prompt
    except Exception as e:
        print(f"Prompt Enhancement Error: {e}")
        return prompt

async def download_image(url, save_path, is_json=False):
    """Helper to download image from direct URL or JSON response."""
    try:
        if is_json:
            response = requests.get(url, timeout=35)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("url")
                if image_url:
                    img_res = requests.get(image_url, timeout=35)
                    if img_res.status_code == 200:
                        with open(save_path, 'wb') as f:
                            f.write(img_res.content)
                        return True
        else:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=35)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
    except Exception as e:
        print(f"Download Error: {e}")
    return False

@Dhruv.on_message(filters.command(["imagine", "aiimage"]))
async def imagine_(b, message: Message):
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        await message.reply_text("✨ Please provide a prompt or reply to a message!\nExample: `/imagine a cyberpunk city`")
        return

    dhruv = await message.reply_text("`Refining your prompt and generating magic...` ✨")
    
    try:
        await b.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        
        # Phase 1: Enhance prompt using Groq for better results
        refined_prompt = await enhance_prompt(text)
        encoded_prompt = quote(refined_prompt)
        
        generated_path = f"waifu_{message.from_user.id}_{random.randint(100,999)}.jpg"
        success = False
        
        # Fallback Chain
        # 1. Pollinations (Fast and High Quality)
        seed = random.randint(1, 1000000)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1024&height=1024&nologo=True"
        if await download_image(pollinations_url, generated_path):
            success = True
        
        # 2. Hercai (Stable v3)
        if not success:
            hercai_url = f"https://hercai.onrender.com/v3/text2img?prompt={encoded_prompt}"
            if await download_image(hercai_url, generated_path, is_json=True):
                success = True

        # 3. Air Force (Imagine2 - simulated fallback via known direct API)
        if not success:
            # Note: Using another known free endpoint as final fallback if above fails
            pixazo_url = f"https://api.pixazo.ai/v1/stable-diffusion?prompt={encoded_prompt}"
            if await download_image(pixazo_url, generated_path):
                success = True

        if success:
            caption = f"""
💘 **sᴜᴄᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ !**

✨ **Prompt:** `{text}`
🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {message.from_user.mention}
🎉 **ᴘᴏᴡᴇʀᴇᴅ ʙʏ:** @{BOT_USERNAME}
"""
            await message.reply_photo(generated_path, caption=caption, quote=True)
            await dhruv.delete()
        else:
            await dhruv.edit_text("❌ All AI image servers are currently busy or down. Please try again later.")

    except Exception as e:
        await dhruv.edit_text(f"**Error during generation:** {e}")
    finally:
        if os.path.exists(generated_path):
            os.remove(generated_path)

__mod_name__ = "Aɪ ɪᴍᴀɢᴇ"
__help__ = """
  ❍ /imagine <ᴘʀᴏᴍᴘᴛ>*:* ɢᴇɴᴇʀᴀᴛᴇ ᴀɪ ɪᴍᴀɢᴇ ғʀᴏᴍ ᴛᴇxᴛ.
  ❍ /aiimage <ᴘʀᴏᴍᴘᴛ>*:* sᴀᴍᴇ ᴀs /ɪᴍᴀɢɪɴᴇ.
"""
