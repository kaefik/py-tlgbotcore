"""
Example plugin for tlgbotcore (send hi) with i18n support and default language fallback
"""

from telethon import events
from bot.menu_system import register_menu

# Регистрируем плагин в системе меню
register_menu({
    'key': 'privet',
    'tr_key': 'menu_privet_title',
    'plugin': 'privet',
    'handler': 'menu_handler',
    'order': 10  # Показываем в начале меню
})

@tlgbot.on(tlgbot.cmd('hi'))
async def handler(event):
    user = tlgbot.settings.get_user(event.sender_id)
    # Получаем язык пользователя, если не задан — используем язык по умолчанию из i18n
    lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    await event.reply(tlgbot.i18n.t("greeting", lang=lang))

# Обработчик для вызова из меню
async def menu_handler(event):
    user = tlgbot.settings.get_user(event.sender_id)
    # Получаем язык пользователя, если не задан — используем язык по умолчанию из i18n
    lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    await event.respond(tlgbot.i18n.t("menu_privet_response", lang=lang))
