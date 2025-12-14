import asyncio
import json
import os
import threading
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8529361701:AAHNWQ0KZDRHOr2-0GfdmMNhAsrO8bFe_sM"
SUBSCR_FILE = "subscribers.json"


def load_subscribers():
    if os.path.exists(SUBSCR_FILE):
        with open(SUBSCR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_subscribers(subs):
    with open(SUBSCR_FILE, "w", encoding="utf-8") as f:
        json.dump(subs, f, indent=2, ensure_ascii=False)


bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    chat_id = message.chat.id
    subs = load_subscribers()
    if chat_id not in subs:
        subs.append(chat_id)
        save_subscribers(subs)
        await message.answer("Ты зарегистрирован!")
    else:
        await message.answer("Ты уже зарегистрирован.")


async def send_message_to_all(text: str):
    subs = load_subscribers()
    for cid in subs:
        try:
            await bot.send_message(cid, text)
        except Exception as e:
            print(f"Ошибка у {cid}: {e}")


def input_thread(loop):
    """Запускается в отдельном потоке и передаёт задачи в event loop."""
    print("Вводи сообщение для рассылки. quit — выйти.")
    while True:
        text = input("> ").strip()
        if text.lower() == "quit":
            break
        if text:
            asyncio.run_coroutine_threadsafe(send_message_to_all(text), loop)


async def main():
    print(">>> Запускаю polling...")
    loop = asyncio.get_running_loop()

    # Запуск input в отдельном потоке
    threading.Thread(target=input_thread, args=(loop,), daemon=True).start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())