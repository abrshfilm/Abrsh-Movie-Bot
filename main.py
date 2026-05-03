Act as an Expert Python Developer specializing in the `pyTelegramBotAPI` (Telebot) library. I want you to write a complete, fully functional, and bug-free Telegram bot script (`main.py`) for a movie distribution bot. 

### 1. Bot Setup & Infrastructure
* **Token**: `8572682873:AAH5NW-kqxi_Lg1MLgEhmVODOe-B8NyuXeo`
* **Admin ID**: `7908276494`
* **Database**: Use `sqlite3`. Create a database named `abrsh.db` with two tables:
  1. `users`: `user_id` (INTEGER PRIMARY KEY), `balance` (REAL, default 5.0), `first_name` (TEXT).
  2. `movies`: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `name` (TEXT), `file_id` (TEXT), `price` (REAL), `category` (TEXT).
* **Keep-Alive**: Include a basic Flask server and threading to keep the bot alive on Replit.
* **Parse Mode**: Always use `parse_mode="Markdown"` when sending messages to render bold text.

### 2. Main Keyboard Menu & Welcome Photo
When a user sends `/start`, register them in the DB (give 5.0 ETB default).
Send them a photo using `bot.send_photo()`. The photo URL is `https://i.ibb.co/nH5gRkz/IMG-20260405-155116-584.jpg`.
Set the caption to this EXACT welcome message (the markdown `**` makes it fully bold):
"**※ ሰላም ይህ የ ABRSH Movies Bot ነው እንኳን በደህና መጡ!**\n\n**※ በትረጉም ፊልሞቻችን ይዝናኑ!**\n\n**※ ፊልም ልይ'ን ይጫኑ ና ደስታዎን ያስጀምሩ!**"

Attach a `ReplyKeyboardMarkup` to this photo message with 3 rows (2 buttons per row):
Row 1: [※ ፊልም ልይ!] [※ ያለኝ ሂሳብ!]
Row 2: [※ ገቢ ላድርግ!] [※ ጎደኛዬን ልጋብዝ!]
Row 3: [※ አጠቃቀም!] [※ DM ABRSH!]

### 3. Admin Control Panel (Strictly for Admin ID)
If the user ID matches the Admin ID during `/start`, send an additional message: "🛠 **Admin Control Panel:**" with an `InlineKeyboardMarkup` containing 3 vertical buttons:
1. **📊 Bot Statics**: On click, show total user count and movie count in an alert popup.
2. **📂 Upload Movies**: On click, ask the admin to send a video/document with the movie name in the caption. Use `register_next_step_handler`. Once received, show inline buttons for categories/prices (e.g., ⚫️ 0.5, 🟢 0.5, 🟡 0.3, 🔴 1.0, 🔵 0.5, ⚪️ 5.0). Save the selected data to the `movies` table.
3. **⚙️ Edit Movies**: On click, fetch the last 10 movies from the DB and display them as inline buttons. If the admin clicks a movie, give two options: [💰 ዋጋ ቀይር] (Edit Price) and [❌ አጥፋ] (Delete). Allow deleting from DB or updating the price using `register_next_step_handler`.

### 4. Deposit & Payment Approval Flow (Accept/Reject)
* When user clicks **"※ ገቢ ላድርግ!"**, reply EXACTLY:
  "**⨳ ገቢ የሚያደርጉበት መንገድ ቴሌብር ነው!**\n\n**በዚህ +251961343796 ስልክ ቁጥር ከ5 ብር ጀምሮ በማስገባት Screen Shoot ላኩ።**"
* **Screenshot Handler**: If a user sends a photo (screenshot), forward it to the Admin ID. Add inline buttons under the photo for the Admin: [✅ Accept] and [❌ Reject]. Reply to the user: "**⏳ ስክሪንሹቱ ተልኳል፣ አድሚኑ እስኪያረጋግጥ ይጠብቁ።**"
* **Admin Accepts**: If Admin clicks Accept, bot asks the admin: "ስንት ብር ይግባለት?". Admin types the amount (e.g., 10). Update the user's balance in DB and send the user: "**✅ ውድ ተጠቃሚ {amount} ብር በካውንትዎ ላይ ተጨምሯል!**"
* **Admin Rejects**: If Admin clicks Reject, send the user EXACTLY: "**ውድ {first_name} ጥያቄዎ አልተሳካም❎**"

### 5. Exact User Commands & Responses
You MUST use these EXACT Amharic strings without changing a single character. All replies must be bolded using Markdown.

* **"※ ፊልም ልይ!"**:
  Ask: "**⨳ የሚፈልጉትን ፊልም ስም ይፃፉ!**"
  Search the DB using `LIKE`. If found, list movies as inline buttons (e.g., `🎬 {name} - {price} ብር`). If clicked, check user balance. If balance is sufficient, deduct price and send the video. If not, alert: "❌ በቂ ሂሳብ የለዎትም!"
  IF MOVIE NOT FOUND, reply EXACTLY:
  "**⨳ በዚ ስም የተሰየመ ፊልም ማግኘት አልቻልኩም!**
**⨳ ፊደል ተሳስተው እንዳይሆን ያረጋግጡ!**"

* **"※ ያለኝ ሂሳብ!"**:
  Reply EXACTLY: "**⨳ ቀሪ ሂሳብ ~> {balance} ብር**"

* **"※ ጎደኛዬን ልጋብዝ!"**:
  Reply EXACTLY:
  "**ጓደኞችዎን ይጋብዙ ና ሽልማቶች ያግኙ! 🎉**

**የአብርሽን ፊልሞች እየኮመኮሙ እንዲደሰቱ ጓደኞችዎን ይጋብዙ!**

**1 ሰው ሲጋብዙ > 0.7 ብር ያገኛሉ!**
**ከታች ያለውን ልዩ የግብዣ ሊንክዎን ለጓደኞችዎ ያጋሩ ።**

**https://t.me/ABRSHMovies_Bot?start=ref{user_id}**"

* **"※ DM ABRSH!"**:
  Reply EXACTLY: "**የዚህ ቦት Owner👉 @ABRSHFILMBET**"

* **"※ አጠቃቀም!"**:
  Reply EXACTLY with this formatted list:
**🧶 የICON ከለሮች ትርጉም።**
**">">">">">">">">**
**⚫️ -> ትርጉም ተከታታይ እና ሲንግል!**
**🟢 -> ሲንግል!**
**🟡 -> ተከታታይ ትርጉም!**
**🔴 -> ሮማንስ ያለ ትርጉም!**
**🔵 -> አማርኛ!**
**🟣 -> ተከታታይ አማርኛ!**
**🟠 -> ቃና ፊልሞች!**
**⚪️ -> መፅሀፍት!**
**">">">">">">">">**
**💵 የፊልሞች ዋጋ**
**💰ሲንግል -> 0.5 ብር።**
**💰ተከታታይ -> 0.3 ብር።**
**💰አማርኛ -> 0.5 ብር።**
**💰ኢሮቲክ -> 1 ብር።**
**💰ተከታታይ አማርኛ -> 0.5 ብር።**
**💰ቃና -> 0.3 ብር።**
**💰መፅሀፍ -> 5 ብር።**
**">">">">">">">">**
**✅ @ABRSHFILMBET**

Write the entire code cleanly in one block. Do not leave placeholders. Implement all `register_next_step_handler` flows correctly.
