#future binance api
#바이낸스 선물 api
from Api.binance_api import BinanceAPI
import configparser
import requests
class FBinanceAPI(BinanceAPI):
    def __init__(self, config_file='Config/config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.api_key = self.config['binance']['api_key']
        self.api_secret = self.config['binance']['api_secret']
        self.base_url = 'https://fapi.binance.com'

    def get_account_info(self):
        endpoint = '/fapi/v2/account'
        query_string = self.get_query_string()
        signature = self.create_signature(query_string)
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        url = f'{self.base_url}{endpoint}?{query_string}&signature={signature}'
        response = requests.get(url, headers=headers)
        return response.json()
    
    #GET /fapi/v1/income
    def get_income_history(self):
        endpoint = '/fapi/v1/income'
        query_string = self.get_query_string()
        signature = self.create_signature(query_string)
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        url = f'{self.base_url}{endpoint}?{query_string}&signature={signature}'
        print(url)
        response = requests.get(url, headers=headers)
        return response.json()
    
    def get_future_balance(self):
        endpoint = '/fapi/v2/balance'
        query_string = self.get_query_string()
        signature = self.create_signature(query_string)
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        url = f'{self.base_url}{endpoint}?{query_string}&signature={signature}'
        print(url)
        response = requests.get(url, headers=headers)
        return response.json()


