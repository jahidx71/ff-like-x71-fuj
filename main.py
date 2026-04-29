import telebot
import requests
from flask import Flask
from threading import Thread
import os

# CONFIG
BOT_TOKEN = "8320059942:AAH0V-RlPUD_CKJ2dMB1lDUDxRDX0ubL0Pg"
OWNER_ID = 6207280168 
OWNER_USERNAME = "@jahidx71"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

def call_api(region, uid):
    url = f"http://free-fire-xj-711-like-api.vercel.app/like?uid={uid}&server_name={region}"
    try:
        response = requests.get(url, timeout=25)
        return response.json()
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "Admin ✅")

@bot.message_handler(commands=['like'])
def handle_like(message):
    if message.from_user.id != OWNER_ID:
        return 

    args = message.text.split()
    if len(args) == 3:
        region, uid = args[1], args[2]
        res = call_api(region, uid)
        
        if res:
            status = res.get("status")
            if status == 1:
                text = (f"✅ Like Send Successful !\n\n"
                        f"👤 Name: {res.get('PlayerNickname')}\n"
                        f"🆔 UID: {uid}\n"
                        f"🌍 Region: {region}\n"
                        f"🧩 Likes Before: {res.get('LikesbeforeCommand')}\n"
                        f"📈 Likes Added: {res.get('LikesGivenByAPI')}\n"
                        f"🗿 Likes Now: {res.get('LikesafterCommand')}\n\n"
                        f"👑 Credit: {OWNER_USERNAME}")
                bot.reply_to(message, text)
            else:
                bot.reply_to(message, "Like Send Failed. 😐")
        else:
            bot.reply_to(message, "Like Send Failed. 😐")

@bot.message_handler(func=lambda m: True)
def ignore_all(message):
    pass

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling()
        
