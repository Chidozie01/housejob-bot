import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")

HOSPITALS_PREMIUM = [
    "University of Abuja Teaching Hospital", "National Hospital Abuja", "Federal Medical Centre Jabi", "Federal Medical Centre Ebute Metta"
]

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
            f"Once payment is confirmed, type /status to check."
        )
    else:
        await query.edit_message_text("❌ Error generating payment link. Please try again with /pay")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Checking your slot status... not active yet.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Need help? Contact us at @yourusername")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pay", pay))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
