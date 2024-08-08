import configparser
from binance.um_futures import UMFutures
import ta
import pandas as pd
from time import sleep
from binance.error import ClientError
import sys

api_key = input("binance api key 를 입력해주세요 : ")
api_secret = input("binance security key를 입력해주세요 : ")
client = UMFutures(key=api_key, secret=api_secret)
type = 'ISOLATED'

def get_balance_usdt():
    try:
        response = client.balance(recvWindow=6000)
        for elem in response:
            if elem['asset'] == 'USDT':
                return float(elem['balance'])
            
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers
try:
    account = client.account()
    print(f"현재 보유 USDT 는 {get_balance_usdt()} 입니다.")
except ClientError as error:
        print(
            "잘못된 API KEY 입니다."
        )
        sys.exit(1)

volume = int(input("주문당 투자금액을 입력해주세요(단위 : USDT) : "))
leverage = int(input("레버리지를 입력해주세요 : "))
sl = float(input("손절가격(상승/하락 비율)을 백분위 단위로 입력해주세요. (예시 : 1% = 0.01) "))
tp = float(input("익절가격(상승/하락 비율)을 백분위 단위로 입력해주세요. (예시 : 1% = 0.01) "))
max_qty = int(input("최대 주문 수를 입력해주세요. "))
 
def klines(symbol):

    try:
        resp = pd.DataFrame(client.klines(symbol, '1h'))
        resp = resp.iloc[:, :6]
        resp.columns = ['Time','Open','High', 'Low','Close','Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit='ms')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

def set_leverage(symbol, level):
    try:
        response = client.change_leverage(
            symbol=symbol, leverage = level, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

def set_mode(symbol, type):
    try:
        response = client.change_margin_type(
            symbol =symbol, marginType = type, recvWindow=6000
        )
        print(response)
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

#코인의 허용되는 가격 소수점 자리수를 반환합니다.
def get_price_precision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['pricePrecision']
        
#코인의 허용되는 수량 소수점 자리수를 반환합니다.
def get_qty_precision(symbol):
    resp = client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['quantityPrecision']
        
def open_order(symbol, side):
    price = float(client.ticker_price(symbol)['price'])
    qty_precision = get_qty_precision(symbol)
    price_precision = get_price_precision(symbol)
    qty = round(volume /price, qty_precision)
    if side == 'buy':
        try:
            resp1 = client.new_order(symbol=symbol, side='BUY', type='LIMIT', quantity = qty, timeInForce ='GTC', price=price)
            print(symbol, side, "placing order")
            print(resp1)
            sleep(2)
            sl_price = round(price - price*sl, price_precision)
            resp2 = client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(resp2)
            sleep(2)
            tp_price = round(price + price*tp, price_precision)
            resp3 = client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(resp3)
        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
    elif side == 'sell':
        try:
            resp1 = client.new_order(symbol=symbol, side='SELL', type='LIMIT', quantity = qty, timeInForce ='GTC', price=price)
            print(symbol, side, "placing order")
            print(resp1)
            sleep(2)
            sl_price = round(price + price*sl, price_precision)
            resp2 = client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
            print(resp2)
            sleep(2)
            tp_price = round(price - price*tp, price_precision)
            resp3 = client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
            print(resp3)
        except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

def get_pos():
    try:
        resp = client.get_position_risk()
        pos = []
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                pos.append(elem['symbol'])
        return pos
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

def close_open_orders(symbol):
    try:
        response = client.cancel_open_orders(symbol = symbol, recvWindow=2000)
        print(response)
    except ClientError as error:
            print(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

def check_macd_ema(symbol):
    kl = klines(symbol)
    macd = ta.trend.macd_diff(kl.Close)
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if macd.iloc[-3] < 0 and macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema.iloc[-1] < kl.Close.iloc[-1]:
        return 'up'
    if macd.iloc[-3] > 0 and macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema.iloc[-1] > kl.Close.iloc[-1]:
        return 'down'
    else:
        return 'none'
    
def check_orders():
    try:
        response = client.get_orders(recvWindow=6000)
        sym = []
        for elem in response:
            sym.append(elem['symbol'])
        return sym
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
    
orders = 0
symbol = ''
# getting all symbols from Binace Futures list:
symbols = get_tickers_usdt()

while True:
    pos = get_pos()
    ord = []
    ord = check_orders()
    print(f'{len(pos)} 개의 포지션이 있습니다.')
    for elem in ord:
        if not elem in pos:
            close_open_orders(elem)
    

    if len(pos) < max_qty:
        for elem in symbols:
            signal = check_macd_ema(elem)
            if signal == 'up' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                print('Found BUY signal for ', elem)
                set_mode(elem, type)
                sleep(1)
                set_leverage(elem, leverage)
                sleep(1)
                print('Placing order for ', elem)
                open_order(elem, 'buy')
                symbol = elem
                #if len(positions) > 5 :
                order = True
                break

            if signal == 'down' and elem != 'USDCUSDT' and not elem in pos and not elem in ord and elem != symbol:
                print('Found SELL signal for ', elem)
                set_mode(elem, type)
                sleep(1)
                set_leverage(elem, leverage)
                sleep(1)
                print('Placing order for ', elem)
                open_order(elem, 'sell')
                symbol = elem
                #if len(positions) > 5 :
                order = True
                break
    print("1분동안 대기 ... ")
    sleep(60)          