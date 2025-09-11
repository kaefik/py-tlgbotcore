"""
Плагин для смены языка пользователя командой /setlang с inline-кнопками
"""

from telethon import events, Button

AVAILABLE_LANGS = {
    "ru": "Русский",
    "en": "English"
}

@tlgbot.on(tlgbot.cmd('setlang'))
async def setlang_handler(event):
    user = tlgbot.settings.get_user(event.sender_id)
    # Формируем inline-кнопки для выбора языка
    buttons = [
        [Button.inline(name, data=f"setlang_{code}")]
        for code, name in AVAILABLE_LANGS.items()
    ]
    await event.reply(
        tlgbot.i18n.t("choose_lang", lang=getattr(user, "lang", "ru")),
        buttons=buttons
    )

@tlgbot.on(events.CallbackQuery(pattern=b"setlang_.*"))
async def setlang_callback_handler(event):
    user = tlgbot.settings.get_user(event.sender_id)
    data = event.data.decode("utf-8")
    lang_code = data.replace("setlang_", "")
    if lang_code not in AVAILABLE_LANGS:
        await event.answer(
            tlgbot.i18n.t("lang_not_supported", lang=getattr(user, "lang", "ru"), code=lang_code),
            alert=True
        )
        return

    user.lang = lang_code
    tlgbot.settings.update_user(user)  # исправлено
    await event.edit(
        tlgbot.i18n.t("lang_changed", lang=lang_code, lang_name=AVAILABLE_LANGS[lang_code])
    )