О проекте

[py-tlgbotcore](https://github.com/kaefik/py-tlgbotcore) - Основа телеграмм бота которому можно расширять функционал с
помощью плагинов

!!! **вдохновлен проектом [UniBorg](https://github.com/udf/uniborg) и взят за основу и тем самым изучая проект понимаешь
глубже библиотеку Telethon**

## Реализованные возможности:

* подключение плагинов которые реализуют основную функциональность бота.

### Основная функциональность

## Настройка проекта для запуска

### Библиотеки:

* ```bash
  pip3 install Telethon
  ```

  или просто выполняем

  ```bash
  pip install -r requirements.txt
  ```

### Конфигурационные файлы проекта:

* **config.py** - за основу можно взять файл config-example.py

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

### Запуск проекта:

```bash
python start_tlgbotcore.py
```

## Плагины которые доступны:

1. **_core.py** - плагин, который реализует административные команды по плагинам. Доступ имеет администраторы.

Команды:

* /plugins - выводит список подключенных плагинов к боту
* /load имя_плагина или /reload имя_плагина — загружает заново файл имя_плагина.py из папки плагинов
* /unload имя_плагина или /disable имя_плагина или /remove имя_плагина или — отключает плагин от бота
* /help имя_плагина — вывод справочной информации плагина

2. **youtube2mp3.py** - ютуб видео преобразует в звуковой файл формата mp3. Нужно отправить ссылку на ютуб видео.

Команды:

* /delfiles - удаление файлов mp3 на сервере пользователя который вызвал команду.
