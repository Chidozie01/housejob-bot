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
    await
