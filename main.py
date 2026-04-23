import telebot
import requests
from flask import Flask
from threading import Thread
import os

# === CONFIG ===
BOT_TOKEN = "8226051269:AAEguc-ggOp_sIOf2tlucCba1oiyXr2TP-A"
OWNER_ID = 6207280168 
OWNER_USERNAME = "@jahidx71"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# === FLASK SERVER FOR UPTIME (Cron-job এর জন্য) ===
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

# === AUTHORIZATION FILTER (আপনার মূল চাওয়া) ===
def is_authorized(message):
    # ১. আপনি (Admin) নিজে পাঠালে কাজ করবে
    if message.from_user.id == OWNER_ID:
        return True
    
    # ২. মেসেজটি যদি কোনো বট (Any Bot) থেকে আসে তবে কাজ করবে
    if message.from_user.is_bot:
        return True
    
    # ৩. যদি ইনলাইন বা অন্য কোনো ভাবে বটের মাধ্যমে আসে
    if message.via_bot is not None:
        return True
        
    return False

# === LIKE COMMAND ===
@bot.message_handler(func=lambda m: is_authorized(m), commands=['like'])
def handle_like(message):
    # কমান্ড ফরম্যাট চেক: /like bd 12345678
    args = message.text.split()
    
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
            # এরর মেসেজ শুধু আপনাকে (Admin) দেখাবে যাতে অন্য বট কনফিউজ না হয়
            if message.from_user.id == OWNER_ID:
                bot.reply_to(message, "❌ API Error or Limit Reached.")

# সাধারণ ইউজারদের জন্য কোনো রেসপন্স নেই
@bot.message_handler(func=lambda m: not is_authorized(m))
def ignore_others(message):
    pass

# === MAIN RUNNER ===
if __name__ == "__main__":
    keep_alive() # সার্ভার স্টার্ট
    print("✅ Web Server & Bot is starting...")
    bot.infinity_polling(allowed_updates=['message', 'callback_query', 'edited_message'])
                
