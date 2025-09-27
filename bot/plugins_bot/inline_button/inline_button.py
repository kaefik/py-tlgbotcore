"""
    демонстрация кнопок внутри сообщений
"""

from telethon import events, Button

# Импортируем систему меню для интеграции плагина
try:
    from bot.menu_system import register_menu
except ImportError:
    # Заглушка для статического анализа
    def register_menu(entry_data):
        return True

# кнопки команд
button_main_cmd = [
    # visible label, callback data token
    [Button.inline(tlgbot.i18n.t('inline_button_today', lang=tlgbot.i18n.default_lang) if hasattr(tlgbot, 'i18n') else "сегодня", b"today"),
     Button.inline(tlgbot.i18n.t('inline_button_tomorrow', lang=tlgbot.i18n.default_lang) if hasattr(tlgbot, 'i18n') else "завтра", b"tomorrow")],
    [Button.url('Check this site!', 'https://lonamiwebs.github.io'),
     Button.inline(tlgbot.i18n.t('inline_button_any', lang=tlgbot.i18n.default_lang) if hasattr(tlgbot, 'i18n') else "любой день", b"any")]
]

# Регистрируем пункт в системе меню при загрузке плагина
try:
    register_menu({
        'key': 'inline_button',
        'tr_key': 'menu_inline_title',
        'plugin': 'inline_button',
        'handler': 'menu_handler',
        'order': 30,  # Позиция в меню (чем меньше, тем выше)
        'admin_only': False  # Доступен всем пользователям
    })
except Exception as e:
    # Игнорируем ошибки при регистрации для совместимости
    pass

# Обработчик для системы меню
async def menu_handler(event):
    """Обработчик вызова из системы меню"""
    # Получаем язык пользователя
    user_lang = tlgbot.i18n.default_lang
    try:
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            user_lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    except Exception:
        pass
    
    await event.respond(
        tlgbot.i18n.t('menu_inline_response', lang=user_lang),
        buttons=button_main_cmd
    )
    return True

@tlgbot.on(tlgbot.admin_cmd('inline'))
async def start_cmd_plugin(event):
    await event.respond(tlgbot.i18n.t('inline_choose', lang=tlgbot.i18n.default_lang) if hasattr(tlgbot, 'i18n') else "Выбери ", buttons=button_main_cmd)
    # answer = await event.wait_event(events.CallbackQuery())
    # print(answer.data.decode("utf-8"))


@tlgbot.on(events.CallbackQuery(pattern='today|tomorrow|any'))
# @tlgbot.on(events.NewMessage(chats=tlgbot.settings.get_all_user_id(), pattern='сегодня'))
async def today_cmd(event):
    # data tokens are bytes like b'today' - map to localized label
    res = event.data.decode("utf-8")
    
    # Получаем язык пользователя
    user_lang = tlgbot.i18n.default_lang
    try:
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            user_lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    except Exception:
        pass
    
    label_map = {
        'today': tlgbot.i18n.t('inline_button_today', lang=user_lang) if hasattr(tlgbot, 'i18n') else 'сегодня',
        'tomorrow': tlgbot.i18n.t('inline_button_tomorrow', lang=user_lang) if hasattr(tlgbot, 'i18n') else 'завтра',
        'any': tlgbot.i18n.t('inline_button_any', lang=user_lang) if hasattr(tlgbot, 'i18n') else 'любой день'
    }
    choice_label = label_map.get(res, res)
    await event.edit(tlgbot.i18n.t('inline_choice_selected', lang=user_lang, choice=choice_label) 
                     if hasattr(tlgbot, 'i18n') else f"Вы выбрали -  {choice_label}")
