О проекте

[py-tlgbotcore](https://github.com/kaefik/py-tlgbotcore) - Основа телеграмм бота которому можно расширять функционал с
помощью плагинов

!!! **вдохновлен проектом [UniBorg](https://github.com/udf/uniborg) и взят за основу и тем самым изучая проект понимаешь
глубже библиотеку Telethon**

## Реализованные возможности:

* подключение плагинов которые реализуют основную функциональность бота.

## Плагины которые доступны:

1. **_core.py** - плагин, который реализует административные команды по плагинам и доступу к боту. Доступ имеет
   администраторы.

Полную документацию по модулю _core смотрите файл tlbotcore/_core.md

2. **noauthbot** - предупреждает пользователя если он не авторизован для доступа к боту.

3. **runner_questionnaire** - интерпретатор анкет который использует json-подобный синтаксис для набора вопросов и
   возможных ответов.

## Настройка проекта для запуска

### Библиотеки:

```bash
  pip install Telethon # для самого бота
 ```

### Конфигурационные файлы проекта:

* **cfg/config_tlg.py** - за основу можно взять файл config_tlg_example.py

  ```
    # здесь указывается переменные для запуска телеграмм бота
    TLG_APP_NAME = "tlgbotappexample"  # APP NAME get from https://my.telegram.org
    TLG_APP_API_ID = 1258887  # APP API ID get from https://my.telegram.org
    TLG_APP_API_HASH = "sdsadsadasd45522665f"  # APP API HASH get from https://my.telegram.org
    I_BOT_TOKEN = "0000000000:sfdfdsfsdf5s5541sd2f1sd5"  # TOKEN Bot from BotFather
    TLG_ADMIN_ID_CLIENT = [1258889]  # admin clients for admin telegram bot
    # proxy for Telegram
    TLG_PROXY_SERVER = None  # address MTProxy Telegram
    TLG_PROXY_PORT = None  # port  MTProxy Telegram
    TLG_PROXY_KEY = None  # secret key  MTProxy Telegram
    # for save settings user
    # CSV - сохранение данных настроек для доступа к боту используя БД в формате CSV
    # SQLITE - сохранение данных настроек для доступа к боту используя БД в формате sqlite3
    TYPE_DB = "SQLITE"
  ```

Параметром **TYPE_DB** можно выбрать сохранять настройки с помощью sqlite3 или в файле csv (бывает полезно когда по
каким-то причинам на устройстве нет встроенной библиотеки slite3)

## Запуск бота как сервис

сохраним файл start-youtube-audio.service в папку /etc/systemd/system

```bash
[Unit]
Description=Youtube video to audio
After=network.target

[Service]
ExecStart=/bin/bash /home/scripts/youtube2mp3/start-youtube2mp3.sh

[Install]
WantedBy=default.target
```

Запуск сервиса

```bash
systemctl enable start-youtube-audio.service
systemctl start start-youtube-audio.service
```

## Плагины к боту

Все плагины находятся в папке **plugins_bot**. Плагин представляет собой папку с именем плагина, например пусть плагин
называется privet, тогда создаем папку с именем privet в папке плагинов.

Структура папки плагина privet:

1. файл privet.py - функциональность самого плагина (обязательно должен быть присутствовать)
2. файл privet.md - Справочная информация пользователю о плагине. (необязательно)

Пользователь может запросить справочную информацию о плагине с помощью команды **/help имя_плагина**, тогда логика
вывода справки будет следующая:

1. ищется файл справочной информации плагина **имя_плагина.md** в папке плагина
2. если файл справочной информации плагина не найден, то будет выводиться docstring модуля.
3. если не найден docstring плагина, то выводится сообщение о том что справочной информации данного плагина нет.

### Пример файла плагина который может быть подключен к боту:

Создайте файл например с именем privet.py и сохраните его в папку плагинов (в моём случае это plugins_bot)

```python
"""
Example plugins for tlgbotcore (send hi)
"""

from telethon import events


@tlgbot.on(events.NewMessage(pattern='hi'))
async def handler(event):
    await event.reply('hey')
```

Если нужно ограничить доступ к боту ограниченному кругу лиц, то нужно использовать следующий декоратор в плагинах бота:

```python
@tlgbot.on(events.NewMessage(chats=tlgbot.settings.get_all_user_id(), pattern='hi'))
```

### Запуск проекта:

```bash
python start_tlgbotcore.py
```
