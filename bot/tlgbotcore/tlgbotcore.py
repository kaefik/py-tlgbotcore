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
    def __init__(self, session: str, *, plugin_path: str = "plugins", settings_storage: Optional[Any] = None, admins: List[int] = [],
                 bot_token: Optional[str] = None, proxy_server: Optional[str] = None, proxy_port: Optional[int] = None, proxy_key: Optional[str] = None, **kwargs: Any) -> None:
        self._logger = logging.getLogger(session)
        self._name = session
        self._plugins: Dict[str, Any] = {}
        self._plugin_path = plugin_path
        
        # Внедрение зависимости хранилища настроек
        self.settings = settings_storage
        
        # получение всех пользователей из БД
        if self.settings is not None:
            from .models import Role
            self.admins = self.settings.get_user_type_id(Role.admin)  # список администраторов бота
        else:
            self.admins = admins  # fallback к переданным админам
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
        """Асинхронная инициализация клиента."""
        try:
            await self.start(**kwargs)
            self.me = await self.get_me()
            self.uid = telethon.utils.get_peer_id(self.me)
            self._logger.info(f"Клиент инициализирован: {self.me.username or self.me.first_name}")
        except Exception as exc:
            self._logger.exception("Ошибка при инициализации клиента: %s", exc)
            raise

    async def start_core(self, bot_token: Optional[str] = None) -> None:
        """Асинхронный запуск ядра бота с инициализацией и загрузкой плагинов."""
        if bot_token is None:
            self._logger.warning("Не указан параметр bot_token при запуске.")
        
        try:
            # старт клиента
            await self._async_init(bot_token=bot_token)
            
            # приоритет последних хэндлеров
            self._event_builders = hacks.ReverseList()
            
            # загрузка core-плагина
            core_plugin = Path(__file__).parent / "_core.py"
            if not self.load_plugin_from_file(core_plugin):
                self._logger.error("Не удалось загрузить core плагин")
                return
            
            # загрузка остальных плагинов
            if not os.path.exists(self._plugin_path):
                self._logger.warning(f"Нет папки с плагинами {self._plugin_path}")
                return
            
            await self.load_all_plugins()
            self._logger.info("Ядро бота успешно запущено")
            
        except Exception as exc:
            self._logger.exception("Критическая ошибка при запуске ядра: %s", exc)
            raise

    def load_plugin(self, shortname: str) -> None:
        self.load_plugin_from_file(f"{self._plugin_path}/{shortname}.py")

    async def load_all_plugins(self) -> None:
        """Загрузка всех плагинов из папок с удалением старых обработчиков."""
        try:
            # Удаляем все старые плагины (кроме _core)
            for shortname in list(self._plugins.keys()):
                if shortname != "_core":
                    await self.remove_plugin(shortname)

            # получим все папки плагинов
            content = os.listdir(self._plugin_path)
            self._logger.info(f"Найдены директории: {content}")

            loaded_count = 0
            failed_count = 0

            for directory in content:
                dir_path = f"{self._plugin_path}/{directory}"
                if os.path.isdir(dir_path):
                    self._logger.info(f"Загружаем плагины из папки: {directory}")
                    for plugin_file in Path().glob(f"{dir_path}/*.py"):
                        if self.load_plugin_from_file(plugin_file):
                            loaded_count += 1
                        else:
                            failed_count += 1

            self._logger.info(f"Загрузка плагинов завершена: {loaded_count} успешно, {failed_count} с ошибками")

        except Exception as exc:
            self._logger.exception("Ошибка при загрузке плагинов: %s", exc)

    def load_plugin_from_file(self, path: Union[str, Path]) -> bool:
        """Загрузка плагина из файла с улучшенной обработкой ошибок."""
        path = Path(path)
        shortname = path.stem
        
        # Пропускаем системные файлы
        if shortname.startswith('__') or shortname.startswith('.'):
            return True
        
        # Запрещаем перезагрузку _core плагина
        if shortname == '_core' and shortname in self._plugins:
            self._logger.warning("Перезагрузка _core плагина запрещена")
            return False
        
        name = f"_TlgBotCorePlugins.{self._name}.{shortname}"
        
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                self._logger.error(f"Не удалось создать spec для {path}")
                return False
                
            mod = importlib.util.module_from_spec(spec)
            
            # Добавляем атрибуты в модуль динамически
            setattr(mod, 'tlgbot', self)
            setattr(mod, 'logger', logging.getLogger(shortname))
            
            # Загружаем модуль
            if spec.loader is not None:
                spec.loader.exec_module(mod)
            else:
                self._logger.error(f"Нет загрузчика для {shortname}")
                return False
            
            # Health-check: проверка наличия tlgbot
            if not hasattr(mod, 'tlgbot'):
                self._logger.error(f"Плагин {shortname} не содержит 'tlgbot' ссылку")
                return False
            
            self._plugins[shortname] = mod
            self._logger.info(f"Плагин {shortname} успешно загружен")
            return True
            
        except ImportError as exc:
            self._logger.error(f"Ошибка импорта плагина {shortname}: {exc}")
            return False
        except SyntaxError as exc:
            self._logger.error(f"Синтаксическая ошибка в плагине {shortname}: {exc}")
            return False
        except Exception as exc:
            self._logger.exception(f"Неожиданная ошибка при загрузке плагина {shortname} из {path}: {exc}")
            return False

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

        # Динамический фильтр доступа
        async def access_filter(event):
            user_id = event.sender_id
            if admin_only:
                allowed = user_id in (self.admins if self.settings is None else self.settings.get_user_type_id(Role.admin))
            else:
                allowed = user_id in (self.settings.get_all_user_id() if self.settings is not None else [])
            if not allowed:
                await event.reply("Нет доступа к этой команде.")
            return allowed

        self._logger.debug(f"cmd: pattern={pattern}, admin_only={admin_only}")

        return telethon.events.NewMessage(
            outgoing=not self.me.bot,
            pattern=pattern,
            func=access_filter  # <-- динамическая проверка
        )

    def admin_cmd(self, command: str, pattern: Optional[str] = None) -> telethon.events.NewMessage:
        return self.cmd(command, pattern, admin_only=True)
