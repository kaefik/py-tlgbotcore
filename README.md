# py-tlgbotcore

[py-tlgbotcore](https://github.com/kaefik/py-tlgbotcore) - Основа Telegram бота с расширяемым функционалом через плагины.

> Вдохновлён проектом [UniBorg](https://github.com/udf/uniborg) для изучения библиотеки Telethon.

## Возможности

- 🔌 Система плагинов для расширения функциональности
- 🗄️ Поддержка SQLite и CSV для хранения настроек
- 👥 Управление правами доступа и администраторами
- 🎨 Цветное логирование с файловым выводом
- 🔧 Type hints и современные инструменты разработки

## Встроенные плагины

- **_core** - административные команды для управления плагинами и доступом
- **noauthbot** - уведомления неавторизованным пользователям
- **inline_button** - демонстрация inline кнопок (`/inline`)
- **runner_questionnaire** - интерпретатор анкет с JSON-синтаксисом
- **runner_questionnaire_inline_button** - анкеты с inline кнопками

## Команды администратора

Бот поддерживает следующие команды для управления доступом пользователей:

| Команда | Описание | Пример использования |
|---------|----------|----------------------|
| `/adduser` | Добавление нового пользователя с доступом к боту | `/adduser` (далее бот запросит ID пользователя) |
| `/deluser` | Удаление пользователя из списка доступа | `/deluser` (далее бот запросит ID пользователя для удаления) |
| `/listusers` | Просмотр списка пользователей с доступом к боту | `/listusers` |
| `/load` | Загрузка плагина | `/load имя_плагина` |
| `/unload` | Выгрузка плагина | `/unload имя_плагина` |
| `/reload` | Перезагрузка плагина | `/reload имя_плагина` |
| `/plugins` | Просмотр списка загруженных плагинов | `/plugins` |

## Быстрый старт

### 1. Установка зависимостей

```bash
# Клонируем репозиторий
git clone https://github.com/kaefik/py-tlgbotcore.git
cd py-tlgbotcore

# Устанавливаем зависимости
uv sync

# Для разработки (с линтерами и тестами)
uv sync --extra dev
```

### 2. Настройка конфигурации

Создайте `cfg/config_tlg.py` на основе `cfg/config_tlg_example.py`:

```python
# Telegram API (получить на https://my.telegram.org)
TLG_APP_NAME = "your_app_name"
TLG_APP_API_ID = 12345678
TLG_APP_API_HASH = "your_api_hash"

# Bot Token (получить у @BotFather)
I_BOT_TOKEN = "1234567890:your_bot_token"

# ID администраторов
TLG_ADMIN_ID_CLIENT = [123456789]

# Тип БД: "SQLITE" или "CSV"
TYPE_DB = "SQLITE"
SETTINGS_DB_PATH = "settings.db"

# Прокси (опционально)
TLG_PROXY_SERVER = None
TLG_PROXY_PORT = None
TLG_PROXY_KEY = None
```

### 3. Запуск

```bash
# Продакшн режим
uv run tlgbotcore

# Режим разработки (с DEBUG логами)
python dev_start.py
```

## Разработка

### Инструменты качества кода

```bash
# Проверка кода
uv run ruff check .

# Форматирование
uv run ruff format .

# Проверка типов
uv run mypy bot/

# Запуск тестов
uv run pytest
```

### Переменные окружения

Вместо `cfg/config_tlg.py` можно использовать переменные окружения:

```bash
export TLG_APP_NAME="your_app"
export TLG_APP_API_ID="12345678"
export TLG_APP_API_HASH="your_hash"
export I_BOT_TOKEN="your_token"
export TLG_ADMIN_ID_CLIENT="123456789,987654321"
export TYPE_DB="SQLITE"
export SETTINGS_DB_PATH="settings.db"
```

## Развёртывание

### Systemd сервис

Создайте `/etc/systemd/system/tlgbotcore.service`:

```ini
[Unit]
Description=Telegram Bot Core
After=network.target

[Service]
Type=simple
User=tlgbot
WorkingDirectory=/opt/py-tlgbotcore
ExecStart=/opt/py-tlgbotcore/.venv/bin/python -m bot.start_tlgbotcore
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tlgbotcore.service
sudo systemctl start tlgbotcore.service
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


### Docker

```bash
# Сборка образа
docker build -t py-tlgbotcore .

# Запуск с переменными окружения
docker run -d \
  --name tlgbotcore \
  --restart unless-stopped \
  -e TLG_APP_NAME="your_app" \
  -e TLG_APP_API_ID="12345678" \
  -e TLG_APP_API_HASH="your_hash" \
  -e I_BOT_TOKEN="your_token" \
  -e TLG_ADMIN_ID_CLIENT="123456789" \
  -v ./logs:/app/logs \
  -v ./settings.db:/app/settings.db \
  py-tlgbotcore

# Логи
docker logs -f tlgbotcore
```

### Docker Compose

```yaml
version: '3.8'
services:
  tlgbotcore:
    build: .
    restart: unless-stopped
    environment:
      - TLG_APP_NAME=your_app
      - TLG_APP_API_ID=12345678
      - TLG_APP_API_HASH=your_hash
      - I_BOT_TOKEN=your_token
      - TLG_ADMIN_ID_CLIENT=123456789
    volumes:
      - ./logs:/app/logs
      - ./settings.db:/app/settings.db
```
