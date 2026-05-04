import os
import logging
import psycopg2
from psycopg2 import pool
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ─── LOGGING ─────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── ENV ────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL")

AFFILIATE_COMMISSION = 25
FORM_PRICE_PUBLIC = 295
FORM_PRICE_TECH = 250

# ─── DB ─────────────────────────────────
db_pool = pool.ThreadedConnectionPool(1, 10, DATABASE_URL)

def conn():
    return db_pool.getconn()

def release(c):
    db_pool.putconn(c)

def init_db():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        referrer BIGINT,
        balance NUMERIC DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        type TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    c.commit()
    cur.close()
    release(c)

def register(user_id, ref=None):
    c = conn()
    cur = c.cursor()
    cur.execute("""
        INSERT INTO users (user_id, referrer)
        VALUES (%s,%s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, ref))
    c.commit()
    cur.close()
    release(c)

def add_balance(user_id, amount):
    c = conn()
    cur = c.cursor()
    cur.execute("UPDATE users SET balance = balance + %s WHERE user_id=%s", (amount, user_id))
    c.commit()
    cur.close()
    release(c)

def get_balance(user_id):
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=%s", (user_id,))
    r = cur.fetchone()
    cur.close()
    release(c)
    return r[0] if r else 0

def get_ref(user_id):
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT referrer FROM users WHERE user_id=%s", (user_id,))
    r = cur.fetchone()
    cur.close()
    release(c)
    return r[0] if r else None

# ─── START ──────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    ref = None
    if context.args:
        try:
            ref = int(context.args[0])
        except:
            ref = None

    register(user.id, ref)

    await update.message.reply_text(
        "🎓 Welcome to UniformsGH Bot\n\n"
        "Buy:\n"
        "- University Forms\n"
        "- Technical Forms\n"
        "- Checkers\n\n"
        "Commands:\n"
        "/buy - start order\n"
        "/balance - earnings\n"
        "/referral - link"
    )

# ─── REFERRAL ───────────────────────────
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = f"https://t.me/YOUR_BOT_USERNAME?start={update.effective_user.id}"
    await update.message.reply_text(f"Your referral link:\n{link}")

# ─── BUY MENU ───────────────────────────
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏛 Public Forms ₵295", callback_data="pub")],
        [InlineKeyboardButton("🔧 Technical Forms ₵250", callback_data="tech")],
        [InlineKeyboardButton("📄 Checker ₵18.50", callback_data="checker")]
    ]

    await update.message.reply_text(
        "Select product:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── CALLBACKS ──────────────────────────
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user = q.from_user

    if q.data == "pub":
        price = FORM_PRICE_PUBLIC
        order_type = "public"
    elif q.data == "tech":
        price = FORM_PRICE_TECH
        order_type = "tech"
    else:
        price = 18.5
        order_type = "checker"

    await q.edit_message_text(
        f"Order: {order_type}\nPrice: ₵{price}\n\n"
        "After payment send /paid"
    )

    ref = get_ref(user.id)
    if ref:
        add_balance(ref, AFFILIATE_COMMISSION)

# ─── PAID ───────────────────────────────
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text("Payment received 👍 waiting approval")

    await context.bot.send_message(
        ADMIN_ID,
        f"New payment from {user.id}\nApprove: /approve {user.id}"
    )

# ─── APPROVE ────────────────────────────
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        uid = int(context.args[0])
        add_balance(uid, AFFILIATE_COMMISSION)

        await update.message.reply_text("Approved ✔")
        await context.bot.send_message(uid, "🎉 Approved!")

    except:
        await update.message.reply_text("Usage: /approve user_id")

# ─── BALANCE ────────────────────────────
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = get_balance(update.effective_user.id)
    await update.message.reply_text(f"💰 Balance: ₵{bal}")

# ─── MAIN ───────────────────────────────
def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("paid", paid))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))

    app.add_handler(CallbackQueryHandler(callback))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
