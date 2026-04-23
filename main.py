import telebot
import requests

# === CONFIG ===
BOT_TOKEN = "8226051269:AAEguc-ggOp_sIOf2tlucCba1oiyXr2TP-A"
OWNER_ID = 6207280168 
OWNER_USERNAME = "@jahidx71"

bot = telebot.TeleBot(BOT_TOKEN)

# === API CALL ===
def call_api(region, uid):
    url = f"http://free-fire-x71-like-api.vercel.app/like?uid={uid}&server_name={region}"
    try:
        response = requests.get(url, timeout=25)
        return response.json()
    except:
        return None

# === FILTER LOGIC ===
# এটি চেক করবে মেসেজটি আপনার (Owner) থেকে এসেছে কি না অথবা কোনো Bot থেকে এসেছে কি না
def is_authorized(message):
    if message.from_user.id == OWNER_ID:
        return True
    if message.from_user.is_bot: # যেকোনো বট থেকে রিকোয়েস্ট আসলে এটি True হবে
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
            # যদি এপিআই এরর দেয় তবে শুধু আপনাকে (এডমিন) জানাবে
            if message.from_user.id == OWNER_ID:
                bot.reply_to(message, "❌ API Error or Limit Reached.")

# এডমিন ছাড়া অন্য সাধারণ মানুষ কমান্ড দিলে কোনো উত্তর দেবে না
@bot.message_handler(func=lambda m: not is_authorized(m))
def ignore_others(message):
    pass

if __name__ == "__main__":
    print("✅ Bot is active for Admin and other Bots...")
    bot.infinity_polling()
    
