"""
Example plugins for tlgbotcore (send hi)
"""

from telethon import events


@tlgbot.on(events.NewMessage(pattern='hi'))
async def handler(event):
    with open('README.md') as f:
        s = f.read()
    await event.reply(f'{s}')
