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
    # Render-এর জন্য সঠিক পোর্ট হ্যান্ডলিং
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

# === AUTHORIZATION FILTER ===
# আপনি নিজে এবং যেকোনো বট থেকে কমান্ড আসলে কাজ করবে
def is_authorized(message):
    if message.from_user.id == OWNER_ID:
        return True
    if message.from_user.is_bot:
        return True
    return False

# === LIKE COMMAND ===
@bot.message_handler(func=lambda m: is_authorized(m), commands=['like'])
def handle_like(message):
    args = message.text.split()
    # ফরম্যাট: /like bd 12345678
    if len(args) == 3:
        region, uid = args[1], args[2]
        res = call_api(region, uid)
        
        if res and res.get("status") == 1:
            text = (f"✅ Like Send Successful !\n\n"
                    f"👤 Name: {res.get('PlayerNickname')}\n"
                    f"🆔 UID: {uid}\n"
                    f"🌍 Region: {region}\n"
                    f"🤡 Likes Before: {res.get('LikesbeforeCommand')}\n"
                    f"📈 Likes Added: {res.get('LikesGivenByAPI')}\n"
                    f"🗿 Total Likes Now: {res.get('LikesafterCommand')}\n"
                    f"👑 Credit: {OWNER_USERNAME}")
            bot.reply_to(message, text)
        else:
            if message.from_user.id == OWNER_ID:
                bot.reply_to(message, "❌ API Error or Limit Reached.")

# স্টার্ট কমান্ড
@bot.message_handler(commands=['start'])
def start(message):
    if is_authorized(message):
        bot.reply_to(message, "✅ Admin/Bot System Active. Use `/like region uid`.")

# সাধারণ ব্যবহারকারীদের জন্য সাইলেন্ট মোড
@bot.message_handler(func=lambda m: not is_authorized(m))
def ignore_others(message):
    pass

# === MAIN EXECUTION ===
if __name__ == "__main__":
    # ১. প্রথমে ফ্লাস্ক সার্ভার চালু হবে (যাতে Cron-job লিঙ্ক খুঁজে পায়)
    keep_alive()
    print("✅ Web Server started...")
    
    # ২. এরপর বট পোলিং শুরু করবে
    print("✅ Bot is polling...")
    bot.infinity_polling()
    
