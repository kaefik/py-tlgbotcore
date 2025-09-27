"""
обработка команды /start
Использует динамическую систему меню
"""

from telethon import events, Button
from bot.menu_system import send_main_menu, init_menu_system


# Инициализируем систему меню при загрузке плагина
init_menu_system(tlgbot)


@tlgbot.on(tlgbot.cmd('start'))
async def start_cmd_plugin(event):
    """
    Обработчик команды /start
    Показывает пользователю главное меню с доступными действиями
    """
    # Получаем язык пользователя
    lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
    if hasattr(tlgbot, 'settings') and tlgbot.settings:
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            lang = getattr(user, "lang", lang)
    
    # Отправляем приветственное сообщение
    welcome_message = tlgbot.i18n.t('start_welcome', lang=lang) if hasattr(tlgbot, 'i18n') else "Привет! Выберите действие:"
    
    # Отправляем главное меню с кнопками, которые соответствуют роли пользователя
    await send_main_menu(event, lang)
