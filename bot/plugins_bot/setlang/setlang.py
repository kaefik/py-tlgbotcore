"""
Плагин для смены языка пользователя командой /setlang с inline-кнопками
Интегрирован с системой меню
"""

from telethon import events, Button
from cfg import config_tlg
from bot.menu_system import register_menu

# Регистрируем плагин в системе меню
register_menu({
    'key': 'setlang',
    'tr_key': 'menu_setlang_title',
    'plugin': 'setlang',
    'handler': 'menu_handler',
    'order': 20  # Показываем после приветствия
})

@tlgbot.on(tlgbot.cmd('setlang'))
async def setlang_handler(event):
    user = tlgbot.settings.get_user(event.sender_id)
    # Формируем inline-кнопки для выбора языка на основе config_tlg.AVAILABLE_LANGS
    buttons = [
        [Button.inline(name, data=f"setlang_{code}")]
        for code, name in config_tlg.AVAILABLE_LANGS.items()
    ]
    await event.reply(
        tlgbot.i18n.t("choose_lang", lang=getattr(user, "lang", "ru")),
        buttons=buttons
    )
    
# Обработчик для вызова из меню
async def menu_handler(event):
    # Используем тот же обработчик, что и для команды /setlang
    await setlang_handler(event)

@tlgbot.on(events.CallbackQuery(pattern=b"setlang_.*"))
async def setlang_callback_handler(event):
    user = tlgbot.settings.get_user(event.sender_id)
    data = event.data.decode("utf-8")
    lang_code = data.replace("setlang_", "")
    if lang_code not in config_tlg.AVAILABLE_LANGS:
        await event.answer(
            tlgbot.i18n.t("lang_not_supported", lang=getattr(user, "lang", "ru"), code=lang_code),
            alert=True
        )
        return

    # Если по какой-то причине lang_code не задан, используем язык по умолчанию из конфига
    user.lang = lang_code or getattr(config_tlg, "DEFAULT_LANG", "ru")
    tlgbot.settings.update_user(user)  # используйте update_user для обновления существующего пользователя
    await event.edit(
        tlgbot.i18n.t("lang_changed", lang=user.lang, lang_name=config_tlg.AVAILABLE_LANGS[user.lang])
    )

    # Дополнительно: пересоздаем reply-клавиатуру с кнопкой "Меню" в новом языке
    # Чтобы пользователь сразу видел обновлённый текст кнопки без /start
    try:
        from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton  # type: ignore
        bot_client = getattr(event, 'client', None)
        if bot_client and hasattr(bot_client, 'i18n'):
            button_text = bot_client.i18n.t("menu_keyboard_button", lang=user.lang)
            keyboard = ReplyKeyboardMarkup([
                KeyboardButtonRow([
                    KeyboardButton(button_text)
                ])
            ], resize=True, single_use=False, selective=False)
            await event.respond(
                bot_client.i18n.t("menu_keyboard_added", lang=user.lang),
                buttons=keyboard
            )
    except Exception:
        # Тихо игнорируем, чтобы не ломать процесс смены языка
        pass