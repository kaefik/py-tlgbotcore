"""
Система меню для бота.
Позволяет плагинам регистрировать пункты меню и создавать динамические кнопки.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import logging

# Используем 'type: ignore', так как telethon может быть доступен только во время работы бота
try:
    from telethon import Button  # type: ignore
except ImportError:
    # Заглушка для запуска без активного telethon
    class Button:
        @staticmethod
        def text(text: str, data: Optional[str] = None) -> Any:
            return {"text": text, "data": data}
        
        @staticmethod
        def inline(text: str, data: str) -> Any:
            return {"text": text, "data": data}

# Настройка логгера
logger = logging.getLogger(__name__)


@dataclass
class MenuEntry:
    """
    Класс для хранения информации о пункте меню.
    
    Атрибуты:
        key (str): Уникальный идентификатор пункта меню
        tr_key (str): Ключ для локализации текста кнопки
        plugin (str): Имя плагина, где находится обработчик
        handler (str): Имя функции-обработчика в плагине
        order (int): Порядок сортировки (меньше = выше)
        admin_only (bool): Только для администраторов
    """
    key: str
    tr_key: str
    plugin: str
    handler: str
    order: int
    admin_only: bool = False


# Глобальный реестр меню - хранит все зарегистрированные пункты меню
# Ключ - уникальный идентификатор пункта, значение - экземпляр MenuEntry
MENU_REGISTRY: Dict[str, MenuEntry] = {}

# Кэш кнопок - для оптимизации создания меню
# Ключи: (язык, is_admin), значение - список кнопок в формате telethon
MENU_CACHE: Dict[Tuple[str, bool], List[List[Any]]] = {}


def register_menu(entry_data: Dict[str, Any]) -> bool:
    """
    Регистрирует пункт меню в системе.
    
    Аргументы:
        entry_data: Словарь с данными о пункте меню, должен содержать ключи:
            - key: уникальный идентификатор пункта
            - tr_key: ключ для локализации текста
            - plugin: имя плагина, где находится обработчик
            - handler: имя функции-обработчика
            - order: порядок сортировки (меньше = выше)
            - admin_only: (опционально) только для администраторов
    
    Возвращает:
        bool: True, если регистрация успешна, иначе False
    """
    # Проверяем наличие обязательных полей
    required_fields = ['key', 'tr_key', 'plugin', 'handler', 'order']
    if not all(field in entry_data for field in required_fields):
        logger.error(f"Не хватает обязательных полей в пункте меню: {entry_data}")
        return False
    
    # Проверяем, не зарегистрирован ли уже такой пункт
    key = entry_data['key']
    if key in MENU_REGISTRY:
        logger.warning(f"Пункт меню с ключом '{key}' уже зарегистрирован, перезаписываем")
    
    # Создаем экземпляр MenuEntry и добавляем в реестр
    menu_entry = MenuEntry(
        key=key,
        tr_key=entry_data['tr_key'],
        plugin=entry_data['plugin'],
        handler=entry_data['handler'],
        order=entry_data['order'],
        admin_only=entry_data.get('admin_only', False)
    )
    
    MENU_REGISTRY[key] = menu_entry
    
    # Сбрасываем кэш после изменения реестра
    invalidate_menu()
    
    logger.debug(f"Зарегистрирован пункт меню: {menu_entry}")
    return True


def invalidate_menu(lang: Optional[str] = None) -> None:
    """
    Инвалидирует кэш меню.
    
    Аргументы:
        lang: Если указан, сбрасывает кэш только для конкретного языка,
              иначе сбрасывает весь кэш
    """
    if lang is None:
        # Полностью сбрасываем кэш
        MENU_CACHE.clear()
        logger.debug("Кэш меню полностью сброшен")
    else:
        # Сбрасываем кэш только для указанного языка
        keys_to_remove = [k for k in MENU_CACHE if k[0] == lang]
        for key in keys_to_remove:
            del MENU_CACHE[key]
        logger.debug(f"Кэш меню сброшен для языка {lang}")


def _is_admin_user(user_id: int, admins: List[int]) -> bool:
    """
    Проверяет, является ли пользователь администратором.
    
    Аргументы:
        user_id: ID пользователя для проверки
        admins: Список ID администраторов
        
    Возвращает:
        bool: True, если пользователь админ, иначе False
    """
    return user_id in admins


def build_menu(tlgbot: Any, lang: str, user_id: Optional[int] = None) -> List[List[Any]]:
    """
    Строит кнопки меню для указанного языка и роли пользователя.
    
    Аргументы:
        tlgbot: Экземпляр TlgBotCore для доступа к i18n и settings
        lang: Код языка для локализации кнопок
        user_id: ID пользователя (для определения роли)
        
    Возвращает:
        List[List[Button]]: Список строк с кнопками меню
    """
    # Проверяем, является ли пользователь админом
    is_admin = False
    if user_id is not None:
        is_admin = _is_admin_user(user_id, getattr(tlgbot, "admins", []))
    
    # Проверяем, есть ли меню в кэше
    cache_key = (lang, is_admin)
    if cache_key in MENU_CACHE:
        logger.debug(f"Используем кэшированное меню для {cache_key}")
        return MENU_CACHE[cache_key]
    
    # Создаем меню заново
    menu_entries = list(MENU_REGISTRY.values())
    
    # Отфильтровываем пункты только для админов, если пользователь не админ
    if not is_admin:
        menu_entries = [entry for entry in menu_entries if not entry.admin_only]
    
    # Сортируем пункты по полю order
    menu_entries.sort(key=lambda entry: entry.order)
    
    # Формируем кнопки, по две в ряд
    buttons = []
    row = []
    
    for entry in menu_entries:
        # Получаем локализованный текст
        text = tlgbot.i18n.t(entry.tr_key, lang=lang) if hasattr(tlgbot, 'i18n') else entry.tr_key
        
        # Создаем кнопку с callback_data в формате "menu:ключ_пункта"
        button = Button.inline(text, f"menu:{entry.key}")
        
        # Добавляем в текущий ряд или начинаем новый
        row.append(button)
        if len(row) == 2:
            buttons.append(row)
            row = []
    
    # Добавляем оставшийся неполный ряд, если такой есть
    if row:
        buttons.append(row)
    
    # Сохраняем в кэше
    MENU_CACHE[cache_key] = buttons
    
    logger.debug(f"Создано новое меню для {cache_key}")
    return buttons


async def dispatch_command(event: Any, key: str) -> bool:
    """
    Находит и вызывает обработчик для конкретного ключа меню.
    
    Аргументы:
        event: Событие Telethon, которое будет передано обработчику
        key: Ключ пункта меню для поиска обработчика
        
    Возвращает:
        bool: True, если обработчик найден и вызван, иначе False
    """
    if key not in MENU_REGISTRY:
        logger.error(f"Обработчик для ключа '{key}' не найден")
        return False
    
    # Получаем информацию о пункте меню
    menu_entry = MENU_REGISTRY[key]
    
    # Проверяем, есть ли tlgbot в глобальном контексте
    tlgbot = getattr(event, "client", None)
    if tlgbot is None:
        logger.error("Не удалось получить экземпляр tlgbot из события")
        return False
    
    # Проверяем права доступа, если пункт меню только для админов
    if menu_entry.admin_only:
        user_id = event.sender_id
        is_admin = _is_admin_user(user_id, getattr(tlgbot, "admins", []))
        if not is_admin:
            logger.warning(f"Пользователь {user_id} пытается получить доступ к админскому пункту меню '{key}'")
            await event.answer("У вас нет прав для выполнения этого действия", alert=True)
            return False
    
    # Проверяем, загружен ли плагин
    if menu_entry.plugin not in tlgbot._plugins:
        logger.error(f"Плагин '{menu_entry.plugin}' не загружен")
        await event.answer(f"Ошибка: плагин '{menu_entry.plugin}' не загружен", alert=True)
        return False
    
    # Получаем обработчик из плагина
    plugin_module = tlgbot._plugins[menu_entry.plugin]
    handler_func = getattr(plugin_module, menu_entry.handler, None)
    
    if handler_func is None:
        logger.error(f"Обработчик '{menu_entry.handler}' не найден в плагине '{menu_entry.plugin}'")
        await event.answer(f"Ошибка: обработчик не найден", alert=True)
        return False
    
    # Вызываем обработчик
    try:
        # Отправляем уведомление, что команда принята
        await event.answer("Выполняется...")
        
        # Вызываем обработчик
        await handler_func(event)
        logger.debug(f"Успешно выполнен обработчик для пункта меню '{key}'")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при вызове обработчика меню '{key}': {e}")
        # Отправляем уведомление об ошибке
        try:
            await event.answer(f"Произошла ошибка при обработке команды", alert=True)
        except Exception:
            pass  # Игнорируем ошибку при отправке уведомления
        return False


def init_menu_system(tlgbot: Any) -> None:
    """
    Инициализирует роутер для callback-кнопок с префиксом 'menu:'.
    
    Аргументы:
        tlgbot: Экземпляр TlgBotCore
    """
    from telethon import events  # type: ignore
    
    @tlgbot.on(events.CallbackQuery(pattern=r'^menu:'))
    async def menu_callback_router(event):
        """
        Маршрутизатор callback-запросов для системы меню.
        
        Обрабатывает callback-данные в формате:
        - menu:key - для простых действий
        - menu:key:param1:param2... - для действий с параметрами
        """
        # Извлекаем данные из callback_data
        callback_data = event.data.decode('utf-8')
        if not callback_data.startswith('menu:'):
            return
        
        # Разбираем параметры (если есть)
        parts = callback_data[5:].split(':')
        menu_key = parts[0]
        
        # Добавляем параметры к event для использования в обработчике
        if len(parts) > 1:
            params = parts[1:]
            setattr(event, 'menu_params', params)
            logger.debug(f"Вызов меню с параметрами: key={menu_key}, params={params}")
        else:
            setattr(event, 'menu_params', [])
            logger.debug(f"Вызов меню без параметров: key={menu_key}")
        
        # Вызываем соответствующий обработчик
        success = await dispatch_command(event, menu_key)
        
        # Если обработчик не найден, сообщаем об этом пользователю
        if not success:
            await event.answer("Обработчик для этого пункта меню не найден", alert=True)
    
    # Регистрируем специальный обработчик для текстовых сообщений, соответствующих меню
    @tlgbot.on(events.NewMessage())
    async def text_menu_handler(event):
        """
        Проверяет текстовые сообщения на соответствие пунктам меню.
        Это позволяет пользователям вводить команды вручную, а не только через кнопки.
        """
        # Проверяем, что это текстовое сообщение
        if not event.text:
            return
        
        # Получаем экземпляр tlgbot
        tlgbot = event.client
        
        # Определяем язык пользователя
        lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
        user_id = event.sender_id
        if hasattr(tlgbot, 'settings') and tlgbot.settings:
            user = tlgbot.settings.get_user(user_id)
            if user:
                lang = getattr(user, "lang", lang)
        
        # Проверяем, соответствует ли текст сообщения какому-либо пункту меню
        for entry in MENU_REGISTRY.values():
            menu_text = tlgbot.i18n.t(entry.tr_key, lang=lang) if hasattr(tlgbot, 'i18n') else entry.tr_key
            
            # Если текст сообщения совпадает с текстом пункта меню, вызываем обработчик
            if event.text == menu_text:
                logger.debug(f"Текстовое сообщение соответствует пункту меню: {entry.key}")
                await dispatch_command(event, entry.key)
                break


async def send_main_menu(event: Any, lang: Optional[str] = None) -> None:
    """
    Отправляет основное меню пользователю с учетом его роли.
    
    Аргументы:
        event: Событие Telethon, из которого берется sender_id
        lang: Код языка, если None - будет использован язык пользователя или дефолтный
    """
    tlgbot = event.client
    
    # Определяем ID пользователя
    user_id = event.sender_id
    
    # Определяем язык пользователя
    if lang is None:
        # Пытаемся получить пользователя и его язык из хранилища
        if hasattr(tlgbot, 'settings') and tlgbot.settings:
            user = tlgbot.settings.get_user(user_id)
            lang = getattr(user, "lang", None)
        
        # Если язык все еще None, используем дефолтный
        if lang is None:
            lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
    
    # Строим меню для конкретного пользователя
    buttons = build_menu(tlgbot, lang, user_id)
    
    # Отправляем приветственное сообщение с меню
    welcome_message = tlgbot.i18n.t('menu_welcome', lang=lang) if hasattr(tlgbot, 'i18n') else "Выберите действие:"
    await event.respond(welcome_message, buttons=buttons)