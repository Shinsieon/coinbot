from telegram_notifier import TelegramNotifier
from websocket_client import WebSocketClient
import configparser
from balance_checker import BalanceChecker

config = configparser.ConfigParser()
config.read('config.ini')

API_KEY = config['binance']['api_key']
API_SECRET = config['binance']['api_secret']
BOT_TOKEN = config['telegram']['bot_token']
CHAT_ID = config['telegram']['chat_id']
if __name__ == "__main__":
    # websocket_url = "wss://stream.binance.com:9443/ws"
    # bot_token = "BOT_TOKEN"
    # chat_id = CHAT_ID

    # telegram_notifier = TelegramNotifier(bot_token, chat_id)
    # ws_client = WebSocketClient(websocket_url, telegram_notifier)
    # ws_client.run()
    if __name__ == '__main__':
        checker = BalanceChecker()
        checker.check_balances()

    