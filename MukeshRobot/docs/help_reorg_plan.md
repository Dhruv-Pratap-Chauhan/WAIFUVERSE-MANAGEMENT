# Help Menu Reorganization Plan

This plan aims to reorganize the bot's help menu into logical categories, ensuring that all modules are accounted for and that group management is separated from other features like games or AI tools.

## Proposed Categories

1.  **📕 Management**: Core group management features.
2.  **🎯 Toyz**: Fun, games, and entertainment modules.
3.  **🤖 AI-Lab**: Artificial Intelligence features (ChatGPT, Image generation).
4.  **🏮 Anime**: Anime-related commands (Quotes, info).
5.  **💡 Tools**: Utility tools (Currency converter, carbon, etc.)
6.  **💁 Basic**: Fundamental commands (Info, settings, start, etc.)

## Module Assignment Matrix

### 📕 Management (Group Admin Focused)
- admin
- bans
- muting
- locks
- welcome
- reporting
- log_channel
- blacklist
- cust_filters
- flood
- approve
- cleaner
- notes
- rules
- zombies
- antiban
- blacklist_stickers
- nightmode
- unbanall
- purge
- tagall
- blacklistusers
- connection
- disable

### 🎯 Toyz (Games & Fun)
- fun
- dicegame
- truth_dare
- animation
- couples
- sexy
- shayri

### 🤖 AI-Lab (AI Tools)
- aiimage
- chatgpt

### 🏮 Anime (Anime Related)
- anime
- animez

### 💡 Tools (Utility)
- cash
- country
- carbon
- currency_converter
- gettime
- gitinfo
- google
- gps
- hastaggen
- json
- memify
- paste
- phone
- qrcode
- quotly
- reactions
- revel
- sed
- speed_test
- telegraph
- translator
- ud
- urlshortner
- wallpaper
- weather
- webss
- writetool
- zip

### 💁 Basic (Fixed/Hardcoded in UI)
- info (userinfo)
- settings
- reload
- staff

## Technical Approach

1.  **Update `MGMT_MODULES`, `FUN_MODULES`, `AI_MODULES`, `ANIME_MODULES`** in `__main__.py` to reflect the above list.
2.  **Refine the `help_button` logic** to ensure that any module NOT in the above explicit lists defaults to the **Tools** category, ensuring 100% coverage.
3.  **Clean up the `MukeshRobot_Main_Callback`** to remove old hardcoded strings and link everything to the dynamic categorization system.
4.  **Fix UI display issues** (like the broken lantern emoji).
