import telebot
import requests
from flask import Flask
from threading import Thread
import os

# === CONFIG ===
# আপনার দেওয়া তথ্য অনুযায়ী
BOT_TOKEN = "8226051269:AAEguc-ggOp_sIOf2tlucCba1oiyXr2TP-A"
OWNER_ID = 6207280168 
OWNER_USERNAME = "@jahidx71"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# === FLASK SERVER FOR UPTIME ===
@app.route('/')
def home():
    return "Bot is Alive and Running!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# === API CALL ===
def call_api(region, uid):
    url = f"http://free-fire-x71-like-api.vercel.app/like?uid={uid}&server_name={region}"
    try:
        response = requests.get(url, timeout=25)
        return response.json()
    except:
        return None

# === LIKE COMMAND (ONLY FOR ADMIN) ===
@bot.message_handler(commands=['like'])
def handle_like(message):
    # শুধুমাত্র আপনি (Admin) ব্যবহার করতে পারবেন
    if message.from_user.id != OWNER_ID:
        return # অন্য কেউ কমান্ড দিলে বট কোনো উত্তরই দেবে না

    args = message.text.split()
    # ফরম্যাট: /like bd 12345678
    if len(args) == 3:
        region, uid = args[1], args[2]
        res = call_api(region, uid)
        
        if res:
            status = res.get("status")
            
            # যদি লাইক সফলভাবে যায়
            if status == 1:
                text = (f"✅ **Like Send Successful !**\n\n"
                        f"👤 **Name:** `{res.get('PlayerNickname')}`\n"
                        f"🆔 **UID:** `{uid}`\n"
                        f"🌍 **Region:** `{region}`\n"
                        f"🧩 **Likes Before:** `{res.get('LikesbeforeCommand')}`\n"
                        f"📈 **Likes Added:** `{res.get('LikesGivenByAPI')}`\n"
                        f"🗿 **Total Likes Now:** `{res.get('LikesafterCommand')}`\n\n"
                        f"👑 **Credit:** {OWNER_USERNAME}")
                bot.reply_to(message, text, parse_mode="Markdown")
            
            # যদি আজ অলরেডি লাইক দেওয়া হয়ে থাকে
            elif "Already Sent" in str(res.get("message", "")) or status == 0:
                bot.reply_to(message, "❌ **Like Already Sent Today, This UID. 😐**", parse_mode="Markdown")
            
            else:
                bot.reply_to(message, "❌ **API Error or Invalid UID.**")
        else:
            bot.reply_to(message, "❌ **Server Timeout or API Down.**")

# স্টার্ট কমান্ড (শুধুমাত্র এডমিনদের জন্য)
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "✅ **Admin Panel Active.**\nUse `/like region uid` to send likes.")

# অন্য সব মেসেজ ইগনোর করবে
@bot.message_handler(func=lambda m: True)
def ignore_all(message):
    pass

# === MAIN RUNNER ===
if __name__ == "__main__":
    keep_alive() # Render-কে জাগিয়ে রাখার জন্য
    print("✅ Admin-Only Bot is starting...")
    bot.infinity_polling()
    
