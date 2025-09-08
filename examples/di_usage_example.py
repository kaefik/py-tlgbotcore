"""Пример использования DI-контейнера вместо прямых импортов."""

import asyncio
from bot.tlgbotcore.di_container import DIContainer, BotFactory, IConfig, ISettingsStorage
from bot.tlgbotcore.storage_factory import StorageFactory


class ConfigAdapter:
    """Адаптер для существующего конфига."""
    
    def __init__(self, config_module):
        self.TLG_APP_NAME = config_module.TLG_APP_NAME
        self.TLG_APP_API_ID = config_module.TLG_APP_API_ID
        self.TLG_APP_API_HASH = config_module.TLG_APP_API_HASH
        self.I_BOT_TOKEN = config_module.I_BOT_TOKEN
        self.TLG_ADMIN_ID_CLIENT = config_module.TLG_ADMIN_ID_CLIENT
        self.TYPE_DB = config_module.TYPE_DB
        self.SETTINGS_DB_PATH = config_module.SETTINGS_DB_PATH


async def main_with_di():
    """Запуск бота через DI-контейнер."""
    
    # Настройка контейнера
    container = DIContainer()
    
    # Регистрация конфига
    from cfg import config_tlg as config
    config_adapter = ConfigAdapter(config)
    container.register_instance(IConfig, config_adapter)
    
    # Регистрация хранилища через фабрику
    def create_storage():
        return StorageFactory.create_storage(
            config.TYPE_DB,
            config.SETTINGS_DB_PATH,
            config.TLG_ADMIN_ID_CLIENT
        )
    
    container.register_factory(ISettingsStorage, create_storage)
    
    # Создание бота через фабрику
    bot_factory = BotFactory(container)
    bot = bot_factory.create_bot()
    
    # Запуск
    await bot.start_core(bot_token=config.I_BOT_TOKEN)
    await bot.disconnected


if __name__ == "__main__":
    asyncio.run(main_with_di())
