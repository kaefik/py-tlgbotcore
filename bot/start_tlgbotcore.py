import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cfg.config_tlg as config
from tlgbotcore import TlgBotCore

import logging

logging.basicConfig(level=logging.INFO)

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
                 type_db=config.TYPE_DB)

tlg.run_until_disconnected()
