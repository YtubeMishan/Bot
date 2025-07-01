import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import asyncio
from prediction import PredictionManager

# === CONFIG ===
BOT_TOKEN = "6524072744:AAGLnv-NvVKvQDw_JPlEp6byMvHzsVuOCWg"
OWNER_ID = 7912905599
CHANNEL_ID = -1002898322642  # or @wingo30s_predict

# === LOGGING ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# === GLOBAL STATE ===
manager = PredictionManager()

# === HANDLERS ===

async def start_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔️ Not authorized.")
        return

    try:
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ Format: `<period> <direction>`")
            return

        period, direction = parts
        direction = direction.lower()
        if direction not in ("big", "small"):
            await update.message.reply_text("❌ Direction must be 'big' or 'small'")
            return

        if manager.active:
            await update.message.reply_text("⚠️ Prediction already running.")
            return

        manager.start(period, direction)

        # Start the prediction loop
        asyncio.create_task(send_predictions(context))

        await update.message.reply_text(f"✅ Started predicting from {period} with '{direction.upper()}'")

    except Exception as e:
        logging.error(f"Error in start_prediction: {e}")
        await update.message.reply_text("⚠️ An error occurred.")


async def send_predictions(context: ContextTypes.DEFAULT_TYPE):
    while manager.active:
        text = f"🧠 Prediction\n🆔 {manager.current_period}\n🎯 {manager.direction.upper()}"
        keyboard = [
            [InlineKeyboardButton("✅ ITM", callback_data="itm")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

        await asyncio.sleep(30)
        manager.next()


async def handle_itm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != OWNER_ID:
        await query.edit_message_text("⛔️ Only the owner can stop predictions.")
        return

    manager.stop()
    await query.edit_message_text(f"✅ ITM. Prediction stopped at {manager.current_period}.")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command or wrong format.\nUse: `2025070122000 big`")


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start_prediction))
    app.add_handler(CallbackQueryHandler(handle_itm))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("🤖 Bot is running...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
