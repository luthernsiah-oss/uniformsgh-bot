import telebot
import sqlite3
import os

ADMIN_ID = 6045603526

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()


# START
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    args = message.text.split()
    referrer = None

    if len(args) > 1:
        try:
            referrer = int(args[1])
        except:
            referrer = None

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?, ?)", (user_id, referrer))
        conn.commit()

    bot.send_message(user_id,
        "Welcome to UniformsGH Bot 🎓\n\nUse /referral to earn ₵25 per sale.")


# REFERRAL
@bot.message_handler(commands=['referral'])
def referral(message):
    user_id = message.chat.id
    link = f"https://t.me/uniformsgh_bot?start={user_id}"

    bot.send_message(user_id, f"Your referral link:\n{link}")


# BUY
@bot.message_handler(commands=['buy'])
def buy(message):
    user_id = message.chat.id

    bot.send_message(user_id,
        "University forms: ₵295\nTechnical Universities: ₵250\n\nPay via MoMo: 0530790707")

    cursor.execute("SELECT referrer FROM users WHERE user_id=?", (user_id,))
    ref = cursor.fetchone()

    if ref and ref[0]:
        cursor.execute("UPDATE users SET balance = balance + 25 WHERE user_id=?", (ref[0],))
        conn.commit()


# PAID
@bot.message_handler(commands=['paid'])
def paid(message):
    user_id = message.chat.id

    bot.send_message(user_id,
        "Payment received 👍\nWaiting for admin approval.")

    bot.send_message(
        ADMIN_ID,
        f"💰 Payment request from user: {user_id}\nApprove with /approve {user_id}"
    )


# APPROVE
@bot.message_handler(commands=['approve'])
def approve(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])

        cursor.execute("UPDATE users SET balance = balance + 25 WHERE user_id=?", (user_id,))
        conn.commit()

        bot.send_message(user_id, "🎉 Approved! ₵25 added to your balance.")
        bot.send_message(ADMIN_ID, "✔ Approved")

    except:
        bot.send_message(ADMIN_ID, "Usage: /approve user_id")


# BALANCE
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.chat.id

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cursor.fetchone()

    if bal:
        bot.send_message(user_id, f"Your earnings: ₵{bal[0]}")
    else:
        bot.send_message(user_id, "No earnings yet.")


bot.infinity_polling()
