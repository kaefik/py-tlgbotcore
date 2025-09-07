import os
from typing import Optional, List, Dict, Any, Union
from telethon import TelegramClient  # , events, connection, Button
import telethon.utils
import telethon.events
from . import hacks
from .models import Role

import asyncio
import logging
from pathlib import Path
import importlib.util
import inspect


class TlgBotCore(TelegramClient):
    def __init__(self, session: str, *, plugin_path: str = "plugins", storage: Optional[Any] = None, admins: List[int] = [],
                 bot_token: Optional[str] = None, proxy_server: Optional[str] = None, proxy_port: Optional[int] = None, proxy_key: Optional[str] = None, type_db: str = 'SQLITE', settings_db_path: str = 'settings.db', **kwargs: Any) -> None:
        self._logger = logging.getLogger(session)
        self._name = session
        self._plugins: Dict[str, Any] = {}
        self._plugin_path = plugin_path
        # self.admins = admins

        self._logger.info(type_db)
        self.settings = None

        # настройки пользователей бота в том числе и администратора admin_client
        if type_db == 'SQLITE':
            from .sqliteutils import SettingUser
            from .models import User, Role
            name_file_settings = settings_db_path
            if not os.path.exists(name_file_settings):
                self._logger.info('Нет файла БД настроек')
                name_admin = ''
                settings = SettingUser(namedb=name_file_settings)

                for admin_client in admins:
                    admin_User = User(id=admin_client, role=Role.admin, active=True)
                    settings.add_user(admin_User)

            else:
                self._logger.info('Есть файл БД настроек!')
                settings = SettingUser(namedb=name_file_settings)
            self.settings = settings
        elif type_db == 'CSV':
            name_file_settings = 'settings_db'
            from .csvdbutils.csvdbutils import SettingUser
            from .models import User, Role
            self._logger.info(f"БД типа CSV")
            if not os.path.exists(name_file_settings):
                self._logger.info('Нет файла БД настроек')
                name_admin = ''
                settings = SettingUser(namedb=name_file_settings)

                for admin_client in admins:
                    admin_User = User(id=admin_client, role=Role.admin, active=True)
                    settings.add_user(admin_User)

            else:
                self._logger.info('Есть файл БД настроек!')
                settings = SettingUser(namedb=name_file_settings)
            self.settings = settings

        else:
            self._logger.info(f"Неправильный тип БД для настроек пользователя.")
            return

        # получение всех пользователей из БД
        if self.settings is not None:
            self.admins = self.settings.get_user_type_id(Role.admin)  # список администраторов бота
        else:
            self.admins = []
        self._logger.info(f"Админы ботов {self.admins}")
        # END настройки бота

        if bot_token is None:
            self._logger.info("Не указан параметр bot_token.")

        super().__init__(session, **kwargs)

        # # получим все папки плагинов
        # content = os.listdir(self._plugin_path)
        #
        # self._logger.info(content)
        #
        # for directory in content:
        #     if os.path.isdir(f"{self._plugin_path}/{directory}"):
        #         self._logger.info(f"папка плагина {directory}")
        #         for p in Path().glob(f"{self._plugin_path}/{directory}/*.py"):
        #             self.load_plugin_from_file(p)
        # ------- END Загрузка плагинов бота

    def refresh_admins(self) -> None:
        """Обновить список админов из хранилища настроек."""
        try:
            if self.settings is not None:
                self.admins = self.settings.get_user_type_id(Role.admin)
                self._logger.info(f"Обновлён список админов: {self.admins}")
            else:
                self.admins = []
        except Exception:
            self._logger.exception("Не удалось обновить список админов")

    async def _async_init(self, **kwargs: Any) -> None:
        await self.start(**kwargs)
        self.me = await self.get_me()
        self.uid = telethon.utils.get_peer_id(self.me)

    async def start_core(self, bot_token: Optional[str] = None) -> None:
        if bot_token is None:
            self._logger.info("Не указан параметр bot_token при запуске.")
        # старт клиента
        await self._async_init(bot_token=bot_token)
        # приоритет последних хэндлеров
        self._event_builders = hacks.ReverseList()
        # загрузка core-плагина
        core_plugin = Path(__file__).parent / "_core.py"
        self.load_plugin_from_file(core_plugin)
        # загрузка остальных плагинов
        if not os.path.exists(self._plugin_path):
            self._logger.info(f"Нет папки с плагинами {self._plugin_path}")
            return
        self.load_all_plugins()

    def load_plugin(self, shortname: str) -> None:
        self.load_plugin_from_file(f"{self._plugin_path}/{shortname}.py")

    def load_all_plugins(self) -> None:
        """
        загрузка всех плагинов
        """
        # получим все папки плагинов
        content = os.listdir(self._plugin_path)

        self._logger.info(content)

        for directory in content:
            if os.path.isdir(f"{self._plugin_path}/{directory}"):
                self._logger.info(f"папка плагина {directory}")
                for p in Path().glob(f"{self._plugin_path}/{directory}/*.py"):
                    self.load_plugin_from_file(p)
        # ------- END Загрузка плагинов бота

    def load_plugin_from_file(self, path: Union[str, Path]) -> bool:
        path = Path(path)
        shortname = path.stem
        name = f"_TlgBotCorePlugins.{self._name}.{shortname}"

        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            self._logger.error(f"Failed to create spec for {path}")
            return False
        mod = importlib.util.module_from_spec(spec)

        # Добавляем атрибуты в модуль динамически
        setattr(mod, 'tlgbot', self)  # поле tlgbot отвечает за то как нужно будет указываться файлах плагинов
        # декоратор, см. например _core.py
        setattr(mod, 'logger', logging.getLogger(shortname))

        try:
            if spec.loader is not None:
                spec.loader.exec_module(mod)
            else:
                self._logger.error(f"No loader for {shortname}")
                return False  # pragma: no cover
        except Exception:
            self._logger.exception(f"Failed to load plugin {shortname} from {path}")
            return False

        # health-check: проверка наличия tlgbot и хэндлеров
        if not hasattr(mod, 'tlgbot'):
            self._logger.error(f"Plugin {shortname} missing 'tlgbot' reference")
            return False

        self._plugins[shortname] = mod
        self._logger.info(f"Successfully loaded plugin {shortname}")
        return True

    async def remove_plugin(self, shortname: str) -> None:
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

    def await_event(self, event_matcher: Any, filter: Optional[Any] = None) -> asyncio.Future[Any]:
        fut: asyncio.Future[Any] = asyncio.Future()

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

    def cmd(self, command: str, pattern: Optional[str] = None, admin_only: bool = False) -> telethon.events.NewMessage:
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

    def admin_cmd(self, command: str, pattern: Optional[str] = None) -> telethon.events.NewMessage:
        return self.cmd(command, pattern, admin_only=True)
