import asyncio
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiohttp import ClientConnectorError
SYSTEM_DIR = Path("system_files")
CONFIG_PATH = SYSTEM_DIR / "config.json"
USERS_PATH = SYSTEM_DIR / "telegram_users.json"


def is_tg_first_launch() -> bool:
    if not CONFIG_PATH.exists():
        return True
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return bool(data.get("tg_config", True))
    except (json.JSONDecodeError, OSError):
        return True


def _set_tg_first_launch_state(value: bool) -> None:
    SYSTEM_DIR.mkdir(exist_ok=True)
    data = {}
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data["tg_config"] = value
    CONFIG_PATH.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def _load_registered_users() -> dict:
    if not USERS_PATH.exists():
        return {}
    try:
        return json.loads(USERS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registered_users(data: dict) -> None:
    SYSTEM_DIR.mkdir(exist_ok=True)
    USERS_PATH.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


class TelegramBotService:
    def __init__(self, token: str, auth_code: str):
        self.token = token
        self.auth_code = str(auth_code)
        self.awaiting_name = set()

        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()

        self.router = Router()
        self._register_handlers()

        self.dp.include_router(self.router)

    def _register_handlers(self) -> None:
        @self.router.message(CommandStart())
        async def start_handler(message: Message) -> None:
            user_id = str(message.from_user.id)
            registered = _load_registered_users()

            if user_id in registered:
                await message.answer("Вы уже зарегистрированы.")
                return

            self.awaiting_name.add(user_id)
            await message.answer("Программа рапознала этот запуск режима, как первый. Введите код на вашем экране.")

        @self.router.message()
        async def message_handler(message: Message) -> None:
            user_id = str(message.from_user.id)
            registered = _load_registered_users()

            if user_id in registered:
                await message.answer("Вы уже зарегистрированы.")
                return

            if user_id not in self.awaiting_name:
                await message.answer("Нажмите /start для начала регистрации.")
                return

            text = (message.text or "").strip()
            if text == self.auth_code:
                registered[user_id] = "moderator"
                _save_registered_users(registered)
                self.awaiting_name.discard(user_id)
                _set_tg_first_launch_state(False)
                await message.answer("✅ Код принят. Вы зарегистрированы как модератор.")
                return

            await message.answer("Код неверный. Попробуйте ещё раз или нажмите /start.")

    async def _run(self) -> None:
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    def run(self) -> None:
        try:
            asyncio.run(self._run())
        except ClientConnectorError:
            print(
                "[TG BOT] Не удалось подключиться к api.telegram.org. "
                "Проверь интернет/прокси/VPN и запусти бот снова."
            )
        except Exception as error:
            print(f"[TG BOT] Ошибка запуска бота: {error}")
