from datetime import datetime
import pytz

class Ticker:
    def __init__(self, code, timestamp, open, high, low, close, volume):
        self.code = code
        self.timestamp = timestamp
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume = volume

    @staticmethod
    def from_json(json_data):
        return Ticker(
            code=json_data['s'],
            timestamp=datetime.fromtimestamp(json_data['E'] / 1000, tz=pytz.timezone('Asia/Seoul')),
            open=json_data['k']['o'],
            high=json_data['k']['h'],
            low=json_data['k']['l'],
            close=json_data['k']['c'],
            volume=json_data['k']['v']
        )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (f'Ticker <code: {self.code}, timestamp: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}, '
                f'open: {self.open}, high: {self.high}, low: {self.low}, close: {self.close}, volume: {self.volume}>')
