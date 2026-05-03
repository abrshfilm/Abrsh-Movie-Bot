import os
import telebot
from telebot import types
import sqlite3
from flask import Flask
from threading import Thread

# --- 1. SERVER SETUP FOR RENDER/REPLIT ---
app = Flask(__name__)
@app.route('/')
def home(): 
    return "ABRSH BOT IS LIVE"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- 2. BOT CONFIGURATION ---
TOKEN = "8572682873:AAH5NW-kqxi_Lg1MLgEhmVODOe-B8NyuXeo"
ADMIN_ID = 7908276494 
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# --- 3. DATABASE ---
def get_db():
    conn = sqlite3.connect('abrsh_pro.db', check_same_thread=False)
    return conn

conn = get_db()
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 5.0, first_name TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS movies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_id TEXT, price REAL, category TEXT)')
conn.commit()

user_states = {}

# --- 4. MAIN KEYBOARD ---
def main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("※ ፊልም ልይ!", "※ ያለኝ ሂሳብ!")
    markup.row("※ ገቢ ላድርግ!", "※ ጎደኛዬን ልጋብዝ!")
    markup.row("※ አጠቃቀም!", "※ DM ABRSH!")
    return markup

# --- 5. START & WELCOME ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    fname = message.from_user.first_name
    
    # Register user
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, balance, first_name) VALUES (?, ?, ?)", (uid, 5.0, fname))
    conn.commit()

    # Image and Welcome Text
    photo_url = "https://i.ibb.co/nH5gRkz/IMG-20260405-155116-584.jpg"
    welcome_text = (
        "**※ ሰላም ይህ የ ABRSH Movies Bot ነው እንኳን በደህና መጡ!**\n\n"
        "**※ በትረጉም ፊልሞቻችን ይዝናኑ!**\n\n"
        "**※ ፊልም ልይ'ን ይጫኑ ና ደስታዎን ያስጀምሩ!**"
    )
    
    try:
        bot.send_photo(message.chat.id, photo_url, caption=welcome_text, reply_markup=main_markup())
    except:
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_markup())

    if uid == ADMIN_ID:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("📊 Bot Statics", callback_data="adm_stats"),
            types.InlineKeyboardButton("📂 Upload Movies", callback_data="adm_upload"),
            types.InlineKeyboardButton("⚙️ Edit Movies", callback_data="adm_edit")
        )
        bot.send_message(message.chat.id, "🛠 **Admin Control Panel:**", reply_markup=kb)

# --- 6. MOVIE SEARCH (PROFESSIONAL BUTTON STYLE) ---
@bot.message_handler(func=lambda m: m.text == "※ ፊልም ልይ!")
def search_init(m):
    msg = bot.send_message(m.chat.id, "**⨳ የሚፈልጉትን ፊልም ስም ይፃፉ!**")
    bot.register_next_step_handler(msg, search_process)

