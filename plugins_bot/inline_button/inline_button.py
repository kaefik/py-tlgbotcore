"""
    демонстрация кнопок внутри сообщений
"""

from telethon import events, Button

# кнопки команд
button_main_cmd = [
    [Button.inline("сегодня"),
     Button.inline("завтра")],
    [Button.inline("табель"),
     Button.inline("любой день")]
]


@tlgbot.on(events.NewMessage(chats=tlgbot.settings.get_all_user_id(), pattern='/inline'))
async def start_cmd_plugin(event):
    await event.respond("Выбери ", buttons=button_main_cmd)


@tlgbot.on(events.CallbackQuery(pattern='сегодня|завтра|табель|любой день'))
# @tlgbot.on(events.NewMessage(chats=tlgbot.settings.get_all_user_id(), pattern='сегодня'))
async def today_cmd(event):
    res = event.data.decode("utf-8")
    await event.edit(f"Вы выбрали -  {res}")
