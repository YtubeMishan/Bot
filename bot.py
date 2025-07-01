import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==== CONFIGURATION ====
BOT_TOKEN = '7769439864:AAHoR601B2jzOzdIIlzShyTFO-twgsqcGkM'
OWNER_ID = 7912905599
CHANNEL_ID = -1002898322642  # @wingo30s_predict

# ==== LOGGING ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==== GLOBAL VARIABLES ====
predicting = False
current_period = None
current_prediction = None
prediction_task = None

# ==== MESSAGE FORMAT ====
def format_message(period: str, prediction: str) -> str:
    return f"""
✅𝘮𝘰𝘫𝘴 𝘪𝘦𝘭𝘪 

⏩⏩⏩⏩  ⏪⏪⏪⏪ ({period}) 

⚔️𝘬𝘮𝘴𝘰𝘮 30𝘮𝘴 ⏪

❤️‍🔥ℙ𝘳𝘮𝘴𝘮𝘴𝘫𝘮 ⚡️⏩⏩  ⏪⏪⚡️ ({prediction.upper()})

💲𝘪𝘬𝘴𝘮 𝘦𝘪𝘴𝘮𝘯𝘰
             𝘪𝘦𝘭𝘪

Maintain ⚔️

𝘭𝘰 𝘵𝘮𝘫 ⏩ 𝘭𝘶 𝘪𝘮𝘭𝘰𝘪𝘱 

𝘭𝘮 𝘴𝘮 𝘮𝘱𝘦𝘭 𝘭𝘶♻️

𝘭𝘮 𝘫𝘮𝘭𝘰"""

# ==== PREDICTION LOOP ====
async def prediction_loop(application):
    global predicting, current_period
    while predicting:
        text = format_message(current_period, current_prediction)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ITM", callback_data="itm")]
        ])
        await application.bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=keyboard)

        await asyncio.sleep(30)
        current_period = str(int(current_period) + 1)

# ==== COMMAND HANDLERS ====
async def start_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global predicting, current_period, current_prediction, prediction_task

    if update.effective_user.id != OWNER_ID:
        return

    try:
        args = update.message.text.split()
        if len(args) != 2:
            await update.message.reply_text("Send in format: <period> <big/small>")
            return

        current_period = args[0]
        current_prediction = args[1].lower()
        predicting = True

        await update.message.reply_text(f"Started predicting {current_prediction.upper()} from period {current_period}")

        prediction_task = asyncio.create_task(prediction_loop(context.application))

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Something went wrong.")

async def stop_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global predicting, prediction_task

    if update.effective_user.id != OWNER_ID:
        return

    predicting = False
    if prediction_task:
        prediction_task.cancel()
        prediction_task = None

    await update.callback_query.answer("Stopped. ITM achieved!")
    await update.callback_query.message.reply_text("✅ Profit achieved. Bot stopped.")

# ==== MAIN ====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start_prediction))
    app.add_handler(CallbackQueryHandler(stop_prediction, pattern="itm"))

    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