def search_process(m):
    query = m.text
    res = conn.execute("SELECT id, name, price, category FROM movies WHERE name LIKE ?", (f'%{query}%',)).fetchall()
    
    if not res:
        bot.send_message(m.chat.id, "**⨳ በዚ ስም የተሰየመ ፊልም ማግኘት አልቻልኩም!**\n"
                                     "**⨳ ፊደል ተሳስተው እንዳይሆን ያረጋግጡ!**")
        return
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    for row in res[:10]:
        # እንደ ቴሌብር በተን ስሙ እና ዋጋው አብሮ ይመጣል
        btn_text = f"🎬 {row[1]} | {row[3]} | {row[2]} ETB"
        kb.add(types.InlineKeyboardButton(btn_text, callback_data=f"buy_{row[0]}"))
    
    bot.send_message(m.chat.id, f"**🔍 ለ '{query}' የተገኙ ውጤቶች፦**", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def finalize_purchase(call):
    mid = call.data.split("_")[1]
    mov = conn.execute("SELECT name, file_id, price FROM movies WHERE id=?", (mid,)).fetchone()
    usr = conn.execute("SELECT balance FROM users WHERE user_id=?", (call.from_user.id,)).fetchone()
    
    if usr and usr[0] >= mov[2]:
        new_bal = usr[0] - mov[2]
        conn.execute("UPDATE users SET balance=? WHERE user_id=?", (new_bal, call.from_user.id))
        conn.commit()
        bot.send_video(call.message.chat.id, mov[1], caption=f"**🎬 {mov[0]}**\n**💰 ቀሪ ሂሳብ፦ {new_bal} ብር**")
    else:
        bot.answer_callback_query(call.id, "❌ በቂ ሂሳብ የለዎትም! እባክዎ ገቢ ያድርጉ።", show_alert=True)

# --- 7. DEPOSIT (EXACT MESSAGE & FLOW) ---
@bot.message_handler(func=lambda m: m.text == "※ ገቢ ላድርግ!")
def deposit_start(m):
    txt = (
        "**⨳ ገቢ የሚያደርጉበት መንገድ ቴሌብር ነው!**\n\n"
        "**በዚህ +251961343796 ስልክ ቁጥር ከ5 ብር ጀምሮ በማስገባት Screen Shoot ላኩ።**"
    )
    bot.send_message(m.chat.id, txt)

@bot.message_handler(content_types=['photo'])
def handle_receipt(m):
    # አድሚኑ ጋር Accept/Reject እንዲሄድ
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("✅ Accept", callback_data=f"acc_{m.from_user.id}"),
           types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{m.from_user.id}"))
    
    bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
    bot.send_message(ADMIN_ID, f"**💰 የክፍያ ጥያቄ ከ፦ {m.from_user.first_name}\nID: `{m.from_user.id}`**", reply_markup=kb)
    bot.send_message(m.chat.id, "**⏳ ስክሪንሹቱ ተልኳል፣ አድሚኑ እስኪያረጋግጥ ይጠብቁ።**")

@bot.callback_query_handler(func=lambda c: c.data.startswith(("acc_", "rej_")))
def admin_approval(call):
    action, uid = call.data.split("_")
    if action == "acc":
        msg = bot.send_message(ADMIN_ID, f"**ለተጠቃሚው (ID: {uid}) የሚገባውን የብር መጠን በቁጥር ብቻ ይላኩ፦**")
        bot.register_next_step_handler(msg, lambda m: deposit_confirm(m, uid))
    else:
        usr = conn.execute("SELECT first_name FROM users WHERE user_id=?", (uid,)).fetchone()
        bot.send_message(uid, f"**ውድ {usr[0] if usr else ''} ጥያቄዎ አልተሳካም❎**")
        bot.answer_callback_query(call.id, "ውድቅ ተደርጓል")

def deposit_confirm(m, uid):
    try:
        amount = float(m.text)
        current = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()[0]
        conn.execute("UPDATE users SET balance=? WHERE user_id=?", (current + amount, uid))
        conn.commit()
        bot.send_message(uid, f"**✅ ውድ ተጠቃሚ {amount} ብር በካውንትዎ ላይ ተጨምሯል!**")
        bot.send_message(ADMIN_ID, f"**✅ በተሳካ ሁኔታ {amount} ብር ለ {uid} ገብቷል።**")
    except:
        bot.send_message(ADMIN_ID, "❌ ስህተት! እባክዎ ቁጥር ብቻ ይላኩ።")

# --- 8. ADMIN TOOLS (UPLOAD/EDIT) ---
@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def admin_actions(call):
    if call.data == "adm_stats":
        u = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        m = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        bot.answer_callback_query(call.id, f"Users: {u} | Movies: {m}", show_alert=True)
    
    elif call.data == "adm_upload":
        msg = bot.send_message(ADMIN_ID, "**📂 ቪዲዮውን ይላኩ (Caption ላይ ስሙን ይጻፉ)...**")
        bot.register_next_step_handler(msg, movie_save_start)
    
    elif call.data == "adm_edit":
        movies = conn.execute("SELECT id, name FROM movies ORDER BY id DESC LIMIT 15").fetchall()
        kb = types.InlineKeyboardMarkup()
        for mid, name in movies:
            kb.add(types.InlineKeyboardButton(f"🎬 {name}", callback_data=f"editopt_{mid}"))
        bot.send_message(ADMIN_ID, "**⚙️ ማስተካከል የሚፈልጉትን ፊልም ይምረጡ፦**", reply_markup=kb)

def movie_save_start(m):
    if not (m.video or m.document): return
    fid = m.video.file_id if m.video else m.document.file_id
    name = m.caption if m.caption else "ያልተሰየመ"
    user_states[ADMIN_ID] = {'fid': fid, 'name': name}
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    opts = [("⚫️", 0.5), ("🟢", 0.5), ("🟡", 0.3), ("🔴", 1.0), ("🔵", 0.5), ("⚪️", 5.0)]
    for icon, price in opts:
        kb.insert(types.InlineKeyboardButton(f"{icon} {price} ETB", callback_data=f"sv_{icon}_{price}"))
    bot.send_message(ADMIN_ID, "**የፊልሙን አይነት እና ዋጋ ይምረጡ፦**", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("sv_"))
def movie_save_final(call):
    _, icon, prc = call.data.split("_")
    d = user_states.get(ADMIN_ID)
    if d:
        conn.execute("INSERT INTO movies (name, file_id, price, category) VALUES (?,?,?,?)", (d['name'], d['fid'], float(prc), icon))
        conn.commit()
        bot.edit_message_text(f"**✅ {d['name']} ተጭኗል።**", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("editopt_"))
def edit_logic(call):
    mid = call.data.split("_")[1]
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("💰 ዋጋ ቀይር", callback_data=f"uprc_{mid}"),
           types.InlineKeyboardButton("❌ አጥፋ", callback_data=f"del_{mid}"))
    bot.edit_message_text("**ምን ለማድረግ ይፈልጋሉ?**", call.message.chat.id, call.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith(("uprc_", "del_")))
