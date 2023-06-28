import pytz
from datetime import datetime, timedelta

from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import InviteToChannelRequest

from services.telethon_client import telethon_client

wa_bot_id = 1655066222
tildaforms_id = 265299531


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
            return message.date + timedelta(minutes=5) > datetime.now(tz=pytz.UTC)


async def start_jobs(channel_id):
    client = await telethon_client.get_client()
    entity = await client.get_entity(channel_id)
    await client.send_message(entity=entity, message="/daily_poll")


async def add_member(username, channels):
    client = await telethon_client.get_client()
    if not client:
        return

    for channel in channels:
        user_to_add = await client.get_input_entity(username)
        print(user_to_add)

        try:
            await client(InviteToChannelRequest(channel, [user_to_add]))
        except Exception as e:
            print(e)
