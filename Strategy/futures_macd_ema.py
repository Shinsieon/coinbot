import configparser
from binance.um_futures import UMFutures
import ta
import pandas as pd
from time import sleep
from binance.error import ClientError

config = configparser.ConfigParser()
config.read('Config/config.ini')
api_key = config['binance']['api_key']
api_secret = config['binance']['api_secret']
print(api_key) 

client = UMFutures(key=api_key, secret=api_secret)

tp = 0.01 #1% 오르면 매도
sl = 0.01 #1% 떨어져도 매도
volume = 200
leverage = 10 #10배율이므로 한 계약 단위는 5USDT
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


print("My balance is : ", get_balance_usdt())

def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

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

def check_position():
    positions = []
    try:
        resp = client.get_position_risk()
        for elem in resp:
            if float(elem['positionAmt'])!= 0:
                positions.append(elem)
        
        return positions
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
    if ta.trend.macd_diff(kl.Close).iloc[-1] > 0 and ta.trend.macd_diff(kl.Close).iloc[-2] < 0 \
        and ta.trend.ema_indicator(kl.Close, window=200).iloc[-1] < kl.Close.iloc[-1]:
            return 'up'
    elif ta.trend.macd_diff(kl.Close).iloc[-1] < 0 and ta.trend.macd_diff(kl.Close).iloc[-2] > 0 \
        and ta.trend.ema_indicator(kl.Close, window=200).iloc[-1] > kl.Close.iloc[-1]:
            return 'down'
    
    else : 
        return 'none'
    
order = False
symbol = ''
symbols = get_tickers_usdt()

while True:
    positions = check_position()
    print(f'You have {len(positions)} opened positions')
    if len(positions) == 0:
        order = False
        if symbol != '':
            close_open_orders(symbol)

    my_symbols = [item['symbol'] for item in positions]

    if order == False:
        for elem in symbols : 
            signal = check_macd_ema(elem)
            if signal == 'up' and elem not in my_symbols:
                print('Found BUY signal for ', elem)
                set_mode(elem, type)
                sleep(1)
                set_leverage(elem, leverage)
                sleep(1)
                print('Placing order for ', elem)
                open_order(elem, 'buy')
                symbol = elem
                if len(positions) > 5 :
                    order = True
                break

            if signal == 'down' and elem not in my_symbols:
                print('Found SELL signal for ', elem)
                set_mode(elem, type)
                sleep(1)
                set_leverage(elem, leverage)
                sleep(1)
                print('Placing order for ', elem)
                open_order(elem, 'sell')
                symbol = elem
                if len(positions) > 5 :
                    order = True
                break
    print("Waiting 60 secs")
    sleep(60)          