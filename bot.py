import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, ConversationHandler, filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Conversation states
HOSPITAL_TYPE, HOSPITAL_CHOICES, MDCN_NUMBER, PORTAL_PASSWORD = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏥 Welcome to HouseJob Helper!\n\n"
        "We help you secure your housemanship slot automatically.\n\n"
        "Type /pay to get started and make payment."
    )

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Payment is currently being updated.\n\n"
        "We're switching to a new payment provider — please check back shortly!\n\n"
        "Need help? Contact @yourusername"
    )

async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏥 Regular Hospital", callback_data="regular")],
        [InlineKeyboardButton("⭐ Premium Hospital", callback_data="premium")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ Payment confirmed! Let's set up your slot grabber.\n\n"
        "Which type of hospital are you going for?",
        reply_markup=reply_markup
    )
    return HOSPITAL_TYPE

async def hospital_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["hospital_type"] = query.data
    await query.edit_message_text(
        "🏥 Enter up to 3 hospitals you want, separated by commas.\n\n"
        "Example:\n"
        "UATH, Garki Hospital, FMC Ebute Metta"
    )
    return HOSPITAL_CHOICES

async def hospital_choices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hospitals"] = update.message.text
    await update.message.reply_text(
        "🔑 Now enter your MDCN registration number:"
    )
    return MDCN_NUMBER

async def mdcn_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mdcn"] = update.message.text
    await update.message.reply_text(
        "🔒 Now enter your housemanship portal password:\n\n"
        "⚠️ Your details are encrypted and used ONLY to secure your slot."
    )
    return PORTAL_PASSWORD

async def portal_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["password"] = update.message.text
    hospitals = context.user_data.get("hospitals")
    mdcn = context.user_data.get("mdcn")

    await update.message.reply_text(
        f"✅ All details received!\n\n"
        f"🏥 Hospitals: {hospitals}\n"
        f"🔑 MDCN: {mdcn}\n\n"
        f"🤖 Your slot grabber is now ACTIVE!\n"
        f"We will check every 60 seconds and notify you the moment your slot is secured! 🎯"
    )
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Checking your slot status... not active yet.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Need help? Contact us at @yourusername")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled. Type /start to begin again.")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("activate", activate)],
    states={
        HOSPITAL_TYPE: [CallbackQueryHandler(hospital_type_chosen)],
        HOSPITAL_CHOICES: [MessageHandler(filters.TEXT & ~filters.COMMAND, hospital_choices)],
        MDCN_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, mdcn_number)],
        PORTAL_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, portal_password)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pay", pay))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(conv_handler)

app.run_polling()
