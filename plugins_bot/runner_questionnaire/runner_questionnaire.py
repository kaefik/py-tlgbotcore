"""
Интерпретатор анкет который использует json-подобный синтаксис для набора вопросов и возможных ответов.
Отправь anketa для запуска беседы по анкете.
"""

from telethon import events


@tlgbot.on(events.NewMessage(chats=tlgbot.settings.get_all_user_id(), pattern='anketa'))
async def handler(event):
    await event.reply("Запуск беседы...")