def final_edit(call):
    action, mid = call.data.split("_")
    if action == "del":
        conn.execute("DELETE FROM movies WHERE id=?", (mid,))
        conn.commit()
        bot.answer_callback_query(call.id, "ተሰርዟል!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif action == "uprc":
        msg = bot.send_message(ADMIN_ID, "**አዲሱን ዋጋ ይላኩ፦**")
        bot.register_next_step_handler(msg, lambda m: update_price_db(m, mid))

def update_price_db(m, mid):
    try:
        p = float(m.text)
        conn.execute("UPDATE movies SET price=? WHERE id=?", (p, mid))
        conn.commit()
        bot.send_message(ADMIN_ID, "**✅ ዋጋው ተቀይሯል።**")
    except: pass

# --- 9. OTHER COMMANDS ---
@bot.message_handler(func=lambda m: m.text == "※ ያለኝ ሂሳብ!")
def my_balance(m):
    res = conn.execute("SELECT balance FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    bot.send_message(m.chat.id, f"**⨳ ቀሪ ሂሳብ ~> {res[0] if res else 0.0} ብር**")

@bot.message_handler(func=lambda m: m.text == "※ አጠቃቀም!")
def how_to(m):
    txt = (
        "**🧶 የICON ከለሮች ትርጉም።**\n"
        "**\">\">\">\">\">\">\">\">**\n"
        "**⚫️ -> ትርጉም ተከታታይ እና ሲንግል!**\n"
        "**🟢 -> ሲንግል!**\n"
        "**🟡 -> ተከታታይ ትርጉም!**\n"
        "**🔴 -> ሮማንስ ያለ ትርጉም!**\n"
        "**🔵 -> አማርኛ!**\n"
        "**🟣 -> ተከታታይ አማርኛ!**\n"
        "**🟠 -> ቃና ፊልሞች!**\n"
        "**⚪️ -> መፅሀፍት!**\n"
        "**\">\">\">\">\">\">\">\">**\n"
        "**💵 የፊልሞች ዋጋ**\n"
        "**💰ሲንግል -> 0.5 ብር።**\n"
        "**💰ተከታታይ -> 0.3 ብር።**\n"
        "**💰አማርኛ -> 0.5 ብር።**\n"
        "**💰ኢሮቲክ -> 1 ብር።**\n"
        "**💰ተከታታይ አማርኛ -> 0.5 ብር።**\n"
        "**💰ቃና -> 0.3 ብር።**\n"
        "**💰መፅሀፍ -> 5 ብር።**\n"
        "**\">\">\">\">\">\">\">\">**\n"
        "**✅ @ABRSHFILMBET**"
    )
    bot.send_message(m.chat.id, txt)

@bot.message_handler(func=lambda m: m.text == "※ ጎደኛዬን ልጋብዝ!")
def referral(m):
    link = f"https://t.me/ABRSHMovies_Bot?start=ref{m.from_user.id}"
    bot.send_message(m.chat.id, f"**ጓደኞችዎን ይጋብዙ ና ሽልማቶች ያግኙ! 🎉**\n\n**1 ሰው ሲጋብዙ > 0.7 ብር ያገኛሉ!**\n\n**ሊንክ፦ {link}**")

@bot.message_handler(func=lambda m: m.text == "※ DM ABRSH!")
def dm_abrsh(m):
    bot.send_message(m.chat.id, "**የዚህ ቦት Owner👉 @ABRSHFILMBET**")

# --- 10. RUN ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
