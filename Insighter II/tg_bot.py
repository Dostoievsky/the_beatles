import asyncio
import os
import random
import sqlite3
import threading
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError


class TelegramBotService:
    def __init__(self, token: str, db_path: str = r"system_files/insighter.db"):
        self.token = token
        self.db_path = db_path

        self._thread = None
        self._loop = None
        self._ready = threading.Event()
        self._lock = threading.Lock()

        self._bot = None
        self._dispatcher = None

        self._registration_config = None
        self._user_states = {}

    @staticmethod
    def _normalize_name(value: str) -> str:
        return (value or "").strip().lower().replace("ё", "е")

    async def _safe_answer(self, message: Message, text: str) -> bool:
        try:
            await message.answer(text)
            return True
        except TelegramForbiddenError:
            print(f"Не удалось ответить пользователю {message.from_user.id}: бот заблокирован")
            self._user_states.pop(message.from_user.id, None)
            return False

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
        self._ready.wait(timeout=10)

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._bot = Bot(token=self.token)
        self._dispatcher = Dispatcher()
        self._register_handlers()
        self._ready.set()

        async def _runner():
            await self._dispatcher.start_polling(self._bot)

        try:
            self._loop.run_until_complete(_runner())
        finally:
            self._loop.run_until_complete(self._bot.session.close())
            self._loop.close()

    def _register_handlers(self):
        @self._dispatcher.message(CommandStart())
        async def on_start(message: Message):
            config = self._registration_config
            if not config:
                await self._safe_answer(message, "Регистрация сейчас недоступна.")
                return

            class_name = config["class_name"]
            tg_id = message.from_user.id

            if self._is_registered_in_class(class_name, tg_id):
                full_name = self._get_full_name_by_tg_id(class_name, tg_id)
                await self._safe_answer(
                    message,
                    f"Вы уже зарегестрированы как {full_name} - ученик {class_name}"
                )
                return

            self._user_states[tg_id] = {
                "step": "awaiting_name",
                "class_name": class_name,
            }
            await self._safe_answer(message, "Введите имя и фамилию одним сообщением.")

        @self._dispatcher.message(F.text)
        async def on_text(message: Message):
            tg_id = message.from_user.id
            state = self._user_states.get(tg_id)
            if not state:
                return

            text = (message.text or "").strip()

            if state["step"] == "awaiting_name":
                parts = text.split()
                if len(parts) != 2:
                    await self._safe_answer(message, "Введите имя и фамилию одним сообщением в формате: Имя Фамилия")
                    return
                state["full_name"] = f"{parts[0]} {parts[1]}"
                state["name"] = parts[0]
                state["surname"] = parts[1]
                state["step"] = "awaiting_room_code"
                await self._safe_answer(message, "Введите код комнаты.")
                return

            if state["step"] == "awaiting_room_code":
                if not self._registration_config:
                    await self._safe_answer(message, "Регистрация сейчас недоступна.")
                    self._user_states.pop(tg_id, None)
                    return

                if text != self._registration_config["room_code"]:
                    await self._safe_answer(message, "Неверный код комнаты. Попробуйте снова.")
                    return

                class_name = state["class_name"]
                self._upsert_student_telegram(
                    class_name=class_name,
                    name=state["name"],
                    surname=state["surname"],
                    telegram_id=tg_id,
                )
                await self._safe_answer(
                    message,
                    f"Регистрация прошла успешно. Вы зарегестрированы как {state['full_name']} - ученик {class_name}"
                )
                self._user_states.pop(tg_id, None)

    def enable_registration(self, class_name: str) -> str:
        room_code = str(random.randint(10000, 99999))
        self._registration_config = {
            "class_name": class_name,
            "room_code": room_code,
        }
        self._user_states.clear()
        return room_code

    def disable_registration(self):
        self._registration_config = None
        self._user_states.clear()

    def send_to_class(self, class_name: str, text: str = "", file_paths=None) -> int:
        file_paths = file_paths or []
        tg_ids = self._get_telegram_ids_by_class(class_name)

        if not tg_ids:
            return 0

        future = asyncio.run_coroutine_threadsafe(
            self._send_payload(tg_ids, text, file_paths),
            self._loop,
        )
        return future.result(timeout=120)

    async def _send_payload(self, tg_ids, text, file_paths):
        sent_count = 0
        for tg_id in tg_ids:
            try:
                if text.strip():
                    await self._bot.send_message(chat_id=tg_id, text=text)
                for path in file_paths:
                    if os.path.exists(path):
                        await self._bot.send_document(chat_id=tg_id, document=FSInputFile(path))
                sent_count += 1
            except TelegramForbiddenError:
                print(f"Не удалось отправить пользователю {tg_id}: бот заблокирован")
            except TelegramBadRequest as exc:
                print(f"Не удалось отправить пользователю {tg_id}: {exc}")
            except Exception as exc:
                print(f"Не удалось отправить пользователю {tg_id}: {exc}")
        return sent_count

    def send_generation_results(self, class_name: str, folder_path: str):
        valid_files = []
        invalid_files = []

        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return 0, [], []

        for file_path in folder.iterdir():
            if not file_path.is_file() or file_path.suffix.lower() != ".txt":
                invalid_files.append(file_path.name)
                continue

            # Telegram не принимает пустые файлы
            try:
                if file_path.stat().st_size <= 0:
                    invalid_files.append(file_path.name)
                    continue
            except OSError:
                invalid_files.append(file_path.name)
                continue

            parts = file_path.stem.split("_")
            if len(parts) != 2:
                invalid_files.append(file_path.name)
                continue

            part1 = self._normalize_name(parts[0])
            part2 = self._normalize_name(parts[1])
            valid_files.append((file_path, part1, part2))

        if not valid_files:
            return 0, [], invalid_files

        db_name_to_tg = self._get_students_tg_by_name(class_name)
        to_send = []

        for file_path, first, second in valid_files:
            tg_id = db_name_to_tg.get((first, second))
            if not tg_id:
                tg_id = db_name_to_tg.get((second, first))

            if tg_id:
                to_send.append((tg_id, str(file_path)))
            else:
                invalid_files.append(file_path.name)

        if not to_send:
            return 0, [], invalid_files

        future = asyncio.run_coroutine_threadsafe(
            self._send_results_files(to_send),
            self._loop,
        )
        sent_count, failed_files = future.result(timeout=120)
        sent_names = [Path(path).name for _, path in to_send if Path(path).name not in failed_files]
        invalid_files.extend(failed_files)
        return sent_count, sent_names, invalid_files

    async def _send_results_files(self, targets):
        sent_count = 0
        failed_files = []

        for tg_id, file_path in targets:
            try:
                await self._bot.send_document(chat_id=tg_id, document=FSInputFile(file_path))
                sent_count += 1
            except TelegramForbiddenError as exc:
                print(f"Не удалось отправить файл {file_path}: {exc}")
                failed_files.append(Path(file_path).name)
            except TelegramBadRequest as exc:
                # Частый случай: "file must be non-empty"
                print(f"Не удалось отправить файл {file_path}: {exc}")
                failed_files.append(Path(file_path).name)
            except Exception as exc:
                print(f"Не удалось отправить файл {file_path}: {exc}")
                failed_files.append(Path(file_path).name)

        return sent_count, failed_files

    def _connect_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_telegram_ids_by_class(self, class_name):
        conn = self._connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT s.telegram_id
                FROM students s
                JOIN classes c ON c.id = s.class_id
                WHERE c.class_name = ?
                  AND s.telegram_id IS NOT NULL
                """,
                (class_name,),
            )
            rows = cursor.fetchall()

            unique_ids = []
            seen = set()
            for row in rows:
                tg_id = row["telegram_id"]
                if tg_id is None:
                    continue
                tg_id = int(tg_id)
                if tg_id in seen:
                    continue
                seen.add(tg_id)
                unique_ids.append(tg_id)
            return unique_ids
        finally:
            conn.close()

    def _get_students_tg_by_name(self, class_name):
        conn = self._connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT TRIM(surname) AS surname,
                       TRIM(name) AS name,
                       telegram_id
                FROM students s
                JOIN classes c ON c.id = s.class_id
                WHERE c.class_name = ?
                  AND s.telegram_id IS NOT NULL
                """,
                (class_name,),
            )
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                if not row["telegram_id"]:
                    continue

                surname = self._normalize_name(row["surname"])
                name = self._normalize_name(row["name"])
                tg_id = int(row["telegram_id"])

                # Сопоставляем оба варианта: имя/фамилия и фамилия/имя
                result[(surname, name)] = tg_id
                result[(name, surname)] = tg_id

            return result
        finally:
            conn.close()

    def _is_registered_in_class(self, class_name, tg_id):
        conn = self._connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1
                FROM students s
                JOIN classes c ON c.id = s.class_id
                WHERE c.class_name = ? AND s.telegram_id = ?
                LIMIT 1
                """,
                (class_name, tg_id),
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def _get_full_name_by_tg_id(self, class_name, tg_id):
        conn = self._connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name, surname
                FROM students s
                JOIN classes c ON c.id = s.class_id
                WHERE c.class_name = ? AND s.telegram_id = ?
                LIMIT 1
                """,
                (class_name, tg_id),
            )
            row = cursor.fetchone()
            if not row:
                return "Неизвестный ученик"
            return f"{row['name']} {row['surname']}"
        finally:
            conn.close()

    def _upsert_student_telegram(self, class_name, name, surname, telegram_id):
        conn = self._connect_db()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM classes WHERE class_name = ?", (class_name,))
            class_row = cursor.fetchone()
            if not class_row:
                cursor.execute("INSERT INTO classes (class_name) VALUES (?)", (class_name,))
                class_id = cursor.lastrowid
            else:
                class_id = class_row["id"]

            cursor.execute(
                """
                SELECT id
                FROM students
                WHERE class_id = ?
                  AND (
                      (LOWER(REPLACE(TRIM(name), 'ё', 'е')) = LOWER(REPLACE(TRIM(?), 'ё', 'е'))
                       AND LOWER(REPLACE(TRIM(surname), 'ё', 'е')) = LOWER(REPLACE(TRIM(?), 'ё', 'е')))
                      OR
                      (LOWER(REPLACE(TRIM(name), 'ё', 'е')) = LOWER(REPLACE(TRIM(?), 'ё', 'е'))
                       AND LOWER(REPLACE(TRIM(surname), 'ё', 'е')) = LOWER(REPLACE(TRIM(?), 'ё', 'е')))
                  )
                LIMIT 1
                """,
                (class_id, name, surname, surname, name),
            )
            student_row = cursor.fetchone()

            if student_row:
                cursor.execute(
                    "UPDATE students SET telegram_id = ? WHERE id = ?",
                    (telegram_id, student_row["id"]),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO students (class_id, name, surname, telegram_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (class_id, name, surname, telegram_id),
                )

            conn.commit()
        finally:
            conn.close()
