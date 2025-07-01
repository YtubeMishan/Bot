import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters,
)

OWNER_ID = 7912905599
CHANNEL_USERNAME = "@wingo30s_predict"

# States for conversation
WAIT_PERIOD_ID = 1
WAIT_TYPE = 2
RUNNING = 3

# Globals to keep track of bot state
current_state = None
period_id = None
predict_type = None
send_task = None


def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != OWNER_ID:
            if update.message:
                await update.message.reply_text("❌ You are not authorized to use this bot.")
            elif update.callback_query:
                await update.callback_query.answer("❌ You are not authorized.", show_alert=True)
            return
        return await func(update, context)
    return wrapper


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_state, period_id, predict_type, send_task
    current_state = None
    period_id = None
    predict_type = None
    if send_task:
        send_task.cancel()
        send_task = None

    keyboard = [
        [InlineKeyboardButton("Start", callback_data="start")],
        [InlineKeyboardButton("Stop", callback_data="stop")],
    ]
    text = f"Wingo Predict 30s on {CHANNEL_USERNAME}"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.callback_query.answer("❌ Not authorized.", show_alert=True)
        return

    global current_state, period_id, predict_type, send_task

    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "start":
        if current_state == RUNNING:
            await query.edit_message_text("⏳ Prediction already running. Click ITM to stop.")
            return
        current_state = WAIT_PERIOD_ID
        await query.edit_message_text("Please send the **period ID** to start prediction.", parse_mode="Markdown")

    elif data == "stop":
        if send_task:
            send_task.cancel()
            send_task = None
        current_state = None
        period_id = None
        predict_type = None
        await query.edit_message_text("Stopped. Use /start to start again.")

    elif data == "itm":
        # Stop sending predictions on ITM click
        if send_task:
            send_task.cancel()
            send_task = None
        current_state = None
        period_id = None
        predict_type = None
        await query.edit_message_text("Prediction stopped by ITM button.\nUse /start to begin again.")


@owner_only
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_state, period_id, predict_type, send_task

    text = update.message.text.strip()

    if current_state == WAIT_PERIOD_ID:
        if not text.isdigit():
            await update.message.reply_text("Invalid period ID. Please send a numeric period ID.")
            return
        period_id = text
        current_state = WAIT_TYPE
        await update.message.reply_text(
            "Got period ID: *" + period_id + "*\nNow please send the prediction type: *small* or *big*",
            parse_mode="Markdown"
        )
    elif current_state == WAIT_TYPE:
        if text.lower() not in ["small", "big"]:
            await update.message.reply_text("Invalid type. Please send *small* or *big*.", parse_mode="Markdown")
            return
        predict_type = text.lower()
        current_state = RUNNING
        # Start sending predictions task
        send_task = asyncio.create_task(send_predictions(context))
        await update.message.reply_text(
            f"Signal Sending on {CHANNEL_USERNAME}\n"
            "Click ITM button when you get profit.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ITM", callback_data="itm")]])
        )
    else:
        await update.message.reply_text("Use /start to begin.")


async def send_predictions(context: ContextTypes.DEFAULT_TYPE):
    global period_id, predict_type, current_state, send_task

    next_period_id = int(period_id)
    try:
        while True:
            text = (
                f"Prediction for period: {next_period_id}\n"
                f"Type: {predict_type}\n"
                f"On {CHANNEL_USERNAME}"
            )
            try:
                await context.bot.send_message(CHANNEL_USERNAME, text)
            except Exception as e:
                print(f"Error sending message: {e}")

            next_period_id += 1
            await asyncio.sleep(30)

            if current_state != RUNNING:
                break
    except asyncio.CancelledError:
        print("send_predictions task cancelled")
    finally:
        send_task = None


async def main():
    app = ApplicationBuilder().token("7769439864:AAHoR601B2jzOzdIIlzShyTFO-twgsqcGkM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    print("🤖 Bot is running...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
