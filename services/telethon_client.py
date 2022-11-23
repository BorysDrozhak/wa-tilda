import os

from telethon import TelegramClient


class TelethonClient:
    API_ID = os.getenv('TELETHON_API_ID')
    API_HASH = os.getenv('TELETHON_API_HASH')
    PHONE = os.getenv('PHONE')

    def __init__(self):
        self.client = None

    async def get_client(self):
        if self.API_ID and self.API_HASH and self.PHONE:
            if not self.client:
                self.client = TelegramClient(f'wa_session', self.API_ID, self.API_HASH)
                self.client.start(phone=self.PHONE)
            return self.client


telethon_client = TelethonClient()
