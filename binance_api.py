import requests
import time
import hmac
import hashlib
import configparser
from binance.spot import Spot

#request 모듈을 사용한 정식 API 요청 방법
class BinanceAPI:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.api_key = self.config['binance']['api_key']
        self.api_secret = self.config['binance']['api_secret']
        self.base_url = 'https://api.binance.com'

    def create_signature(self, query_string):
        return hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    #잔고조회
    def get_account_info(self):
        endpoint = '/api/v3/account'
        timestamp = int(time.time() * 1000)
        query_string = f'timestamp={timestamp}'
        signature = self.create_signature(query_string)
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        url = f'{self.base_url}{endpoint}?{query_string}&signature={signature}'
        response = requests.get(url, headers=headers)
        return response.json()
    
#binance-connector 을 사용한 API 조회 방법
#https://github.com/binance/binance-connector-python
class BinanceConnector:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.api_key = self.config['binance']['api_key']
        self.api_secret = self.config['binance']['api_secret']

    def get_account_info(self):
        client = Spot(api_key=self.api_key, api_secret=self.api_secret)
        return client.account()
