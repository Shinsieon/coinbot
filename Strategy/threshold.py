
# 이 전략은 다음과 같은 단계로 구성된 자동화된 코인 거래 봇입니다:

# 전략 요약
# 초기 자본: N달러
# 목표: 거래량이 가장 많은 다섯 개의 코인을 추출하여 매수하고, 가격이 일정 수준(Threshold)에 도달하면 매도
# Threshold: 5% (코인 가격이 5% 상승하면 매도)
# Threshold: 3% (코인 가격이 3% 하락하면 매도)
# 단계별 설명
# 1. 가장 거래량이 많은 다섯 개의 코인 추출
# Binance API를 사용하여 지난 24시간 동안 거래량이 가장 많은 다섯 개의 코인을 추출합니다.
# 2. 코인 매수
# 초기 자본 10달러를 다섯 개의 코인에 균등하게 분배하여 각 코인을 매수합니다.
# 예를 들어, 각 코인에 2달러씩 투자하여 매수합니다.
# 3. Threshold 전략으로 매매
# 코인의 가격이 매수 가격 대비 5% 상승 혹은 3% 하락하면 해당 코인을 매도합니다.
# 매수한 코인의 현재 가격을 주기적으로 확인하고, 가격이 5% 이상 상승 or 3%이상 하락했는지 확인합니다.
# 상승 기준에 도달하면 해당 코인을 매도하여 이익을 실현합니다.

import requests
import time
from Notifier.telegram_notifier import TelegramNotifier
from Balance.balance_checker import BalanceChecker
from Api.binance_api import BinanceAPI

class Threshold:
    def __init__(self, api = BinanceAPI()):
        self.api = api
        self.coins = []
        self.up_threshold = 0.05  # 5% threshold for selling
        self.down_threshold = -0.03  # -3% threshold for stop-loss
        self.messenger = TelegramNotifier()
        self.usdt_amount = 0

    def initialize_portfolio(self):
        self.coins = self.api.get_volume_coins()
        usdt_amount = list(filter(lambda n : n['asset'] == 'USDT', BalanceChecker().get_have_balances()))
        if len(usdt_amount) == 0 :
            return
        
        self.usdt_amount = float(usdt_amount[0]['free'])
        self.messenger.send_message(f"현재 USDT 보유량 {self.usdt_amount} 입니다.")
        
        amount_per_coin = self.usdt_amount / len(self.coins)
        orders_summary = []
        for coin in self.coins:
            symbol = f"{coin}"
            current_price = self.api.get_current_price(symbol)
            quantity = amount_per_coin / float(current_price)
            try:
                result = self.api.create_order(symbol, 'BUY', 'LIMIT', quantity, current_price, 'GTC')
                order_summary = f"코인: {symbol}, 현재 가격: {current_price}, 주문량: {quantity}, 결과: {result}"
            except Exception as e:
                order_summary = f"코인: {symbol}, 현재 가격: {current_price}, 주문량: {quantity}, 에러: {e}"
            orders_summary.append(order_summary)
        
        # orders_summary를 하나의 문자열로 결합
        orders_message = "\n".join(orders_summary)
        
        # 메시지 전송
        self.messenger.send_message(f"주문 결과:\n{orders_message}")
            

    def check_threshold_and_trade(self):
        account_info = self.api.get_account_info()
        for asset in account_info['balances']:
            if asset['asset'] in self.coins:
                symbol = f"{asset['asset']}"
                quantity = float(asset['free'])
                current_price = float(self.api.get_current_price(symbol))
                purchase_price = self.usdt_amount / len(self.coins) / quantity

                change_ratio = (current_price - purchase_price) / purchase_price
                if change_ratio >= self.up_threshold:
                    self.api.create_order(symbol, 'SELL', 'MARKET', quantity)
                    self.messenger.send_message(f"Sold {quantity} of {symbol} at {current_price}")
                elif change_ratio <= self.down_threshold:
                    self.api.create_order(symbol, 'SELL', 'MARKET', quantity)
                    self.messenger.send_message(f"Stop-loss: Sold {quantity} of {symbol} at {current_price}")

    def run(self):
        self.initialize_portfolio()
        while True:
            self.check_threshold_and_trade()
            time.sleep(30)  # Check every 60 seconds

api = BinanceAPI()
bot = Threshold(api)
bot.run()