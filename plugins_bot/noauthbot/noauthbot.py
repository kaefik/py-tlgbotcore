"""
Сообщает пользователю у которого нет доступа к боту.
"""

from telethon import events


@tlgbot.on(events.NewMessage())
async def noauthbot_plugin(event):
    # with open('README.md') as f:
    #     s = f.read()
    sender = await event.get_sender()
    sender_id = sender.id
    if sender_id in tlgbot.settings.get_all_user_id():
        return
    await event.reply(f'У вас нет доступа к боту. Ваш id {sender_id}. Обратитесь к администратору бота. ')
