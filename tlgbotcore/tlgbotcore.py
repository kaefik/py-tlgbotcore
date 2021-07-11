import os
from telethon import TelegramClient  # , events, connection, Button
import telethon.utils
import telethon.events
from . import hacks

import asyncio
import logging
from pathlib import Path
import importlib.util
import inspect


class TlgBotCore(TelegramClient):
    def __init__(self, session, *, plugin_path="plugins", storage=None, admins=[],
                 bot_token=None, proxy_server=None, proxy_port=None, proxy_key=None, **kwargs):
        self._logger = logging.getLogger(session)
        self._name = session
        self._plugins = {}
        self._plugin_path = plugin_path
        self.admins = admins

        if bot_token is None:
            print("Не указан параметр bot_token.")

        super().__init__(session, **kwargs)

        # ------- Загрузка плагинов бота
        # This is a hack, please avert your eyes
        # We want this in order for the most recently added handler to take
        # precedence
        self._event_builders = hacks.ReverseList()

        if proxy_server and proxy_port and proxy_key:
            self._logger.info(f"Trying connect with Proxy...")
            # TODO: сделать чтобы подключался бот через прокси сервер
            self.loop.run_until_complete(self._async_init(bot_token=bot_token))
        else:
            self._logger.info(f"Trying connect without Proxy...")
            self.loop.run_until_complete(self._async_init(bot_token=bot_token))

        core_plugin = Path(__file__).parent / "_core.py"
        self.load_plugin_from_file(core_plugin)

        if not os.path.exists(self._plugin_path):
            self._logger.info(f"Нет папки с плагинами {self._plugin_path}")
            return

        # получим все папки плагинов
        content = os.listdir(self._plugin_path)

        self._logger.info(content)

        for directory in content:
            if os.path.isdir(f"{self._plugin_path}/{directory}"):
                self._logger.info(f"папка плагина {directory}")
                for p in Path().glob(f"{self._plugin_path}/{directory}/*.py"):
                    self.load_plugin_from_file(p)
        # ------- END Загрузка плагинов бота

    async def _async_init(self, **kwargs):
        await self.start(**kwargs)
        self.me = await self.get_me()
        self.uid = telethon.utils.get_peer_id(self.me)

    def load_plugin(self, shortname):
        self.load_plugin_from_file(f"{self._plugin_path}/{shortname}.py")

    def load_plugin_from_file(self, path):
        path = Path(path)
        shortname = path.stem
        name = f"_TlgBotCorePlugins.{self._name}.{shortname}"

        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)

        mod.tlgbot = self  # поле tlgbot отвечает за то как нужно будет указываться файлах плагинов
        # декоратор, см. например _core.py

        mod.logger = logging.getLogger(shortname)

        spec.loader.exec_module(mod)

        self._plugins[shortname] = mod
        self._logger.info(f"Successfully loaded plugin {shortname}")

    async def remove_plugin(self, shortname):
        name = self._plugins[shortname].__name__

        for i in reversed(range(len(self._event_builders))):
            ev, cb = self._event_builders[i]
            if cb.__module__ == name:
                del self._event_builders[i]

        plugin = self._plugins.pop(shortname)
        if callable(getattr(plugin, 'unload', None)):
            try:
                unload = plugin.unload()
                if inspect.isawaitable(unload):
                    await unload
            except Exception:
                self._logger.exception(f'Unhandled exception unloading {shortname}')

        del plugin
        self._logger.info(f"Removed plugin {shortname}")

    def await_event(self, event_matcher, filter=None):
        fut = asyncio.Future()

        @self.on(event_matcher)
        async def cb(event):
            try:
                if filter is None or await filter(event):
                    fut.set_result(event)
            except telethon.events.StopPropagation:
                fut.set_result(event)
                raise

        fut.add_done_callback(
            lambda _: self.remove_event_handler(cb, event_matcher))

        return fut

    def cmd(self, command, pattern=None, admin_only=False):
        if self.me.bot:
            command = fr'{command}(?:@{self.me.username})?'

        if pattern is not None:
            pattern = fr'{command}\s+{pattern}'
        else:
            pattern = command

        if not self.me.bot:
            pattern = fr'^\.{pattern}'
        else:
            pattern = fr'^\/{pattern}'
        pattern = fr'(?i){pattern}$'

        if self.me.bot and admin_only:
            allowed_users = self.admins
        else:
            allowed_users = None

        return telethon.events.NewMessage(
            outgoing=not self.me.bot,
            from_users=allowed_users,
            pattern=pattern
        )

    def admin_cmd(self, command, pattern=None):
        return self.cmd(command, pattern, admin_only=True)
