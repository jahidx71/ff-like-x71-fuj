import telebot
import requests
from flask import Flask
from threading import Thread
import os
import datetime
import time
from telebot import types

# === CONFIG ===
BOT_TOKEN = "8320059942:AAH0V-RlPUD_CKJ2dMB1lDUDxRDX0ubL0Pg"
OWNER_ID = 6207280168 
OWNER_USERNAME = "@jahidx71"
CHANNEL_ID = "@X71_SOCIETY" 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# ইউজার লাস্ট ব্যবহারের সময় ট্র্যাকিং
user_last_use = {}

@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# চ্যানেল জয়েন চেক ফাংশন
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# বাটন: গ্রুপে এড করার জন্য
def get_add_to_group_button():
    markup = types.InlineKeyboardMarkup()
    url = f"https://t.me/{bot.get_me().username}?startgroup=true"
    btn = types.InlineKeyboardButton("Add Me To Your Group", url=url)
    markup.add(btn)
    return markup

# বাটন: জয়েন চ্যানেল
def get_join_channel_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Join Channel", url="https://t.me/X71_SOCIETY")
    markup.add(btn)
    return markup

def call_api(region, uid):
    url = f"http://free-fire-x71-like-api.vercel.app/like?uid={uid}&server_name={region}"
    try:
        response = requests.get(url, timeout=25)
        return response.json()
    except:
        return None

# === ইনবক্স (Private Chat) কন্ট্রোল ===
@bot.message_handler(func=lambda m: m.chat.type == "private")
def private_chat_restriction(message):
    text = (
        "এই বটটি যেকোনো গ্রুপে কাজ করবে, তাই লাইক নেওয়ার জন্য আপনার গ্রুপে এই বটটি অ্যাড করুন 💝\n"
        "--------------------------------------------------\n"
        "This bot will work in any group, so add this bot to your group to get likes 💝\n\n"
        "To make the bot work, you must join our channel."
    )
    bot.reply_to(message, text, reply_markup=get_join_channel_button())

# === গ্রুপে কমান্ড হ্যান্ডলার ===
@bot.message_handler(commands=['start'])
def start_in_group(message):
    if message.chat.type != "private" and message.from_user.id == OWNER_ID:
        bot.reply_to(message, "Admin ✅")

@bot.message_handler(commands=['like'])
def handle_like(message):
    if message.chat.type == "private":
        return 

    user_id = message.from_user.id
    current_time = time.time()
    wait_time = 24 * 3600 # ২৪ ঘণ্টা

    # এডমিন চেক (এডমিন আনলিমিটেড)
    if user_id != OWNER_ID:
        # চ্যানেল সাবস্ক্রিপশন চেক
        if not is_subscribed(user_id):
            bot.reply_to(message, "Please join our channel to use this command:", reply_markup=get_join_channel_button())
            return

        # প্রতিদিন ১ বার ব্যবহারের লিমিট চেক
        if user_id in user_last_use:
            elapsed_time = current_time - user_last_use[user_id]
            if elapsed_time < wait_time:
                remaining_seconds = wait_time - elapsed_time
                hours = int(remaining_seconds // 3600)
                minutes = int((remaining_seconds % 3600) // 60)
                bot.reply_to(message, f"⏳ You Already Used Today\nTry After {hours}h {minutes}m", reply_markup=get_add_to_group_button())
                return

    args = message.text.split()
    if len(args) == 3:
        region, uid = args[1], args[2]
        res = call_api(region, uid)
        
        if res:
            status = res.get("status")
            if status == 1:
                # সাকসেস হলে সময় সেভ করা (এডমিন বাদে)
                if user_id != OWNER_ID:
                    user_last_use[user_id] = current_time
                
                text = (f"✅ Like Send Successful !\n\n"
                        f"👤 Name: {res.get('PlayerNickname')}\n"
                        f"🆔 UID: {uid}\n"
                        f"🌍 Region: {region}\n"
                        f"🧩 Likes Before: {res.get('LikesbeforeCommand')}\n"
                        f"📈 Likes Added: {res.get('LikesGivenByAPI')}\n"
                        f"🗿 Likes Now: {res.get('LikesafterCommand')}\n\n"
                        f"👑 Credit: {OWNER_USERNAME}")
                bot.reply_to(message, text, reply_markup=get_add_to_group_button())
            
            elif status == 0 or "Already Send" in str(res.get("message", "")):
                bot.reply_to(message, "Like Already Send This UID ,😐", reply_markup=get_add_to_group_button())
            
            else:
                bot.reply_to(message, "Like Send Failed ,😐", reply_markup=get_add_to_group_button())
        else:
            bot.reply_to(message, "Like Send Failed ,😐", reply_markup=get_add_to_group_button())

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    print("✅ Bot is Running Successfully!")
    bot.infinity_polling()
    
