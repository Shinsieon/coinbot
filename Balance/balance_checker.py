from Api.binance_api import BinanceAPI
class BalanceChecker:
    def __init__(self, api=BinanceAPI()):
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
    bc = BalanceChecker()
    have_balances = bc.get_have_balances()
    print(have_balances)


