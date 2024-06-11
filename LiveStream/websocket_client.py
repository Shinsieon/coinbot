import websocket
import json
from LiveStream.ticker import Ticker

class WebSocketClient:
    def __init__(self, url, notifier):
        self.url = url
        self.notifier = notifier
        self.ws = None

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'k' in data:
            ticker = Ticker.from_json(data)
            self.notifier(ticker)
            

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        params = {
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@kline_1m"  # 1분 간격의 Kline 데이터 스트림 구독
            ],
            "id": 1
        }
        ws.send(json.dumps(params))
        print("Sent subscribe request")

    def run(self):
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()
        