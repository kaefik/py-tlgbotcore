
# py-tlgbotcore

**py-tlgbotcore** — расширяемое ядро Telegram-бота на Telethon с системой плагинов, поддержкой SQLite/CSV, мультиязычностью и современным стеком разработки.

> Вдохновлён [UniBorg](https://github.com/udf/uniborg). Для Python 3.12+.

---

## 🚀 Возможности

- 🔌 Плагины: расширяйте функциональность без изменения ядра
- 🗄️ Хранилище: SQLite или CSV для пользователей и настроек
- 🌍 Мультиязычность: встроенная поддержка локалей (ru, en, ba, tt, ba_lat, tt_lat)
- 👥 Гибкое управление доступом и ролями
- 🛡️ Безопасная загрузка плагинов (валидация, логирование)
- 🧩 DI-контейнер для внедрения зависимостей
- 📝 Современные инструменты: type hints, ruff, mypy, pytest
- 🐳 Docker/Docker Compose-ready

---

## 📁 Структура проекта

```
py-tlgbotcore/
├── main.py                # точка входа (пример)
├── dev_start.py           # запуск в dev-режиме (DEBUG)
├── bot/
│   ├── tlgbotcore/        # ядро, DI, i18n, модели, storage
│   └── plugins_bot/       # плагины (см. ниже)
│   └── locales/           # json-файлы поддержки различных языков
├── cfg/
│   └── config_tlg.py      # ваш конфиг (на основе config_tlg_example.py)
├── logs/                  # логи
├── README.md
└── pyproject.toml
```

---

## 🧩 Плагины (plugins_bot)

Каждый плагин — отдельная папка с файлом `имя_плагина.py` и (опционально) `имя_плагина.md` (help).

**Встроенные плагины:**
- `_core` — админ-команды (загрузка/выгрузка/список плагинов, управление доступом)
- `noauthbot` — сообщения неавторизованным пользователям
- `inline_button` — пример inline-кнопок
- `runner_questionnaire` — анкеты на JSON
- `runner_questionnaire_inline_button` — анкеты с inline-кнопками
- `setlang` — смена языка пользователя /setlang
- `start_cmd` — обработка /start
- `privet` — пример простого плагина с i18n

**Пример плагина:**
```python
from telethon import events

@tlgbot.on(tlgbot.cmd('hi'))
async def handler(event):
    await event.reply('hey')
```

**Help по плагину:**
- `/help имя_плагина` — покажет .md или docstring

---

## Команды администратора


Бот поддерживает следующие команды для администраторов:

| Команда | Описание |
|---------|----------|
| `/adduser` | Добавить пользователя по ID (бот запросит ID, добавит с ролью user) |
| `/deluser` | Удалить пользователя по ID (бот запросит ID, удаляет из БД, кроме админов) |
| `/listusers` | Показать всех пользователей с доступом к боту |
| `/plugins` | Список загруженных плагинов с описанием |
| `/load <plugin>` | Загрузить или перезагрузить плагин (например, `/load privet`) |
| `/reload <plugin>` | То же, что и `/load` |
| `/unload <plugin>` | Выгрузить плагин (например, `/unload privet`) |
| `/help <plugin>` | Показать справку по плагину (docstring или .md) |

**Примечания:**
- Для команд `/adduser` и `/deluser` бот ведёт диалог: запрашивает ID пользователя, проверяет корректность ввода.
- `/help <plugin>` ищет файл справки `<plugin>.md` или выводит docstring, если файл не найден.
- Нельзя выгрузить или перезагрузить плагин `_core` (защита от ошибок).
- Все команды доступны только администраторам (ID из `TLG_ADMIN_ID_CLIENT`).



---

## ⚙️ Быстрый старт

1. **Клонируйте и установите зависимости:**
   ```bash
   git clone https://github.com/kaefik/py-tlgbotcore.git
   cd py-tlgbotcore
   uv sync
   # Для разработки:
   uv sync --extra dev
   ```
2. **Создайте конфиг:**
   ```bash
   cp cfg/config_tlg_example.py cfg/config_tlg.py
   # и заполните свои значения (API_ID, HASH, TOKEN, ADMINS...)
   ```
3. **Запуск:**
    `uv run -m bot.start_tlgbotcore`

---

## 🛠️ Качество кода

Проверки и тесты:
```bash
uv run ruff check .        # линтер
uv run ruff format .       # автоформат
uv run mypy bot/           # типизация
uv run pytest              # тесты (добавьте свои)
```

---

## 🐳 Docker / Docker Compose

**Docker:**
```bash
docker build -t py-tlgbotcore .
docker run -d --name tlgbotcore --restart unless-stopped -v ./logs:/app/logs:z -v ./data:/app/data:z -v ./cfg/config_tlg.py:/app/cfg/config_tlg.py:z py-tlgbotcore

```


---

## 📝 Конфиг (cfg/config_tlg.py)

```python
TLG_APP_NAME = "your_app"
TLG_APP_API_ID = 12345678
TLG_APP_API_HASH = "your_hash"
I_BOT_TOKEN = "your_token"
TLG_ADMIN_ID_CLIENT = [123456789]
TYPE_DB = "SQLITE"  # или "CSV"
SETTINGS_DB_PATH = "settings.db"
DEFAULT_LANG = "ru"
AVAILABLE_LANGS = {"ru": "Русский", "en": "English", ...}
```

Можно использовать переменные окружения вместо конфига.

---

## 🛡️ Безопасность и архитектура

- Плагины изолированы, но загружаются динамически 
- Все SQL-запросы параметризованы
- DI-контейнер для слабой связанности
- Логирование ошибок и действий

**Рекомендации:**
- Не храните токены в git!
- Для production — sandbox для плагинов, CI/CD, тесты

---

## 🏆 Автор и лицензия

- Автор: [kaefik](https://github.com/kaefik)
- Лицензия: MPL 2.0

