import requests
import time
import hmac
import hashlib
import configparser
import math
from decimal import Decimal, ROUND_DOWN
#request 모듈을 사용한 정식 API 요청 방법
class BinanceAPI:
    def __init__(self, config_file='Config/config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.api_key = self.config['binance']['api_key']
        self.api_secret = self.config['binance']['api_secret']
        self.base_url = 'https://api.binance.com'

    def get_timestamp(self):
        return int(time.time() * 1000)

    def get_query_string(self):
        timestamp = self.get_timestamp()
        query_string = f'timestamp={timestamp}'
        return query_string

    def create_signature(self, query_string):
        return hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    #잔고조회
    def get_account_info(self):
        endpoint = '/api/v3/account'
        query_string = self.get_query_string()
        signature = self.create_signature(query_string)
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        url = f'{self.base_url}{endpoint}?{query_string}&signature={signature}'
        response = requests.get(url, headers=headers)
        return response.json()
    
     # 현재 가격을 반환합니다.
    def get_current_price(self, symbol):
        url = f"{self.base_url}/api/v3/ticker/price"
        params = {
            'symbol': symbol
        }
        response = requests.get(url, params=params)
        print(response.json())
        return response.json()['price']
    
    def get_volume_coins(self):
        url = f"{self.base_url}/api/v3/ticker/24hr"
        response = requests.get(url)
        data = response.json()
        return data
        
    def get_exchangeInfo(self, symbol):
        url = f"{self.base_url}/api/v3/exchangeInfo"
        response = requests.get(url)
        data = response.json()
        return data
    
    def get_lot_size(self, symbol):
        url = f"{self.base_url}/api/v3/exchangeInfo"
        response = requests.get(url)
        data = response.json()
        for symbol_info in data['symbols']:
            if symbol_info['symbol'] == symbol:
                for filter in symbol_info['filters']:
                    if filter['filterType'] == 'LOT_SIZE':
                        return {
                            'stepSize': filter['stepSize'],
                            'minQty': filter['minQty'],
                            'maxQty': filter['maxQty']
                        }
        return None
    
    #주문 정보를 가져옵니다.
    def get_trade_info(self, symbol):
        endpoint = '/api/v3/myTrades'
        params = {
            'symbol': symbol,
            'timestamp': self.get_timestamp()  # 필요에 따라 변경 가능
        }
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
        

    #주문 가격을 가져옵니다.
    def get_order_history(self, symbol):
        endpoint = '/api/v3/allOrders'
        params = {
            'symbol': symbol,
            'limit': 1000  # 필요에 따라 변경 가능
        }
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def round_quantity(self, quantity, step_size):
        step_size_decimal = Decimal(step_size)
        quantity_decimal = Decimal(quantity)
        return float(quantity_decimal.quantize(step_size_decimal, rounding=ROUND_DOWN))

    def create_order(self, symbol, side, order_type, quantity, price=None, time_in_force='GTC'):
        endpoint = '/api/v3/order'
        timestamp = int(time.time() * 1000)
        lot_size = self.get_lot_size(symbol)
        if lot_size:
            step_size = lot_size['stepSize']
            min_qty = Decimal(lot_size['minQty'])
            max_qty = Decimal(lot_size['maxQty'])
            quantity = Decimal(quantity)
            if quantity < min_qty or quantity > max_qty:
                raise ValueError(f"Quantity {quantity} is out of bounds. Must be between {min_qty} and {max_qty}.")
            quantity = math.floor(self.round_quantity(quantity, step_size))
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'timestamp': timestamp,
            'timeInForce' : time_in_force
        }
        if price:
            params['price'] = price
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        signature = self.create_signature(query_string)
        params['signature'] = signature
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        url = f'{self.base_url}{endpoint}'
        response = requests.post(url, headers=headers, params=params)
        return response.json()
    
    def get_klines(self, symbol, interval='1d', limit=100):
        url = f"{self.base_url}/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data
  