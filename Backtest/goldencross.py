import requests
import time
from datetime import datetime, timedelta
import pandas as pd
from decimal import Decimal
from Api.binance_api import BinanceAPI
class BacktestGoldenCross:
    def __init__(self, api, start_date, end_date, initial_capital=1000):
        self.api = api
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.portfolio = {'USDT': initial_capital}
        self.trade_log = []

    def get_historical_data(self, symbol, start, end):
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': '1d',
            'startTime': int(start.timestamp() * 1000),
            'endTime': int(end.timestamp() * 1000),
            'limit': 300
        }
        response = requests.get(url, params=params)
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['close'] = df['close'].astype(float)
        return df['close']

    def calculate_moving_averages(self, df, short_window=7, long_window=25):
        df['SMA_short'] = df['close'].rolling(window=short_window).mean()
        df['SMA_long'] = df['close'].rolling(window=long_window).mean()
        return df

    def run_backtest(self):
        self.coins = ['BTCUSDT']
        #symbols = [coin['symbol'] for coin in self.coins[:10]]  # 백테스트를 위해 상위 10개 코인만 사용
        symbols = self.coins

        for symbol in symbols:
            data = self.api.get_klines(symbol, '1d', 300)
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            df['close'] = df['close'].astype(float)
            df = self.calculate_moving_averages(df)
            
            for i in range(1, len(df)):
                if df['SMA_short'].iloc[i] > df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i-1] <= df['SMA_long'].iloc[i-1]:  # 골든 크로스 발생
                    if 'USDT' in self.portfolio and self.portfolio['USDT'] > 0:
                        amount_to_invest = self.portfolio['USDT']
                        quantity = amount_to_invest / df['close'].iloc[i]
                        self.portfolio[symbol] = quantity
                        self.portfolio['USDT'] -= amount_to_invest
                        self.trade_log.append({
                            'date': df.index[i],
                            'symbol': symbol,
                            'action': 'BUY',
                            'price': df['close'].iloc[i],
                            'quantity': quantity
                        })
                elif df['SMA_short'].iloc[i] < df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i-1] >= df['SMA_long'].iloc[i-1]:  # 데드 크로스 발생
                    if symbol in self.portfolio and self.portfolio[symbol] > 0:
                        quantity = self.portfolio[symbol]
                        amount = quantity * df['close'].iloc[i]
                        self.portfolio['USDT'] += amount
                        del self.portfolio[symbol]
                        self.trade_log.append({
                            'date': df.index[i],
                            'symbol': symbol,
                            'action': 'SELL',
                            'price': df['close'].iloc[i],
                            'quantity': quantity
                        })

        self.evaluate_performance()

    def evaluate_performance(self):
        final_value = self.portfolio['USDT']
        for symbol, quantity in self.portfolio.items():
            if symbol != 'USDT':
                df = self.get_historical_data(symbol, self.start_date, self.end_date)
                final_price = df.iloc[-1]
                final_value += quantity * final_price

        profit = final_value - self.initial_capital
        print(f"Initial Capital: ${self.initial_capital}")
        print(f"Final Value: ${final_value}")
        print(f"Profit: ${profit}")
        print("Trade Log:")
        for log in self.trade_log:
            print(log)

# Usage
api = BinanceAPI()
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
backtest_bot = BacktestGoldenCross(api, start_date, end_date)
backtest_bot.run_backtest()
