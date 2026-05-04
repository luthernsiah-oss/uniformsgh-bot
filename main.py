import telebot
import os

print("BOT STARTING...")

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6045603526

# ─── START ───
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Welcome to UniformsGH Bot 🎓\n\n"
        "Use /buy to see prices\n"
        "Use /referral to get your link"
    )

# ─── BUY ───
@bot.message_handler(commands=['buy'])
def buy(message):
    bot.send_message(
        message.chat.id,
        "University Forms:\n"
        "• Public Universities: GH¢295\n"
        "• Technical Universities: GH¢250\n\n"
        "Pay via MoMo: 0530790707"
    )

# ─── REFERRAL ───
@bot.message_handler(commands=['referral'])
def referral(message):
    user_id = message.chat.id
    link = f"https://t.me/uniformsgh_bot?start={user_id}"

    bot.send_message(
        user_id,
        f"Your referral link:\n{link}\n\nEarn GH¢25 per referral!"
    )

# ─── BALANCE (simple placeholder) ───
@bot.message_handler(commands=['balance'])
def balance(message):
    bot.send_message(message.chat.id, "Balance system coming soon.")

print("BOT RUNNING...")
bot.infinity_polling()
