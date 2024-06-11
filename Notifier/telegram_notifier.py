import requests
import configparser
class TelegramNotifier:
    def __init__(self, config_file='Config/config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.bot_token = self.config['telegram']['bot_token']
        self.chat_id = self.config['telegram']['chat_id']

    def send_message(self, message):
        print(message)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        response = requests.post(url, json=payload)
        return response.json()