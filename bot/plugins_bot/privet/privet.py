"""
Example plugin for tlgbotcore (send hi) with i18n support
"""

from telethon import events

@tlgbot.on(tlgbot.cmd('hi'))
async def handler(event):
    # Получаем язык пользователя (по умолчанию "ru" если не найден)
    user = tlgbot.settings.get_user(event.sender_id)
    lang = getattr(user, "lang", "ru")
    # Используем локализацию через tlgbot.i18n
    await event.reply(tlgbot.i18n.t("greeting", lang=lang))
