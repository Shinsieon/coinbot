from Notifier.telegram_notifier import TelegramNotifier
from LiveStream.websocket_client import WebSocketClient
from Balance.balance_checker import BalanceChecker

def receiver(message):
    print(message)
if __name__ == "__main__":
    ws_client = WebSocketClient("wss://stream.binance.com:9443/ws", receiver)
    ws_client.run()
    # if __name__ == '__main__':
    #     checker = BalanceChecker()
    #     checker.check_balances()

    