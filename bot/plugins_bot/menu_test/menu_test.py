"""
Тестовый плагин для демонстрации работы системы меню.
Регистрирует несколько пунктов меню и обрабатывает их.
"""

from bot.menu_system import register_menu

# Регистрируем пункты меню при загрузке плагина
register_menu({
    'key': 'test_hello',
    'tr_key': 'menu_test_hello',
    'plugin': 'menu_test',
    'handler': 'handle_hello',
    'order': 100  # показывать в начале меню
})

register_menu({
    'key': 'test_admin_action',
    'tr_key': 'menu_test_admin_action',
    'plugin': 'menu_test',
    'handler': 'handle_admin_action',
    'order': 200,
    'admin_only': True  # этот пункт виден только администраторам
})

register_menu({
    'key': 'test_with_params',
    'tr_key': 'menu_test_with_params',
    'plugin': 'menu_test',
    'handler': 'handle_params',
    'order': 300
})


# Обработчики для пунктов меню

async def handle_hello(event):
    """Обработчик для обычного пункта меню"""
    tlgbot = event.client
    lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
    
    # Проверяем, есть ли у пользователя предпочтительный язык
    if hasattr(tlgbot, 'settings') and tlgbot.settings:
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            lang = getattr(user, "lang", lang)
    
    # Отправляем приветствие
    message = tlgbot.i18n.t('menu_test_hello_response', lang=lang) if hasattr(tlgbot, 'i18n') else "Привет! Это тестовый пункт меню."
    await event.respond(message)


async def handle_admin_action(event):
    """Обработчик для админского пункта меню"""
    tlgbot = event.client
    lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
    
    # Проверяем, есть ли у пользователя предпочтительный язык
    if hasattr(tlgbot, 'settings') and tlgbot.settings:
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            lang = getattr(user, "lang", lang)
    
    # Отправляем ответ для администратора
    message = tlgbot.i18n.t('menu_test_admin_response', lang=lang) if hasattr(tlgbot, 'i18n') else "Это действие доступно только администраторам."
    await event.respond(message)


async def handle_params(event):
    """Обработчик для пункта меню с параметрами"""
    tlgbot = event.client
    lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
    
    # Проверяем, есть ли у пользователя предпочтительный язык
    if hasattr(tlgbot, 'settings') and tlgbot.settings:
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            lang = getattr(user, "lang", lang)
    
    # Получаем параметры, если есть
    params = getattr(event, 'menu_params', [])
    params_text = ", ".join(params) if params else "без параметров"
    
    # Отправляем ответ с информацией о параметрах
    message = tlgbot.i18n.t('menu_test_params_response', lang=lang, params=params_text) if hasattr(tlgbot, 'i18n') else f"Вызван с параметрами: {params_text}"
    await event.respond(message)