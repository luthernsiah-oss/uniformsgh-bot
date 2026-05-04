import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ===== CONFIG =====
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6045603526

MOMO_NUMBER = "0530790707"
ACCOUNT_NAME = "Frank Nsiah"

# ===== UNIVERSITIES =====
PUBLIC_UNIS = [
    "University of Ghana (UG)",
    "KNUST",
    "UCC",
    "UEW",
    "UDS",
    "UMaT",
    "UHAS",
    "UENR"
]

TECH_UNIS = [
    "Accra Technical University",
    "Kumasi Technical University",
    "Takoradi Technical University",
    "Cape Coast Technical University",
    "Ho Technical University"
]

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎓 Public Universities (₵295)", callback_data="public")],
        [InlineKeyboardButton("🔧 Technical Universities (₵250)", callback_data="technical")]
    ]

    await update.message.reply_text(
        "🎓 Welcome to UniformsGH\n\n"
        "Select a university type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== MENU HANDLER =====
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "public":
        buttons = [[InlineKeyboardButton(u, callback_data=f"uni_{u}")] for u in PUBLIC_UNIS]

        context.user_data["price"] = "₵295"

        await query.edit_message_text(
            "🎓 Select a Public University:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data == "technical":
        buttons = [[InlineKeyboardButton(u, callback_data=f"uni_{u}")] for u in TECH_UNIS]

        context.user_data["price"] = "₵250"

        await query.edit_message_text(
            "🔧 Select a Technical University:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data.startswith("uni_"):
        university = query.data.replace("uni_", "")
        price = context.user_data.get("price", "₵295")

        context.user_data["university"] = university

        await query.edit_message_text(
            f"🎓 {university}\n\n"
            f"💰 Price: {price}\n\n"
            f"Make payment to:\n"
            f"MoMo: {MOMO_NUMBER}\n"
            f"Name: {ACCOUNT_NAME}\n\n"
            f"After payment, send screenshot here."
        )

        context.user_data["awaiting_payment"] = True

# ===== HANDLE SCREENSHOT =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get("awaiting_payment"):

        if not update.message.photo:
            await update.message.reply_text("Please send payment screenshot.")
            return

        university = context.user_data.get("university", "Unknown")

        file_id = update.message.photo[-1].file_id

        # Send to admin
        await context.bot.send_photo(
            ADMIN_ID,
            photo=file_id,
            caption=(
                f"💰 New Payment\n\n"
                f"User ID: {user_id}\n"
                f"University: {university}\n\n"
                f"Reply with:\n"
                f"/approve {user_id}"
            )
        )

        await update.message.reply_text(
            "✅ Screenshot received.\n\nWaiting for admin approval."
        )

        context.user_data["awaiting_payment"] = False

# ===== ADMIN APPROVE =====
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])

        await context.bot.send_message(
            user_id,
            "🎉 Payment Approved!\n\n"
            "You will receive your form shortly."
        )

        await update.message.reply_text("✅ Approved")

    except:
        await update.message.reply_text("Usage: /approve user_id")

# ===== MAIN =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CallbackQueryHandler(menu))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
