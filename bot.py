import time
import requests
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7769439864:AAFFaISjadlMAgY-tAr-2BQ5wJZdu85U6QU"  # your bot token
CHANNEL_ID = "@Wingo30sec_PredictChannel"  # your telegram channel or chat id

bot = Bot(token=BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://dkwin9.com/",
    "Origin": "https://dkwin9.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

# Optional: fill with cookies copied from browser if needed, else keep empty
COOKIES = {
    # "cookie_name": "cookie_value",
}

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def fetch_results():
    try:
        params = {"ts": int(time.time() * 1000)}
        resp = requests.get(API_URL, headers=HEADERS, cookies=COOKIES, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        logging.error(f"Error fetching result: {e}")
        return None

def parse_results(data):
    # Extract last 2 results: assume 'result' field contains 'big' or 'small'
    # You need to check exact JSON structure from API response
    try:
        history = data['result']['data']
        last_two = history[:2]  # latest two rounds
        last_results = []
        last_periods = []
        for item in last_two:
            # Example: "result" field might be number or string
            # You must map to 'big' or 'small'
            res = item['result']  # adjust based on actual data key
            period = item['period']
            # Assuming result is numeric, define small/big
            # Change threshold as per your game rules
            if isinstance(res, str):
                # If already 'big' or 'small', use directly
                result_str = res.lower()
            else:
                # numeric result to big/small, example threshold 5
                result_str = "big" if int(res) > 5 else "small"

            last_results.append(result_str)
            last_periods.append(period)
        return last_results, last_periods[0]  # last_results[0] = latest result, period is the latest period
    except Exception as e:
        logging.error(f"Error parsing result data: {e}")
        return None, None

def predict_next(last_two_results):
    # Your algorithm:
    # If last 2 results small => predict big until big appears, then wait for 2 small again
    # If last 2 results big => predict small until small appears, then wait for 2 big again

    if len(last_two_results) < 2:
        return None

    last1, last2 = last_two_results[0], last_two_results[1]

    # Initialize static variables to hold state
    if not hasattr(predict_next, "waiting_for_big"):
        predict_next.waiting_for_big = False
        predict_next.waiting_for_small = False

    if last1 == last2 == "small":
        predict_next.waiting_for_big = True
        predict_next.waiting_for_small = False
        return "big"
    elif last1 == last2 == "big":
        predict_next.waiting_for_small = True
        predict_next.waiting_for_big = False
        return "small"

    # if waiting_for_big is True, predict big until big appears
    if predict_next.waiting_for_big:
        if last1 == "big":
            # stop waiting, wait for 2 small
            predict_next.waiting_for_big = False
            return None
        else:
            return "big"

    # if waiting_for_small is True, predict small until small appears
    if predict_next.waiting_for_small:
        if last1 == "small":
            # stop waiting, wait for 2 big
            predict_next.waiting_for_small = False
            return None
        else:
            return "small"

    return None

def format_message(period, prediction):
    msg = f"""✅𝗣𝗲𝗿𝗶𝗼𝗱 𝗡𝘂𝗺𝗯𝗲𝗿

⏩⏩⏩⏩  ⏪⏪⏪⏪ {period}

⚜️𝗪𝗶𝗻𝗴𝗼 𝟯𝟬𝘀𝗲𝗰 ⏪

❤️‍🔥𝑷𝒓𝒆𝒅𝒊𝒄𝒕 ⚡️⏩⏩  ⏪⏪⚡️ {prediction.upper()}

💲𝗚𝗮𝗺𝗲 𝗡𝗮𝗺𝗲👇👇
          𝗪𝗶𝗻𝗴𝗼

Maintain ⚜️

𝟭𝘀𝘁 𝗕𝗜𝗗 ⏩ 𝟭𝘅 𝗠𝗮𝗶𝗻𝘁𝗮𝗶𝗻

𝗜𝗙 𝗪𝗜𝗡 𝗔𝗴𝗮𝗶𝗻 𝟭𝘅♻️

𝗜𝗙 𝗟𝗢𝗦𝗦  𝟮𝘅 
𝗔𝗚𝗔𝗜𝗡 𝗟𝗢𝗦𝗦 𝟯𝘅 𝗟𝗢𝗦𝗦 𝟰𝘅 𝗟𝗢𝗦𝗦 𝟱𝘅 𝗟𝗢𝗦𝗦 𝟲𝘅 𝗟𝗢𝗦𝗦 𝟳𝘅 𝗟𝗢𝗦𝗦 𝟴𝘅

𝟴𝘅 𝗪𝗶𝗹𝗹 𝗦𝘂𝗽𝗲𝗿𝗦𝗵𝗼𝘁🤑💲
"""
    return msg

def main():
    while True:
        data = fetch_results()
        if data:
            last_results, last_period = parse_results(data)
            if last_results and last_period:
                prediction = predict_next(last_results)
                if prediction:
                    message = format_message(last_period, prediction)
                    try:
                        bot.send_message(CHANNEL_ID, message)
                        logging.info(f"Sent prediction for period {last_period}: {prediction}")
                    except Exception as e:
                        logging.error(f"Telegram send error: {e}")
                else:
                    logging.info("No prediction to send this round.")
            else:
                logging.warning("Failed to parse results.")
        else:
            logging.warning("Failed to fetch results.")
        time.sleep(30)  # repeat every 30 seconds

if __name__ == "__main__":
    main()
