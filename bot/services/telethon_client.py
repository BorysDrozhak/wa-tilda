import os
import shutil
from telethon import TelegramClient

class TelethonClient:
    API_ID = os.environ.get('TELETHON_API_ID')
    API_HASH = os.environ.get('TELETHON_API_HASH')
    PHONE = os.environ.get('PHONE')

    def __init__(self):
        self.client = None

    async def get_client(self):
        if self.API_ID and self.API_HASH:
            if not self.client:
                try:
                    dest = os.path.join(os.path.sep, 'tmp', 'main_bot_session.session')
                    shutil.copy('main_bot_session.session', dest)
                except Exception as e:
                    print(e)
                else:
                    self.client = TelegramClient(f'{dest}', self.API_ID, self.API_HASH)
                    await self.client.start(phone=self.PHONE)
            return self.client


telethon_client = TelethonClient()
