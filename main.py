import os
import telebot
from telebot import types
import sqlite3
from flask import Flask
from threading import Thread

# --- 1. SERVER SETUP ---
app = Flask(__name__)
@app.route('/')
def home(): return "ABRSH BOT IS ALIVE"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- 2. BOT CONFIG ---
TOKEN = "8572682873:AAH5NW-kqxi_Lg1MLgEhmVODOe-B8NyuXeo"
ADMIN_ID = 7908276494 
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# --- 3. DATABASE ---
def get_db():
    conn = sqlite3.connect('abrsh_final_pro.db', check_same_thread=False)
    return conn

conn = get_db()
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 5.0, first_name TEXT, referred_by INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS movies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_id TEXT, price REAL, category TEXT)')
conn.commit()

user_states = {}

# --- 4. KEYBOARDS ---
def main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("※ ፊልም ልይ!", "※ ያለኝ ሂሳብ!")
    markup.row("※ ገቢ ላድርግ!", "※ ጎደኛዬን ልጋብዝ!")
    markup.row("※ አጠቃቀም!", "※ DM ABRSH!")
    return markup

# --- 5. START & REFERRAL SYSTEM ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    fname = message.from_user.first_name
    args = message.text.split()
    
    c = conn.cursor()
    user_exists = c.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,)).fetchone()
    
    if not user_exists:
        referrer = None
        if len(args) > 1 and args[1].startswith('ref'):
            try:
                referrer = int(args[1].replace('ref', ''))
                if referrer != uid:
                    # ለጋባዡ 0.7 ብር መጋበዝ
                    ref_data = c.execute("SELECT balance FROM users WHERE user_id = ?", (referrer,)).fetchone()
                    if ref_data:
                        new_ref_bal = ref_data[0] + 0.7
                        c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_ref_bal, referrer))
                        bot.send_message(referrer, f"**🎉 አዲስ ሰው ጋብዘዋል! 0.7 ብር ወደ ሂሳብዎ ተጨምሯል።**")
            except: pass
        
        c.execute("INSERT INTO users (user_id, balance, first_name, referred_by) VALUES (?, ?, ?, ?)", (uid, 5.0, fname, referrer))
        conn.commit()

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
        kb.add(types.InlineKeyboardButton("📊 Bot Statics", callback_data="adm_stats"),
               types.InlineKeyboardButton("📂 Upload Movies", callback_data="adm_upload"),
               types.InlineKeyboardButton("⚙️ Edit Movies", callback_data="adm_edit"))
        bot.send_message(message.chat.id, "🛠 **Admin Control Panel:**", reply_markup=kb)

