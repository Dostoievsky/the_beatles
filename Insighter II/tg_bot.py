import json
import os
import asyncio
from pathlib import Path
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import Router

def is_tg_first_launch(filename='config.json', key='tg_config'):
    full_path = os.path.join(os.getcwd(), 'system_files', filename)
    with open(full_path, 'r', encoding='utf-8') as file:
        return json.load(file)[key]




DATA_FILE = Path("telegram_data.json")

def load():
    if not DATA_FILE.exists():
        return {}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save(data: dict):
    DATA_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )






class TelegramBotService:
    def __init__(self, token: str, auth_code: str):
        self.token = token
        self.auth_code = str(auth_code)

        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()

        self.router = Router()
        self._register_handlers()

        self.dp.include_router(self.router)

    def _register_handlers(self):
        @self.router.message(CommandStart())
        async def start_handler(message: Message):
            print("TG /start from", message.from_user.id)  # ← ВОТ ЭТО
            data = load()
            data[str(message.from_user.id)] = {
                "role": "pending"
            }
            save(data)

            await message.answer(
                "Привет! Отправь код подтверждения."
            )

            data = load()
            data[str(message.from_user.id)] = {
                "role": "teacher"
            }
            save(data)

            await message.answer(
                "✅ Вы успешно зарегистрированы как учитель."
            )

    async def _run(self):
        # ВАЖНО
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    def run(self):
        asyncio.run(self._run())
