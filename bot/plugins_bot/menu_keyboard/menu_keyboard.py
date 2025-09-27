"""Плагин для добавления кнопки Меню в клавиатуре под строкой ввода"""

from telethon import events, Button
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton
from bot.menu_system import send_main_menu, register_menu

# Ключ в локалях для кнопки меню
MENU_BUTTON_KEY = "menu_keyboard_button"

def create_menu_keyboard(lang):
    """Создает клавиатуру с кнопкой 'Меню'"""
    if not hasattr(tlgbot, 'i18n'):
        button_text = "Меню"
    else:
        button_text = tlgbot.i18n.t(MENU_BUTTON_KEY, lang=lang)
    
    # Создаем клавиатуру с одной кнопкой
    return ReplyKeyboardMarkup([
        KeyboardButtonRow([
            KeyboardButton(button_text)
        ])
    ], resize=True, single_use=False, selective=False)

@tlgbot.on(tlgbot.cmd('keyboard'))
async def keyboard_cmd_handler(event):
    """Обработчик команды /keyboard - добавляет клавиатуру с кнопкой Меню"""
    user = tlgbot.settings.get_user(event.sender_id)
    lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    
    # Создаем клавиатуру
    keyboard = create_menu_keyboard(lang)
    
    # Отправляем сообщение с клавиатурой
    await event.respond(
        tlgbot.i18n.t("menu_keyboard_added", lang=lang) 
        if hasattr(tlgbot, 'i18n') else "Клавиатура с кнопкой меню добавлена",
        buttons=keyboard
    )

# Обработчик для вызова из системы меню
async def menu_handler(event):
    """Обработчик для вызова из системы меню"""
    # Получаем язык пользователя
    user = tlgbot.settings.get_user(event.sender_id)
    lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    
    # Создаем клавиатуру
    keyboard = create_menu_keyboard(lang)
    
    # Для событий типа CallbackQuery используем event.edit или event.answer
    if hasattr(event, 'answer'):
        # Это CallbackQuery, используем соответствующие методы
        await event.answer()  # Подтверждаем нажатие кнопки
        await event.edit(
            tlgbot.i18n.t("menu_keyboard_added", lang=lang)
            if hasattr(tlgbot, 'i18n') else "Клавиатура с кнопкой меню добавлена",
            buttons=keyboard
        )
    else:
        # Это обычное сообщение, используем respond
        await event.respond(
            tlgbot.i18n.t("menu_keyboard_added", lang=lang)
            if hasattr(tlgbot, 'i18n') else "Клавиатура с кнопкой меню добавлена",
            buttons=keyboard
        )

@tlgbot.on(events.NewMessage(pattern=r'^/start'))
async def auto_add_keyboard_on_start(event):
    """Добавляет клавиатуру после команды /start"""
    # Получаем язык пользователя
    lang = tlgbot.i18n.default_lang
    if hasattr(tlgbot, 'settings'):
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            lang = getattr(user, "lang", lang)
            
    # Создаем клавиатуру для пользователя
    keyboard = create_menu_keyboard(lang)
    
    # Добавляем клавиатуру к следующему сообщению с небольшим информационным текстом
    button_text = tlgbot.i18n.t(MENU_BUTTON_KEY, lang=lang) if hasattr(tlgbot, 'i18n') else "Меню"
    message = tlgbot.i18n.t("menu_keyboard_added", lang=lang) if hasattr(tlgbot, 'i18n') else f"Клавиатура с кнопкой '{button_text}' добавлена"
    await event.respond(message, buttons=keyboard)

@tlgbot.on(events.NewMessage())
async def menu_button_handler(event):
    """Обработчик нажатий на кнопку 'Меню' в клавиатуре"""
    # Проверяем, что это текстовое сообщение
    if not hasattr(event, "message") or not hasattr(event.message, "message"):
        return
    
    # Получаем язык пользователя
    if not hasattr(tlgbot, 'settings'):
        return
    
    user = tlgbot.settings.get_user(event.sender_id)
    if not user:
        return
        
    lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    
    # Проверяем, совпадает ли текст сообщения с текстом кнопки меню
    button_text = tlgbot.i18n.t(MENU_BUTTON_KEY, lang=lang) if hasattr(tlgbot, 'i18n') else "Меню"
    
    if event.message.message == button_text:
        # Если совпадает - открываем главное меню
        await send_main_menu(event, lang=lang)

# Регистрируем плагин в системе меню
try:
    register_menu({
        'key': 'keyboard',
        'tr_key': 'menu_keyboard_button',
        'plugin': 'menu_keyboard',
        'handler': 'menu_handler',
        'order': 50
    })
except Exception as e:
    # Игнорируем ошибки при регистрации для совместимости
    pass
