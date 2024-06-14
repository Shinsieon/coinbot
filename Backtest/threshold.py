import requests
import time
from datetime import datetime, timedelta
import pandas as pd
from decimal import Decimal
from Api.binance_api import BinanceAPI

class BacktestThreshold:
    def __init__(self, api, start_date, end_date, initial_capital=1000):
        self.api = api
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.up_threshold = 0.05  # 5% threshold for selling
        self.down_threshold = -0.03  # -3% threshold for stop-loss
        self.coins = []
        self.portfolio = {}
        self.trade_log = []

    def get_historical_data(self, symbol, start, end):
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': '1d',
            'startTime': int(start.timestamp() * 1000),
            'endTime': int(end.timestamp() * 1000)
        }
        response = requests.get(url, params=params)
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['close'] = df['close'].astype(float)
        return df['close']

    def initialize_portfolio(self):
        # Extract top 5 coins by volume
        self.coins = self.api.get_volume_coins()
        self.coins = list(filter(lambda n: 'USDT' in n['symbol'], self.coins))
        self.coins = sorted(self.coins, key=lambda x: float(x['volume']), reverse=True)
        self.coins = [coin['symbol'] for coin in self.coins[:5]]

        # Allocate initial capital equally among the top 5 coins
        amount_per_coin = self.initial_capital / len(self.coins)
        for coin in self.coins:
            self.portfolio[coin] = {
                'amount': amount_per_coin,
                'quantity': 0,
                'purchase_price': 0
            }

    def run_backtest(self):
        self.initialize_portfolio()

        for coin in self.coins:
            symbol = f"{coin}"
            df = self.get_historical_data(symbol, self.start_date, self.end_date)

            for date, price in df.items():
                if self.portfolio[coin]['quantity'] == 0:  # Buy
                    self.portfolio[coin]['quantity'] = self.portfolio[coin]['amount'] / price
                    self.portfolio[coin]['purchase_price'] = price
                    self.trade_log.append({
                        'date': date,
                        'symbol': coin,
                        'action': 'BUY',
                        'price': price,
                        'quantity': self.portfolio[coin]['quantity']
                    })
                else:
                    purchase_price = self.portfolio[coin]['purchase_price']
                    change_ratio = (price - purchase_price) / purchase_price
                    if change_ratio >= self.up_threshold or change_ratio <= self.down_threshold:  # Sell
                        self.trade_log.append({
                            'date': date,
                            'symbol': coin,
                            'action': 'SELL',
                            'price': price,
                            'quantity': self.portfolio[coin]['quantity']
                        })
                        self.portfolio[coin]['quantity'] = 0

        self.evaluate_performance()

    def evaluate_performance(self):
        final_value = 0
        for coin in self.coins:
            symbol = f"{coin}"
            df = self.get_historical_data(symbol, self.start_date, self.end_date)
            last_price = df.iloc[-1]
            if self.portfolio[coin]['quantity'] > 0:
                final_value += self.portfolio[coin]['quantity'] * last_price
            else:
                final_value += self.portfolio[coin]['amount']

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
backtest_bot = BacktestThreshold(api, start_date, end_date)
backtest_bot.run_backtest()
