"""
Example plugins for tlgbotcore (send hi)
"""

from telethon import events


@tlgbot.on(tlgbot.admin_cmd('hi'))
async def handler(event):
    # with open('README.md') as f:
    #     s = f.read()
    await event.reply('Привет!')
