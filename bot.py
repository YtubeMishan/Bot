import time
import requests
import logging
from telegram import Bot

# === CONFIG ===
BOT_TOKEN = "7769439864:AAFFaISjadlMAgY-tAr-2BQ5wJZdu85U6QU"
CHANNEL_ID = "-1002898322642"  # Replace with your actual channel ID

bot = Bot(token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

history = []
last_period = None
predicted_for = None

def fetch_latest_result():
    try:
        ts = int(time.time() * 1000)
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json?ts={ts}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://dkwin9.com/",
            "Origin": "https://dkwin9.com",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Raw Response Text:", response.text[:300])

        response.raise_for_status()
        data = response.json()

        result_list = data.get("list", [])
        if not result_list:
            logging.warning("Empty result list in API response.")
            return None, None

        latest = result_list[0]
        period = latest.get("issueNo")
        result = int(latest.get("openCode"))
        return period, result

    except Exception as e:
        logging.error(f"Error fetching result: {e}")
        return None, None

def classify(value):
    return "SMALL" if value <= 4 else "BIG"

def make_prediction():
    if len(history) < 2:
        return None, None

    last_two = [classify(r) for r in history[-2:]]

    if last_two == ["SMALL", "SMALL"]:
        return "BIG", "Last 2 were SMALL"
    elif last_two == ["BIG", "BIG"]:
        return "SMALL", "Last 2 were BIG"
    else:
        return None, "Waiting for 2 of same"

def send_prediction(period, prediction, reason):
    emoji = "🔴" if prediction == "BIG" else "🔵"
    msg = (
        f"✅𝗣𝗲𝗿𝗶𝗼𝗱 𝗡𝘂𝗺𝗯𝗲𝗿\n\n"
        f"⏩⏩⏩⏩  ⏪⏪⏪⏪  {period}\n\n"
        f"⚜️𝗪𝗶𝗻𝗴𝗼 𝟯𝟬𝘀𝗲𝗰 ⏪\n\n"
        f"❤️‍🔥𝑷𝒓𝒆𝒅𝒊𝒄𝒕 ⚡️⏩⏩  ⏪⏪⚡️  {prediction} {emoji}\n\n"
        f"💲𝗚𝗮𝗺𝗲 𝗡𝗮𝗺𝗲👇👇\n"
        f"         𝗪𝗶𝗻𝗴𝗼\n\n"
        f"Maintain ⚜️\n\n"
        f"𝟭𝘀𝘁 𝗕𝗜𝗗 ⏩ 𝟭𝘅 𝗠𝗮𝗶𝗻𝘁𝗮𝗶𝗻\n\n"
        f"𝗜𝗙 𝗪𝗜𝗡 𝗔𝗴𝗮𝗶𝗻 𝟭𝘅♻️\n\n"
        f"𝗜𝗙 𝗟𝗢𝗦𝗦 𝟮𝘅\n"
        f"𝗔𝗚𝗔𝗜𝗡 𝗟𝗢𝗦𝗦 𝟯𝘅 𝗟𝗢𝗦𝗦 𝟰𝘅 𝗟𝗢𝗦𝗦 𝟱𝘅 𝗟𝗢𝗦𝗦 𝟲𝘅 𝗟𝗢𝗦𝗦 𝟳𝘅 𝗟𝗢𝗦𝗦 𝟴𝘅\n\n"
        f"𝟴𝘅 𝗪𝗶𝗹𝗹 𝗦𝘂𝗽𝗲𝗿𝗦𝗵𝗼𝘁🤑💲"
    )
    try:
        bot.send_message(chat_id=CHANNEL_ID, text=msg)
        logging.info(f"Sent prediction: {prediction} for round {period}")
    except Exception as e:
        logging.error(f"Error sending prediction: {e}")

if __name__ == "__main__":
    while True:
        period, result = fetch_latest_result()

        if period and result:
            if period != last_period:
                history.append(result)
                last_period = period
                logging.info(f"New result: {result} in round {period}")

                prediction, reason = make_prediction()

                if prediction and predicted_for != period:
                    send_prediction(period, prediction, reason)
                    predicted_for = period

        time.sleep(5)
