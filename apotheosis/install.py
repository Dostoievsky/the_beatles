import asyncio
import json
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile


# ================= НАСТРОЙКИ =================

TOKEN = "8529361701:AAHNWQ0KZDRHOr2-0GfdmMNhAsrO8bFe_sM"
USERS_FILE = "subscribers.json"

# =============================================


router = Router()


# ---------- Работа с JSON ----------

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# ---------- Хэндлеры ----------

@router.message(CommandStart())
async def start(message: Message):
    users = load_users()
    tg_id = str(message.from_user.id)

    if tg_id in users:
        await message.answer(
            f"Ты уже зарегистрирован:\n{users[tg_id]}"
        )
        return

    await message.answer(
        "Привет!\nВведи имя и фамилию одним сообщением:"
    )


@router.message()
async def register(message: Message):
    users = load_users()
    tg_id = str(message.from_user.id)

    if tg_id in users:
        await message.answer("Аккаунт уже зарегистрирован.")
        return

    full_name = message.text.strip()

    if len(full_name.split()) < 2:
        await message.answer("Пожалуйста, введи имя и фамилию.")
        return

    users[tg_id] = full_name
    save_users(users)

    await message.answer(
        f"Регистрация завершена ✅\n{full_name}"
    )


# ---------- Рассылка файла ----------

async def send_file_to_all(bot: Bot, file_path: str):
    users = load_users()

    if not users:
        print("❌ Пользователей нет")
        return

    file = FSInputFile(file_path)

    print(f"📤 Рассылка файла {file_path}")

    for tg_id in users.keys():
        try:
            await bot.send_document(
                chat_id=int(tg_id),
                document=file
            )
            await asyncio.sleep(0.1)  # защита от лимитов
        except Exception as e:
            print(f"Не отправлено {tg_id}: {e}")

    print("✅ Рассылка завершена")


# ---------- Запуск ----------

async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # запуск бота
    polling = asyncio.create_task(dp.start_polling(bot))

    # консоль учителя
    while True:
        file_path = input(
            "\nВведите путь к файлу для рассылки (Enter — пропустить):\n"
        ).strip()

        if file_path:
            await send_file_to_all(bot, file_path)

        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())