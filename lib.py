import asyncio
from    telethon.tl.types              import PeerChannel, PeerChat, PeerUser
from    telethon.tl.functions.messages import DeleteMessagesRequest
from    telethon.tl.functions.channels import GetParticipantsRequest
from    telethon.tl.types              import ChannelParticipantsSearch
from    telethon.client                import TelegramClient
from    telethon.tl.custom.message     import Message
from    telethon.errors                import FloodWaitError
import  datetime
import  logging
from    typing import List, Dict, Any, Union


async def get_messages_by_date(
    client:  TelegramClient,
    chat_id: Union[int, str],
    ts:      datetime.datetime,
    te:      datetime.datetime
) -> List[Dict[str, Any]]:
    
    print(f"Fetching messages between {ts} and {te} in chat '{chat_id}'...")
    messages: List[Dict[str, Any]] = []
    async for message in client.iter_messages(chat_id, offset_date=te, reverse=True):
        if message.date < ts:
            break
        messages.append({
            'id':        message.id,
            'sender_id': message.sender_id,
            'text':      message.message,
            'date':      str(message.date)
        })
    print(f"Fetched {len(messages)} messages in date range.")
    return messages


async def delete_my_messages_by_date(
    client:     TelegramClient,
    chat_id:    Union[int, str],
    ts: datetime.datetime,
    te: datetime.datetime
) -> None:
    
    def to_naive(dt: datetime.datetime) -> datetime.datetime:
        return dt.replace(tzinfo=None) if dt.tzinfo else dt

    # Get my own profile
    me  = await client.get_me()
    ids = []

    print(f"Scanning messages for deletion in chat '{chat_id}' from {ts.date()} to {te.date()}...")

    ts_naive = to_naive(ts)
    te_naive = to_naive(te)

    async for m in client.iter_messages(chat_id, reverse=False, from_user=me, offset_date=te):
        d = to_naive(m.date)
        if d < ts_naive:
            break
        if ts_naive <= d <= te_naive:
            ids.append(m.id)

    if not ids:
        # Print and exit
        print("No messages to delete.")
        return
    else:
        BATCH_SIZE = 100
        for i in range(0, len(ids), BATCH_SIZE):
            batch = ids[i:i + BATCH_SIZE]
            try:
                await client.delete_messages(chat_id, batch, revoke=True)
            except FloodWaitError as e:
                print(f"FloodWaitError: Sleeping for {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
                await client.delete_messages(chat_id, batch, revoke=True)
            except Exception as e:
                print(f"Error deleting batch {batch}: {e}")

async def get_all_users(
    client:  TelegramClient,
    chat_id: Union[int, str],
    search:  str = ""
) -> List[Dict[str, Union[int, str, None]]]:
    
    offset: int = 0
    limit:  int = 100
    users:  List[PeerUser] = []

    print(f"Fetching users from chat '{chat_id}'...")
    while True:
        participants = await client(GetParticipantsRequest(
            channel=chat_id,
            filter=ChannelParticipantsSearch(search),
            offset=offset,
            limit=limit,
            hash=0
        ))
        if not participants.users:
            break
        users.extend(participants.users)
        offset += len(participants.users)

    print(f"Found {len(users)} users in chat.")
    return [{
        'id':         user.id,
        'username':   user.username,
        'first_name': user.first_name,
        'last_name':  user.last_name
    } for user in users]
