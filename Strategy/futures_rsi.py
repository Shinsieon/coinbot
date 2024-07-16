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
client = UMFutures(key=api_key, secret=api_secret)

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

def check_rsi_signal(symbol):
    kl = klines(symbol)
    print(kl)
    rsi = ta.momentum.rsi(kl.Close, window=200)
    last_rsi = rsi.iloc[-1]
    if last_rsi > 70 : #과매수 구간
        return 'down'
    elif last_rsi < 30 : 
        return 'up'
    else :
        return 'none'
def get_tickers_usdt():
    tickers = []
    resp = client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

symbols = get_tickers_usdt()
for elem in symbols : 
    print(check_rsi_signal(klines(elem)))