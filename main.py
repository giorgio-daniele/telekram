# main.py
import  asyncio
from    telethon import TelegramClient
from    lib import get_messages_by_date, delete_my_messages_by_date, get_all_users
import  datetime

API_ID       = 0 
API_HASH     = ''
SESSION_NAME = 'my_session'
CHAT_NAME    = "PolitoDebate"

async def main():

    ts = datetime.datetime(year=2025, month=2, day=1)
    te = datetime.datetime(year=2025, month=6, day=11)

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await delete_my_messages_by_date(client, CHAT_NAME, ts, te)

if __name__ == '__main__':
    asyncio.run(main())
