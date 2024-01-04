from datetime import datetime, timedelta, timezone

from telethon.tl import functions
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import InviteToChannelRequest

from services.telethon_client import telethon_client

wa_bot_id = 1655066222
tildaforms_id = 265299531

MESSAGE = '''Подякуйте собі, за те які ви є
І подякуйте людям навколо вас, цей тиждень. Просто. За те що вони є
І не забудьте про батьків
❤️'''


async def get_messages(channel_id):
    client = await telethon_client.get_client()
    if client:
        channel_entity = await client.get_entity(channel_id)
        posts = await client(GetHistoryRequest(
            peer=channel_entity,
            limit=10,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0))

        return posts.messages


def bot_respond(messages):
    for message in messages:
        if message.message and message.from_id.user_id == wa_bot_id:
            return True
        if message.message and message.from_id.user_id == tildaforms_id:
            local_time = datetime.now()
            utc_time = local_time.replace(tzinfo=timezone.utc)
            return message.date + timedelta(minutes=5) > utc_time


async def add_member(username, channels):
    client = await telethon_client.get_client()
    if not client:
        return

    user_to_add = await client.get_input_entity(username)
    print(user_to_add)
    if not user_to_add:
        return

    for channel in channels:
        channel_entity = await client.get_entity(channel)
        try:
            res = await client(InviteToChannelRequest(channel_entity, [user_to_add]))
            print(res)
        except Exception as e:
            print(e)


async def send_messages(users):
    client = await telethon_client.get_client()
    if client:
        for user in users:
            try:
                await client(functions.messages.SendMessageRequest(
                    peer=user.get('username'),  # Replace with the recipient's username or phone number
                    message=MESSAGE))
            except Exception as e:
                print(e)
