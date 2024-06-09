from telegram_notifier import TelegramNotifier
from websocket_client import WebSocketClient

if __name__ == "__main__":
    websocket_url = "wss://stream.binance.com:9443/ws"
    bot_token = "7318188193:AAHknSIE0wCd78yaqJXfBxwGNBef22ycu1k"
    chat_id = "7316218092"

    telegram_notifier = TelegramNotifier(bot_token, chat_id)
    ws_client = WebSocketClient(websocket_url, telegram_notifier)
    ws_client.run()

    