"""
Административный плагин для управления системой меню бота.
Позволяет просматривать, включать/отключать пункты меню,
обновлять кэш и перезагружать плагины меню.
"""

from bot.menu_system import (
    MENU_REGISTRY, invalidate_menu, toggle_menu_item, refresh_menu, register_menu
)
from telethon import events, Button
from typing import List, Any, Dict, Optional


# Регистрируем пункты меню при загрузке плагина
register_menu({
    'key': 'menu_admin',
    'tr_key': 'menu_admin_title',
    'plugin': 'menu_admin',
    'handler': 'show_menu_admin',
    'order': 1000,  # Показываем в конце меню
    'admin_only': True  # Доступно только администраторам
})


async def show_menu_admin(event):
    """Обработчик для показа административного меню управления меню."""
    tlgbot = event.client
    
    # Определяем язык пользователя
    lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
    if hasattr(tlgbot, 'settings') and tlgbot.settings:
        user = tlgbot.settings.get_user(event.sender_id)
        if user:
            lang = getattr(user, "lang", lang)
    
    # Заголовок меню
    title = tlgbot.i18n.t('menu_admin_menu_title', lang=lang) if hasattr(tlgbot, 'i18n') else "Управление меню"
    
    # Строим список пунктов меню
    menu_text = [f"🔧 {title}"]
    menu_text.append(f"📋 Всего пунктов: {len(MENU_REGISTRY)}")
    
    # Создаем кнопки для управления пунктами меню
    buttons = []
    
    # Кнопка обновления меню
    refresh_text = tlgbot.i18n.t('menu_admin_refresh', lang=lang) if hasattr(tlgbot, 'i18n') else "🔄 Обновить меню"
    buttons.append([Button.inline(refresh_text, "menu_admin:refresh")])
    
    # Кнопка для просмотра всех пунктов меню
    list_text = tlgbot.i18n.t('menu_admin_list', lang=lang) if hasattr(tlgbot, 'i18n') else "📋 Список пунктов меню"
    buttons.append([Button.inline(list_text, "menu_admin:list")])
    
    # Кнопка для перезагрузки плагинов
    reload_text = tlgbot.i18n.t('menu_admin_reload', lang=lang) if hasattr(tlgbot, 'i18n') else "🔄 Перезагрузить плагины"
    buttons.append([Button.inline(reload_text, "menu_admin:reload")])
    
    # Кнопка возврата в главное меню
    back_text = tlgbot.i18n.t('menu_back', lang=lang) if hasattr(tlgbot, 'i18n') else "◀️ Назад"
    buttons.append([Button.inline(back_text, "menu:back")])
    
    # Отправляем меню администратора
    await event.respond("\n".join(menu_text), buttons=buttons)


@tlgbot.on(events.CallbackQuery(pattern=r'^menu_admin:'))
async def menu_admin_handler(event):
    """Обработчик для административных команд управления меню."""
    tlgbot = event.client
    
    # Проверяем, что пользователь является администратором
    user_id = event.sender_id
    if user_id not in getattr(tlgbot, 'admins', []):
        await event.answer("У вас нет прав администратора", alert=True)
        return
    
    # Определяем язык пользователя
    lang = tlgbot.i18n.default_lang if hasattr(tlgbot, 'i18n') else "ru"
    if hasattr(tlgbot, 'settings') and tlgbot.settings:
        user = tlgbot.settings.get_user(user_id)
        if user:
            lang = getattr(user, "lang", lang)
    
    # Получаем команду из callback_data
    callback_data = event.data.decode('utf-8')
    command = callback_data.split(':')[1]
    
    if command == "refresh":
        # Обновляем кэш меню
        invalidate_menu()
        await event.answer("Кэш меню очищен")
        
        # Перезагружаем страницу меню
        await show_menu_admin(event)
        
    elif command == "reload":
        # Перезагружаем плагины
        stats = refresh_menu(tlgbot, reload_plugins=True)
        await event.answer(f"Плагины перезагружены: {stats['added']} пунктов меню")
        
        # Перезагружаем страницу меню
        await show_menu_admin(event)
        
    elif command == "list":
        # Показываем список всех пунктов меню
        await list_menu_items(event, lang)
        
    elif command.startswith("toggle:"):
        # Включаем/отключаем пункт меню
        menu_key = command.split(':')[1]
        new_state = toggle_menu_item(menu_key)
        
        if new_state is not None:
            state_text = "включен" if new_state else "отключен"
            await event.answer(f"Пункт меню {menu_key} {state_text}")
            
            # Обновляем список пунктов меню
            await list_menu_items(event, lang)
        else:
            await event.answer(f"Пункт меню {menu_key} не найден", alert=True)


async def list_menu_items(event, lang):
    """Показывает список всех пунктов меню с возможностью управления."""
    tlgbot = event.client
    
    # Заголовок списка
    title = tlgbot.i18n.t('menu_admin_items_title', lang=lang) if hasattr(tlgbot, 'i18n') else "Список пунктов меню:"
    
    # Строим список пунктов меню
    menu_text = [f"📋 {title}"]
    
    # Сортируем пункты меню по порядку
    sorted_entries = sorted(MENU_REGISTRY.values(), key=lambda entry: entry.order)
    
    for entry in sorted_entries:
        # Определяем значки статуса
        status = "✅" if entry.enabled else "❌"
        admin_only = "👑" if entry.admin_only else "👤"
        
        # Добавляем информацию о пункте меню
        menu_text.append(f"{status} {admin_only} [{entry.order}] {entry.key} ({entry.tr_key})")
    
    # Создаем кнопки для управления пунктами меню
    buttons = []
    row = []
    
    # Добавляем кнопки переключения состояния для каждого пункта
    for i, entry in enumerate(sorted_entries):
        # Определяем текст кнопки в зависимости от состояния
        if entry.enabled:
            button_text = f"❌ {entry.key}"  # Отключить
        else:
            button_text = f"✅ {entry.key}"  # Включить
            
        # Добавляем кнопку в текущий ряд
        row.append(Button.inline(button_text, f"menu_admin:toggle:{entry.key}"))
        
        # По 2 кнопки в ряд
        if len(row) == 2 or i == len(sorted_entries) - 1:
            buttons.append(row)
            row = []
    
    # Кнопка возврата в административное меню
    back_text = tlgbot.i18n.t('menu_back', lang=lang) if hasattr(tlgbot, 'i18n') else "◀️ Назад"
    buttons.append([Button.inline(back_text, "menu_admin:back")])
    
    # Отправляем список пунктов меню
    await event.edit("\n".join(menu_text), buttons=buttons)


@tlgbot.on(events.CallbackQuery(pattern=r'^menu_admin:back$'))
async def menu_admin_back(event):
    """Обработчик возврата в административное меню."""
    await show_menu_admin(event)


# Обработчик возврата в главное меню уже реализован в menu_system.py
# Этот код больше не нужен и может быть удален