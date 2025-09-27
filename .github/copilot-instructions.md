# AI Agent Instructions for py-tlgbotcore

This document provides essential knowledge for AI agents working with the py-tlgbotcore codebase. It covers architecture, workflows, conventions, and integration points to help you be immediately productive.

## Project Overview

**py-tlgbotcore** is an extensible Telegram bot framework built on Telethon with a plugin system, SQLite/CSV storage, multilingual support, and a modern development stack (Python 3.12+). The project is inspired by [UniBorg](https://github.com/udf/uniborg).

## Architecture

### Core Components

1. **TlgBotCore** (`bot/tlgbotcore/tlgbotcore.py`): Central class extending `TelegramClient` with plugin loading, command handling, and access control.

2. **DI Container** (`bot/tlgbotcore/di_container.py`): Dependency injection system for cleaner component coupling.

3. **Storage System**: Dual storage options:
   - SQLite (`bot/tlgbotcore/sqliteutils/`)
   - CSV (`bot/tlgbotcore/csvdbutils/`)

4. **I18n** (`bot/tlgbotcore/i18n.py`): Localization system supporting multiple languages.

5. **Plugin System**: Each plugin is a separate module with potential `.md` help file.

### Data Flow

1. Commands trigger registered event handlers in plugins
2. Handlers use injected services (storage, i18n) through the DI container
3. User authorization is checked automatically through command decorators

## Development Workflow

### Environment Setup

```bash
# Clone and setup dependencies
git clone https://github.com/kaefik/py-tlgbotcore.git
cd py-tlgbotcore
uv sync  # or 'uv sync --extra dev' for development

# Create config from example
cp cfg/config_tlg_example.py cfg/config_tlg.py
# Edit config with API keys, tokens, admin IDs
```

### Running the Bot

```bash
uv run -m bot.start_tlgbotcore  # Normal run
python dev_start.py  # Debug run
```

### Code Quality

```bash
uv run ruff check .    # Linting
uv run ruff format .   # Auto-formatting
uv run mypy bot/       # Type checking
uv run pytest          # Run tests
```

### Docker

```bash
docker build -t py-tlgbotcore .
docker run -d --name tlgbotcore --restart unless-stopped \
  -v ./logs:/app/logs:z -v ./data:/app/data:z \
  -v ./cfg/config_tlg.py:/app/cfg/config_tlg.py:z py-tlgbotcore
```

## Project-Specific Patterns

### Plugin Development

1. Create a directory in `bot/plugins_bot/your_plugin_name/`
2. Add a Python file matching the directory name (`your_plugin_name.py`)
3. Optionally add help documentation (`your_plugin_name.md`)

```python
# Example plugin: bot/plugins_bot/your_plugin/your_plugin.py
@tlgbot.on(tlgbot.cmd('command'))  # Regular command
async def handler(event):
    # Get user language preference
    user = tlgbot.settings.get_user(event.sender_id)
    lang = getattr(user, "lang", tlgbot.i18n.default_lang)
    
    # Use i18n for localization
    await event.reply(tlgbot.i18n.t("message_key", lang=lang))

# Admin-only command
@tlgbot.on(tlgbot.admin_cmd('admin_command'))
async def admin_handler(event):
    # Your code here
```

### Internationalization

1. Store translations in JSON files in `bot/locales/` (ru.json, en.json, etc.)
2. Access translations with `tlgbot.i18n.t('key', lang=lang, **kwargs)`
3. Use fallbacks wisely (see `_t` method in `tlgbotcore.py`)

Example locale file:
```json
{
  "greeting": "Hello, {name}!",
  "command_help": "Use /help for assistance"
}
```

### User Management

Users are stored with roles (admin/user) and language preferences. Access control is handled automatically through command decorators:

- `tlgbot.cmd()` - Regular command for authorized users
- `tlgbot.admin_cmd()` - Admin-only command

## Integration Points

1. **Storage**: Implement `ISettingsStorage` for custom storage backends
2. **Config**: Environment variables or `cfg/config_tlg.py`
3. **Telethon Events**: Use Telethon event system for complex handlers

## Critical Files

- `bot/tlgbotcore/tlgbotcore.py` - Core bot functionality
- `bot/tlgbotcore/_core.py` - Admin commands and plugin management
- `bot/tlgbotcore/di_container.py` - Dependency injection system
- `cfg/config_tlg.py` - Bot configuration (based on `config_tlg_example.py`)
- `bot/tlgbotcore/models.py` - Data models for users and roles

---

# Copilot Usage Guidelines

## Стиль ответов
- Отвечай только на русском, неформально.
- Кратко и конкретно, без воды.
- Формат: План (если нужно) → Код/Решение → Краткое «зачем» (если неочевидно).
- Никаких «можно так» — только одно конкретное решение.
- Ограничения (например, политика контента) — дай максимум допустимого и объясни почему.
- Девиз: «Чем короче, тем лучше, но без потери смысла».

## Код и технологии
- Соблюдай линтеры (`ruff`, `mypy`, `pytest`).
- Используй современные практики (async/await, typing, dataclasses/pydantic).
- Предпочитай:
  - Telethon для Telegram API
  - SQLite через `DatabaseManager`
  - Плагины через `tlgbotcore`
- Не использовать:
  - jQuery, eval, небезопасные конструкции
- Улучшающие или нетривиальные подходы помечай как *(спекуляция)*.

## Документация проекта
- Все изменения фиксируй в `TODO.md` в формате markdown.
- Формат записи в `TODO.md`:
  - Заголовок `# TODO`
  - Раздел `## Журнал`
  - Под каждый день: `### YYYY-MM-DD`
  - Список изменений в виде маркеров:
    - `[tag] Краткое описание (1–2 строки)`
    - Можно добавить хэш коммита или ветку.

## Git и коммиты
- Все коммиты должны быть **на русском языке**.
- Формат коммита:
  - первая строка — коротко и по делу (≤ 72 символов),
  - дальше (опционально) — подробности изменений через пустую строку.
- Используй повелительное наклонение: «Добавить», «Исправить», «Удалить».
- Примеры:
  - `Добавить поддержку /today в плагине`
  - `Исправить падение при пустом сообщении`
  - `Обновить зависимости и форматирование`
- Группируй изменения по смыслу — один коммит = одна задача.
- Ветки именуй на латинице: `feature/...`, `fix/...`.
- Pull Request — описание на русском, с чеклистом «что сделал» и «как проверить».
- Автолинтер в CI: коммиты не проходят без `ruff`, `mypy`, `pytest`.
- Конвенция тегов для TODO.md и коммитов: `[feat]`, `[fix]`, `[refactor]`, `[docs]`.

### Шаблон Pull Request
```markdown
# Что сделано
- [ ] Краткий список изменений

# Как проверить
1. Шаг 1
2. Шаг 2

# Дополнительно
- Ссылка на issue или задачу (если есть)
- Замечания или вопросы
```