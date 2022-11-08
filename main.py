import json
import requests
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from twilio.rest import Client

with open("config.json") as json_data_file:
    config_data = json.load(json_data_file)

ALPHA_API_KEY = config_data["alphavantage"]["api_key"]
NEWSAPI_API_KEY = config_data["newsapi"]["api_key"]
TWILIO_ACCOUNT_SID = config_data["twilio"]["account_sid"]
TWILIO_AUTH_TOKEN = config_data["twilio"]["auth_token"]
SENDER = config_data["twilio"]["sender"]
RECEIVER = config_data["twilio"]["receiver"]

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

today_minus_1 = datetime.strftime(datetime.today() - timedelta(1), '%Y-%m-%d')
today_minus_2 = datetime.strftime(datetime.today() - timedelta(2), '%Y-%m-%d')

## STEP 1: Get stock data
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHA_API_KEY
}
stock_response = requests.get(f'https://www.alphavantage.co/query', params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()

minus_1_close = float(stock_data["Time Series (Daily)"][today_minus_1]["4. close"])
minus_2_close = float(stock_data["Time Series (Daily)"][today_minus_2]["4. close"])
stock_diff = minus_1_close - minus_2_close
if stock_diff >= 0:
    symbol = "🔺"
else:
    symbol = "🔻"

abs_stock_chg_pct = round(abs(stock_diff)*100/minus_2_close,2)
message = f"{STOCK}: {symbol}{abs_stock_chg_pct}%\n"

## STEP 2: Get latest headline
news_params = {
    "q": COMPANY_NAME,
    "apikey": NEWSAPI_API_KEY
}
if abs_stock_chg_pct >= 0.1:
    news_response = requests.get(f'https://newsapi.org/v2/everything', params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()
    message += f"Headline: {news_data['articles'][0]['title']}\n"
    message += f"URL: {news_data['articles'][0]['url']}\n"

## STEP 3: Send message
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message,
        from_=SENDER,
        to=RECEIVER
    )

