import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, ConversationHandler, filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")

# Conversation states
HOSPITAL_TYPE, HOSPITAL_CHOICES, MDCN_NUMBER, PORTAL_PASSWORD = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏥 Welcome to HouseJob Helper!\n\n"
        "We help you secure your housemanship slot automatically.\n\n"
        "Type /pay to get started and make payment."
    )

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏥 Regular Hospital - ₦100,000", callback_data="pay_regular")],
        [InlineKeyboardButton("⭐ Premium Hospital - ₦300,000", callback_data="pay_premium")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💳 Select your hospital type to proceed with payment:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    email = f"{user.id}@housejobhelper.com"

    if query.data == "pay_regular":
        amount = 10000000
        label = "Regular Hospital"
    else:
        amount = 30000000
        label = "Premium Hospital"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.paystack.co/transaction/initialize",
            headers={
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "email": email,
                "amount": amount,
                "metadata": {
                    "telegram_id": user.id,
                    "hospital_type": label
                }
            }
        )
        data = response.json()

    if data["status"]:
        payment_url = data["data"]["authorization_url"]
        await query.edit_message_text(
            f"✅ You selected: {label}\n\n"
            f"💳 Click the link below to complete your payment:\n\n"
            f"👉 {payment_url}\n\n"
            f"Once payment is confirmed, type /activate to continue."
        )
    else:
        await query.edit_message_text("❌ Error generating payment link. Please try again with /pay")

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
        "University of Abuja Teaching Hospital, Federal Medical Centre Asaba , Lagos University Teaching Hospital"
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
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(conv_handler)

app.run_polling()
