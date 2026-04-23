import os
import telebot
import requests
import threading
import time
import json
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = "8226051269:AAEguc-ggOp_sIOf2tlucCba1oiyXr2TP-A"
OWNER_ID = 6207280168 
OWNER_USERNAME = "@jahidx71"

bot = telebot.TeleBot(BOT_TOKEN)
DATA_FILE = "auto_db.json"

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: return {}
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

# === AUTO WORKER (সকাল ১০টায় রান হবে) ===
def auto_worker():
    while True:
        now = datetime.now()
        # বাংলাদেশ সময় সকাল ১০টা চেক (সার্ভার টাইম অনুযায়ী অ্যাডজাস্ট হতে পারে)
        if now.hour == 10 and now.minute == 0:
            db = load_db()
            if db:
                for uid in list(db.keys()):
                    info = db[uid]
                    res = call_api(info['region'], uid)
                    if res and res.get("status") == 1:
                        added = int(res.get("LikesGivenByAPI", 0))
                        db[uid]["total_sent"] += added
                        
                        # লিমিট চেক (যদি 'Unlimited' না হয়)
                        if info['limit'] != "Unlimited":
                            if db[uid]["total_sent"] >= int(info['limit']):
                                del db[uid]
                save_db(db)
            time.sleep(61) 
        time.sleep(30)

threading.Thread(target=auto_worker, daemon=True).start()

# === SECURE FILTER ===
@bot.message_handler(func=lambda m: m.from_user.id != OWNER_ID)
def ignore_others(message):
    return 

# === ADMIN COMMANDS ===

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "✅ Admin System Active.")

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

@bot.message_handler(commands=['add'])
def add_auto_like(message):
    args = message.text.split()
    # ফরম্যাট: /add (Uid) (Server) (Limit/N)
    if len(args) == 4:
        uid, region, like_limit = args[1], args[2], args[3]
        
        limit_val = "Unlimited" if like_limit.upper() == 'N' else like_limit
        
        res = call_api(region, uid)
        if res and res.get("status") == 1:
            db = load_db()
            db[uid] = {
                "name": res.get('PlayerNickname'),
                "region": region,
                "limit": limit_val,
                "total_sent": int(res.get("LikesGivenByAPI", 0))
            }
            save_db(db)
            
            text = (f"✅ Auto Like Add Successful !\n\n"
                    f"👤 Name: {res.get('PlayerNickname')}\n"
                    f"🆔 UID: {uid}\n"
                    f"🌍 Region: {region}\n"
                    f"🤡 Likes Before: {res.get('LikesbeforeCommand')}\n"
                    f"📈 Likes Added: {res.get('LikesGivenByAPI')}\n"
                    f"🗿 Total Likes Now: {limit_val}\n"
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
            bot.reply_to(message, f"🗑️ UID {uid} রিমুভ করা হয়েছে।")

@bot.message_handler(commands=['List'])
def list_auto(message):
    db = load_db()
    if not db:
        bot.reply_to(message, "📝 লিস্ট খালি।")
        return
    
    msg = "📊 Auto Like List:\n"
    for i, (uid, info) in enumerate(db.items(), 1):
        msg += f"{i}. {uid} | Limit: {info['limit']} | Sent: {info['total_sent']}\n"
    bot.reply_to(message, msg)

if __name__ == "__main__":
    bot.infinity_polling()
                
