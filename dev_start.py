#!/usr/bin/env python3
"""
Скрипт для запуска бота в режиме разработки с отладочным логированием.
"""

from cfg import config_tlg as config
from bot.tlgbotcore.tlgbotcore import TlgBotCore
from bot.tlgbotcore.logging_config import setup_dev_logging
import asyncio


async def _main_async():
    tlg = TlgBotCore(session=config.TLG_APP_NAME,
                     plugin_path='bot/plugins_bot',
                     connection_retries=None,
                     api_id=config.TLG_APP_API_ID,
                     api_hash=config.TLG_APP_API_HASH,
                     bot_token=config.I_BOT_TOKEN,
                     admins=config.TLG_ADMIN_ID_CLIENT,
                     proxy_key=config.TLG_PROXY_KEY,
                     proxy_server=config.TLG_PROXY_SERVER,
                     proxy_port=config.TLG_PROXY_PORT,
                     type_db=config.TYPE_DB,
                     settings_db_path=config.SETTINGS_DB_PATH)

    await tlg.start_core(bot_token=config.I_BOT_TOKEN)
    await tlg.disconnected


def main():
    setup_dev_logging()  # Включает DEBUG логи и icecream
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
