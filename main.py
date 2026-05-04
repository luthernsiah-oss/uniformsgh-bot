import telebot
import os
import sqlite3

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6045603526

# DATABASE
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER,
    balance INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    referrer INTEGER,
    status TEXT
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
            pass

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?, ?)", (user_id, referrer))
        conn.commit()

    bot.send_message(user_id,
        "🎓 *Welcome to UniformsGH*\n\n"
        "Select a university type:\n\n"
        "1️⃣ Public Universities – ₵295\n"
        "2️⃣ Technical Universities – ₵250\n\n"
        "Send *1* or *2* to continue",
        parse_mode="Markdown"
    )

# SELECT CATEGORY
@bot.message_handler(func=lambda m: m.text in ["1", "2"])
def select_category(message):
    if message.text == "1":
        bot.send_message(message.chat.id,
            "🏛 Public Universities:\n"
            "UG, KNUST, UCC, UEW, UDS, UMaT, UHAS, UENR, UPSA, USTED, UESD, GCTU, UniMAC\n\n"
            "💰 Price: ₵295\n\n"
            "📲 Pay to: 0530790707\n\n"
            "After payment, send screenshot here."
        )
    else:
        bot.send_message(message.chat.id,
            "🔧 Technical Universities:\n"
            "ATU, KsTU, KTU, CCTU, TTU, HTU, BTU\n\n"
            "💰 Price: ₵250\n\n"
            "📲 Pay to: 0530790707\n\n"
            "After payment, send screenshot here."
        )

# PAYMENT SCREENSHOT
@bot.message_handler(content_types=['photo'])
def payment(message):
    user_id = message.chat.id

    cursor.execute("SELECT referrer FROM users WHERE user_id=?", (user_id,))
    ref = cursor.fetchone()
    referrer = ref[0] if ref else None

    cursor.execute("INSERT INTO orders (user_id, referrer, status) VALUES (?, ?, ?)",
                   (user_id, referrer, "pending"))
    order_id = cursor.lastrowid
    conn.commit()

    bot.send_message(user_id, "✅ Payment received. Waiting for admin approval.")

    bot.forward_message(ADMIN_ID, user_id, message.message_id)

    bot.send_message(ADMIN_ID,
        f"💰 New Order\nUser: {user_id}\nOrder ID: {order_id}\n\nApprove with:\n/approve {order_id}"
    )

# APPROVE
@bot.message_handler(commands=['approve'])
def approve(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        order_id = int(message.text.split()[1])
    except:
        bot.send_message(ADMIN_ID, "Use: /approve order_id")
        return

    cursor.execute("SELECT user_id, referrer FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()

    if not order:
        bot.send_message(ADMIN_ID, "Order not found")
        return

    user_id, referrer = order

    # update order
    cursor.execute("UPDATE orders SET status='approved' WHERE id=?", (order_id,))

    # pay affiliate
    if referrer:
        cursor.execute("UPDATE users SET balance = balance + 25 WHERE user_id=?", (referrer,))
        bot.send_message(referrer, "🎉 You earned ₵25 from a referral!")

    conn.commit()

    bot.send_message(user_id,
        "🎉 Payment approved!\n\nAdmin will send your form shortly."
    )

    bot.send_message(ADMIN_ID, "✅ Approved successfully")

# BALANCE
@bot.message_handler(commands=['balance'])
def balance(message):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (message.chat.id,))
    bal = cursor.fetchone()

    amount = bal[0] if bal else 0

    bot.send_message(message.chat.id, f"💰 Your balance: ₵{amount}")

# GENERATE LINK (ADMIN ONLY)
@bot.message_handler(commands=['genlink'])
def genlink(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])
    except:
        bot.send_message(ADMIN_ID, "Use: /genlink user_id")
        return

    link = f"https://t.me/uniformsgh_bot?start={user_id}"

    bot.send_message(ADMIN_ID, f"🔗 Affiliate Link:\n{link}")

print("BOT RUNNING...")
bot.infinity_polling()
