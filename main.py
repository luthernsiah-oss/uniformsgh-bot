import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ─── LOGGING ─────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── ENV ────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# ─── SAFETY CHECK (THIS PREVENTS CRASH) ─
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing in Railway variables")

# ─── START ──────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot is LIVE\n\n"
        "Commands working:\n"
        "/buy\n"
        "/balance\n"
        "/referral"
    )

# ─── SIMPLE TEST COMMANDS ───────────────
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Shop Menu\n\n"
        "Forms:\n- ₵295 Public\n- ₵250 Technical\n\n"
        "Send /paid after payment"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Balance system coming soon")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔗 Referral system active\n\n"
        f"Your ID: {update.effective_user.id}"
    )

# ─── MAIN ───────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))

    logger.info("Bot started successfully")
    app.run_polling()

if __name__ == "__main__":
    main()
