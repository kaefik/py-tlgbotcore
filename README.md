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

### Команды _core.py - плагина, который реализует административные команды по плагинам

* /plugins - выводит список подключенных плагинов к боту
* /load имя_плагина или /reload имя_плагина - загружает заново файл имя_плагина.py из папки плагинов
* /unload имя_плагина или /disable имя_плагина или /remove имя_плагина или - отключает плагин от бота