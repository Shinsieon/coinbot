from Api.binance_api import BinanceAPI
from Api.fbinance_api import FBinanceAPI

class BalanceChecker:
    def __init__(self, api=FBinanceAPI()):
        self.api = api

    def get_balances(self):
        account_info = self.api.get_account_info()
        if 'balances' in account_info:
            return account_info['balances']
        else:
            print(f"Error: {account_info}")
    def get_have_balances(self):
        account_info = self.get_balances()
        return [balance for balance in account_info if float(balance['free']) > 0]

if __name__ == "__main__":
    bc = FBinanceAPI()
    print(bc.get_future_balance())
    # total_free = sum(float(item['free']) for item in have_balances)
    # print(have_balances,total_free)
    

