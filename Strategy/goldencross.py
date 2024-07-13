from Notifier.telegram_notifier import TelegramNotifier
from Balance.balance_checker import BalanceChecker
from Api.binance_api import BinanceAPI
import pandas as pd
import time
class GoldenCross:
    def __init__(self, api = BinanceAPI()):
        self.api = api
        self.messenger = TelegramNotifier()
        self.balance = BalanceChecker()

    def calculate_moving_averages(self, df, short_window=7, long_window=25):
        df['SMA_short'] = df['close'].rolling(window=short_window).mean()
        df['SMA_long'] = df['close'].rolling(window=long_window).mean()
        return df

    def find_golden_crosses(self, symbols):
        up_golden_crosses = []
        down_golden_crosses = []
        for symbol in symbols:
            data = self.api.get_klines(symbol, '1d', 300)
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            df['close'] = df['close'].astype(float)
            df = self.calculate_moving_averages(df)
            if df['SMA_short'].iloc[-1] > df['SMA_long'].iloc[-1] and df['SMA_short'].iloc[-2] <= df['SMA_long'].iloc[-2]: #상승 골든크로스
                up_golden_crosses.append(symbol)
            elif df['SMA_short'].iloc[-1] < df['SMA_long'].iloc[-1] and df['SMA_short'].iloc[-2] >= df['SMA_long'].iloc[-2]: #하락 골든크로스
                down_golden_crosses.append(symbol)
        return [up_golden_crosses , down_golden_crosses]
        
    def run(self):
        self.coins = self.api.get_volume_coins()
        self.coins = list(filter(lambda n : 'USDT' in n['symbol'], self.coins))
        self.coins = sorted(self.coins, key=lambda x: float(x['volume']), reverse=True)
        symbols = [coin['symbol'] for coin in self.coins[:100]]
        golden_crosses = self.find_golden_crosses(symbols)
        print("Golden Crosses:", golden_crosses)

gd = GoldenCross()
while(True):
    gd.run()
    time.sleep(60)