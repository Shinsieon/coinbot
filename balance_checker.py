from binance_api import BinanceAPI

class BalanceChecker:
    def __init__(self):
        self.api = BinanceAPI()

    def check_balances(self):
        account_info = self.api.get_account_info()
        if 'balances' in account_info:
            for balance in account_info['balances']:
                asset = balance['asset']
                free = balance['free']
                locked = balance['locked']
                print(f'Asset: {asset}, Free: {free}, Locked: {locked}')
        else:
            print(f"Error: {account_info}")