# --- 6. BUTTONS LOGIC ---
@bot.message_handler(func=lambda m: True)
def handle_buttons(m):
    if m.text == "※ ፊልም ልይ!":
        msg = bot.send_message(m.chat.id, "**⨳ የሚፈልጉትን ፊልም ስም ይፃፉ!**")
        bot.register_next_step_handler(msg, search_movie)
    
    elif m.text == "※ ያለኝ ሂሳብ!":
        res = conn.execute("SELECT balance FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
        bot.send_message(m.chat.id, f"**⨳ ቀሪ ሂሳብ ~> {res[0] if res else 0.0} ብር**")
    
    elif m.text == "※ ገቢ ላድርግ!":
        bot.send_message(m.chat.id, "**⨳ ገቢ የሚያደርጉበት መንገድ ቴሌብር ነው!**\n\n**በዚህ +251961343796 ስልክ ቁጥር ከ5 ብር ጀምሮ በማስገባት Screen Shoot ላኩ።**")
    
    elif m.text == "※ ጎደኛዬን ልጋብዝ!":
        link = f"https://t.me/ABRSHMovies_Bot?start=ref{m.from_user.id}"
        txt = (
            "**ጓደኞችዎን ይጋብዙ ና ሽልማቶች ያግኙ! 🎉**\n\n"
            "**የአብርሽን ፊልሞች እየኮመኮሙ እንዲደሰቱ ጓደኞችዎን ይጋብዙ!**\n\n"
            "**1 ሰው ሲጋብዙ > 0.7 ብር ያገኛሉ!**\n"
            "**ከታች ያለውን ልዩ የግብዣ ሊንክዎን ለጓደኞችዎ ያጋሩ ።**\n\n"
            f"**{link}**"
        )
        bot.send_message(m.chat.id, txt)
    
    elif m.text == "※ አጠቃቀም!":
        usage_text = (
            "**🧶 የICON ከለሮች ትርጉም።**\n**\">\">\">\">\">\">\">\">**\n"
            "**⚫️ -> ትርጉም ተከታታይ እና ሲንግል!**\n**🟢 -> ሲንግል!**\n**🟡 -> ተከታታይ ትርጉም!**\n"
            "**🔴 -> ሮማንስ ያለ ትርጉም!**\n**🔵 -> አማርኛ!**\n**🟣 -> ተከታታይ አማርኛ!**\n"
            "**🟠 -> ቃና ፊልሞች!**\n**⚪️ -> መፅሀፍት!**\n**\">\">\">\">\">\">\">\">**\n"
            "**💵 የፊልሞች ዋጋ**\n**💰ሲንግል -> 0.5 ብር።**\n**💰ተከታታይ -> 0.3 ብር።**\n"
            "**💰አማርኛ -> 0.5 ብር።**\n**💰ኢሮቲክ -> 1 ብር።**\n**💰ተከታታይ አማርኛ -> 0.5 ብር።**\n"
            "**💰ቃና -> 0.3 ብር።**\n**💰መፅሀፍ -> 5 ብር።**\n**\">\">\">\">\">\">\">\">**\n"
            "**✅ @ABRSHFILMBET**"
        )
        bot.send_message(m.chat.id, usage_text)
    
    elif m.text == "※ DM ABRSH!":
        bot.send_message(m.chat.id, "**የዚህ ቦት Owner👉 @ABRSHFILMBET**")

# --- 7. SEARCH & BUY ---
def search_movie(m):
    res = conn.execute("SELECT id, name, price, category FROM movies WHERE name LIKE ?", (f'%{m.text}%',)).fetchall()
    if not res:
        bot.send_message(m.chat.id, "**⨳ በዚ ስም የተሰየመ ፊልም ማግኘት አልቻልኩም!**\n**⨳ ፊደል ተሳስተው እንዳይሆን ያረጋግጡ!**")
        return
    kb = types.InlineKeyboardMarkup(row_width=1)
    for r in res[:10]:
        kb.add(types.InlineKeyboardButton(f"🎬 {r[1]} | {r[3]} | {r[2]} ብር", callback_data=f"buy_{r[0]}"))
    bot.send_message(m.chat.id, f"**🔍 ውጤቶች፦**", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy_movie(call):
    mid = call.data.split("_")[1]
    mov = conn.execute("SELECT name, file_id, price FROM movies WHERE id=?", (mid,)).fetchone()
    usr = conn.execute("SELECT balance FROM users WHERE user_id=?", (call.from_user.id,)).fetchone()
    if usr and usr[0] >= mov[2]:
        new_bal = usr[0] - mov[2]
        conn.execute("UPDATE users SET balance=? WHERE user_id=?", (new_bal, call.from_user.id))
        conn.commit()
        bot.send_video(call.message.chat.id, mov[1], caption=f"**🎬 {mov[0]}**\n**💰 ቀሪ ሂሳብ፦ {new_bal} ብር**")
    else: bot.answer_callback_query(call.id, "❌ በቂ ሂሳብ የለዎትም!", show_alert=True)

# --- 8. ADMIN ACTIONS ---
@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def admin_calls(call):
    if call.data == "adm_stats":
        u = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        m = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        bot.answer_callback_query(call.id, f"Users: {u} | Movies: {m}", show_alert=True)
    elif call.data == "adm_upload":
        msg = bot.send_message(ADMIN_ID, "**📂 ቪዲዮውን ይላኩ...**")
        bot.register_next_step_handler(msg, process_upload)
    elif call.data == "adm_edit":
        movies = conn.execute("SELECT id, name FROM movies ORDER BY id DESC LIMIT 10").fetchall()
        kb = types.InlineKeyboardMarkup()
        for mid, name in movies: kb.add(types.InlineKeyboardButton(f"🎬 {name}", callback_data=f"emov_{mid}"))
        bot.send_message(ADMIN_ID, "**⚙️ ፊልም ይምረጡ፦**", reply_markup=kb)

def process_upload(m):
    if not (m.video or m.document): return
    fid = m.video.file_id if m.video else m.document.file_id
    user_states[ADMIN_ID] = {'fid': fid, 'name': m.caption or "ያልተሰየመ"}
    kb = types.InlineKeyboardMarkup(row_width=2)
    opts = [("⚫️", 0.5), ("🟢", 0.5), ("🟡", 0.3), ("🔴", 1.0), ("🔵", 0.5), ("⚪️", 5.0)]
    for i, p in opts: kb.insert(types.InlineKeyboardButton(f"{i} {p} ብር", callback_data=f"sv_{i}_{p}"))
    bot.send_message(ADMIN_ID, "**ዋጋ ይምረጡ፦**", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("sv_"))
def save_movie(call):
    _, cat, prc = call.data.split("_")
    d = user_states.get(ADMIN_ID)
    if d:
        conn.execute("INSERT INTO movies (name, file_id, price, category) VALUES (?,?,?,?)", (d['name'], d['fid'], float(prc), cat))
        conn.commit()
        bot.edit_message_text(f"**✅ {d['name']} ተጭኗል።**", call.message.chat.id, call.message.message_id)

# --- 9. DEPOSIT HANDLER ---
@bot.message_handler(content_types=['photo'])
def handle_pay(m):
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("✅ Accept", callback_data=f"p_acc_{m.from_user.id}"),
           types.InlineKeyboardButton("❌ Reject", callback_data=f"p_rej_{m.from_user.id}"))
    bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
    bot.send_message(ADMIN_ID, f"💰 ጥያቄ ከ፦ {m.from_user.first_name} ({m.from_user.id})", reply_markup=kb)
    bot.send_message(m.chat.id, "**⏳ ስክሪንሹቱ ተልኳል፣ አድሚኑ እስኪያረጋግጥ ይጠብቁ።**")

@bot.callback_query_handler(func=lambda c: c.data.startswith("p_"))
def pay_approval(call):
    _, action, uid = call.data.split("_")
    if action == "acc":
        msg = bot.send_message(ADMIN_ID, f"**ስንት ብር ይግባለት?**")
        bot.register_next_step_handler(msg, lambda m: confirm_pay(m, uid))
    else:
        bot.send_message(uid, f"**ውድ ጥያቄዎ አልተሳካም❎**")

def confirm_pay(m, uid):
    try:
        amt = float(m.text)
        curr = conn.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone()[0]
        conn.execute("UPDATE users SET balance=? WHERE user_id=?", (curr + amt, uid))
        conn.commit()
        bot.send_message(uid, f"**✅ {amt} ብር ተጨምሯል!**")
        bot.send_message(ADMIN_ID, "✅ ተፈጽሟል።")
    except: pass

if __name__ == "__main__":
    Thread(t
