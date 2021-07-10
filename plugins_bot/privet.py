"""
Example plugins for tlgbotcore (send hi)
"""

from telethon import events


@tlgbot.on(events.NewMessage(pattern='hi'))
async def handler(event):
    await event.reply('hey')
