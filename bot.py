from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os 
BOT_TOKEN = os.environ.get("BOT_TOKEN")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏥 Welcome to HouseJob Helper!\n\n"
        "We help you secure your housemanship slot automatically.\n\n"
        "Type /pay to get started and make payment."
    )

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 To activate your slot grabber, make payment here:\n\n"
        "👉 Payment link coming soon!\n\n"
        "Once payment is confirmed, you will be asked to enter your portal details."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Checking your slot status... not active yet.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Need help? Contact us at @yourusername"
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pay", pay))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("help", help_command))

app.run_polling()
