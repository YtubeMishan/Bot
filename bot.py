from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Replace with your actual bot token
BOT_TOKEN = "7769439864:AAHoR601B2jzOzdIIlzShyTFO-twgsqcGkM"

OWNER_ID = 7912905599  # Your Telegram user ID

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    keyboard = [
        [InlineKeyboardButton("ITM", callback_data="itm")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Bot started! Predictions will be sent every 30 seconds.",
        reply_markup=reply_markup,
    )

# Callback handler for the "ITM" button
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_ID:
        await query.edit_message_text(text="You are not authorized to press this button.")
        return

    await query.edit_message_text(text="Profit (ITM) acknowledged, stopping predictions.")
    # Here, implement logic to stop your prediction loop

# Main function to build the bot application
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
