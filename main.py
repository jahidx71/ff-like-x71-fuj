import os
import telebot
import requests
import threading
import time
import json
from datetime import datetime

# === CONFIG ===
# আপনার দেওয়া বট টোকেন
BOT_TOKEN = "8226051269:AAEguc-ggOp_sIOf2tlucCba1oiyXr2TP-A"
# শুধুমাত্র এই আইডি কমান্ড দিতে পারবে
OWNER_ID = 6207280168 
OWNER_USERNAME = "@jahidx71"

bot = telebot.TeleBot(BOT_TOKEN)

# ডাটাবেজ ফাইল (অটো লাইক সেভ রাখার জন্য)
DATA_FILE = "auto_db.json"

def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=4)

# === API CALL ===
def call_api(region, uid):
    url = f"http://free-fire-x71-like-api.vercel.app/like?uid={uid}&server_name={region}"
    try:
        response = requests.get(url, timeout=25)
        return response.json()
    except:
        return None

# === BACKGROUND AUTO PROCESS ===
def auto_worker():
    while True:
        db = load_db()
        to_remove = []
        for uid, info in db.items():
            res = call_api("bd", uid)
            if res and res.get("status") == 1:
                added = int(res.get("LikesGivenByAPI", 0))
                db[uid]["total_sent"] += added
                
                # লিমিট পূর্ণ হলে রিমুভ লিস্টে যোগ হবে
                if db[uid]["total_sent"] >= db[uid]["limit"]:
                    to_remove.append(uid)
        
        for uid in to_remove:
            del db[uid]
        
        save_db(db)
        time.sleep(86400) # ২৪ ঘণ্টা পর পর অটো রান হবে

threading.Thread(target=auto_worker, daemon=True).start()

# === SECURE FILTER ===
# এডমিন ছাড়া অন্য কেউ কোনো মেসেজ দিলে বট কোনো উত্তর দেবে না
@bot.message_handler(func=lambda m: m.from_user.id != OWNER_ID)
def ignore_others(message):
    return # No response for non-admins

# === ADMIN COMMANDS ===

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "✅ Admin System Active. Only you can control this bot.")

@bot.message_handler(commands=['like'])
def manual_like(message):
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

@bot.message_handler(commands=['Add'])
def add_auto_like(message):
    args = message.text.split()
    if len(args) == 3:
        uid = args[1]
        try:
            limit = int(args[2])
        except: return

        res = call_api("bd", uid)
        if res and res.get("status") == 1:
            db = load_db()
            added_now = int(res.get("LikesGivenByAPI", 0))
            db[uid] = {
                "name": res.get('PlayerNickname'),
                "limit": limit,
                "total_sent": added_now,
                "before": res.get('LikesbeforeCommand')
            }
            save_db(db)
            
            text = (f"✅ Auto Like Send Successful !\n\n"
                    f"👤 Name: {res.get('PlayerNickname')}\n"
                    f"🆔 UID: {uid}\n"
                    f"🌍 Region: bd\n"
                    f"🤡 Likes Before: {res.get('LikesbeforeCommand')}\n"
                    f"📈 Likes Added: {added_now}\n"
                    f"🗿 Total Likes Now: {limit}\n"
                    f"👑 Credit: {OWNER_USERNAME}")
            bot.reply_to(message, text)

@bot.message_handler(commands=['Delete'])
def delete_auto(message):
    args = message.text.split()
    if len(args) == 2:
        uid = args[1]
        db = load_db()
        if uid in db:
            del db[uid]
            save_db(db)
            bot.reply_to(message, f"🗑️ UID {uid} and its settings removed.")

@bot.message_handler(commands=['List'])
def list_auto(message):
    db = load_db()
    if not db:
        bot.reply_to(message, "📝 List is empty.")
        return
    
    msg = "📊 Auto Like List:\n"
    for i, (uid, info) in enumerate(db.items(), 1):
        msg += f"{i}. {uid} | Limit: {info['limit']} | Total Sent: {info['total_sent']}\n"
    bot.reply_to(message, msg)

# ক্যাচ-অল: এডমিন যদি ভুল কমান্ড দেয় তবেও কোনো রিপ্লাই দিবে না
@bot.message_handler(func=lambda m: True)
def final_ignore(message):
    pass

if __name__ == "__main__":
    print("✅ Bot is running for Admin only.")
    bot.infinity_polling()
      
