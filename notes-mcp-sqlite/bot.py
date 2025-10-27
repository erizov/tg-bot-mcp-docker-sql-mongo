#!/usr/bin/env python3
"""
Телеграм-бот для заметок и напоминаний с использованием SQLite.
"""

import os
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Настройка логирования
def setup_logging() -> logging.Logger:
    """Настраивает систему логирования."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Основной логгер
    logger = logging.getLogger("notes_bot")
    logger.setLevel(logging.INFO)

    # Обработчик для файла
    file_handler = logging.FileHandler(
        log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Инициализация логирования
logger = setup_logging()

# Конфигурация
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DB_PATH: str = "notes.db"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class NotesDatabase:
    """Класс для работы с базой данных заметок."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Инициализация базы данных."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                due_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def add_note(self, title: str, content: str, due_at: Optional[str] = None) -> int:
        """Добавляет новую заметку."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO notes (title, content, due_at)
            VALUES (?, ?, ?)
        """, (title, content, due_at))

        note_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Note added: ID={note_id}, Title='{title}', Due={due_at}")
        return note_id

    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку по ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Проверяем, существует ли заметка
        cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            conn.close()
            logger.warning(f"Attempt to delete non-existent note: ID={note_id}")
            return False

        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted_count > 0:
            logger.info(f"Note deleted: ID={note_id}")
            return True
        return False

    def search_notes(self, query: str, limit: int = 10) -> List[Tuple]:
        """Ищет заметки по содержимому."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT id, title, content, due_at, created_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_pattern, search_pattern, limit))

        results = cursor.fetchall()
        conn.close()

        logger.info(f"Search performed: query='{query}', results={len(results)}")
        return results

    def get_note_by_id(self, note_id: int) -> Optional[Tuple]:
        """Получает заметку по ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, content, due_at, created_at
            FROM notes
            WHERE id = ?
        """, (note_id,))

        result = cursor.fetchone()
        conn.close()

        return result

    def get_recent_notes(self, limit: int = 5) -> List[Tuple]:
        """Получает последние заметки."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, content, due_at, created_at
            FROM notes
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        notes = cursor.fetchall()
        conn.close()

        return notes

    def get_upcoming_reminders(self, hours: int = 24) -> List[Tuple]:
        """Получает напоминания на ближайшие часы."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now()
        future_time = now + timedelta(hours=hours)

        cursor.execute("""
            SELECT id, title, content, due_at, created_at
            FROM notes
            WHERE due_at IS NOT NULL
            AND due_at BETWEEN ? AND ?
            ORDER BY due_at ASC
        """, (now.strftime("%Y-%m-%d %H:%M:%S"), 
              future_time.strftime("%Y-%m-%d %H:%M:%S")))

        reminders = cursor.fetchall()
        conn.close()

        return reminders

    def get_stats(self) -> dict:
        """Получает статистику по заметкам."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Общее количество заметок
        cursor.execute("SELECT COUNT(*) FROM notes")
        total_notes = cursor.fetchone()[0]

        # Заметки с напоминаниями
        cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NOT NULL")
        notes_with_reminders = cursor.fetchone()[0]

        # Заметки без напоминаний
        cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NULL")
        notes_without_reminders = cursor.fetchone()[0]

        # Заметки за последние 7 дней
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT COUNT(*) FROM notes WHERE created_at >= ?", (week_ago,))
        recent_notes = cursor.fetchone()[0]

        conn.close()

        return {
            "total_notes": total_notes,
            "notes_with_reminders": notes_with_reminders,
            "notes_without_reminders": notes_without_reminders,
            "recent_notes": recent_notes
        }


# Инициализация базы данных
db = NotesDatabase(DB_PATH)


def log_user_action(user_id: int, username: str, action: str, details: str = "") -> None:
    """Логирует действия пользователя."""
    logger.info(f"User action: user_id={user_id}, username=@{username}, action={action}, details={details}")


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start."""
    log_user_action(message.from_user.id, message.from_user.username or "unknown", "start")

    await message.answer(
        "Привет! Я бот для заметок и напоминаний.\n\n"
        "Доступные команды:\n"
        "/add <текст> - создать заметку\n"
        "/remind <YYYY-MM-DD HH:MM> <текст> - заметка с напоминанием\n"
        "/list - показать 5 последних заметок\n"
        "/search <запрос> - поиск по содержимому\n"
        "/delete <ID> - удалить заметку\n"
        "/stats - показать статистику\n"
        "/help - показать эту справку"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help."""
    log_user_action(message.from_user.id, message.from_user.username or "unknown", "help")
    await cmd_start(message)


@dp.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """Обработчик команды /stats."""
    log_user_action(message.from_user.id, message.from_user.username or "unknown", "stats")

    stats = db.get_stats()

    await message.answer(
        f"📊 Статистика заметок:\n\n"
        f"📝 Всего заметок: {stats['total_notes']}\n"
        f"⏰ С напоминаниями: {stats['notes_with_reminders']}\n"
        f"📄 Без напоминаний: {stats['notes_without_reminders']}\n"
        f"🆕 За последние 7 дней: {stats['recent_notes']}"
    )


@dp.message(Command("add"))
async def cmd_add(message: Message) -> None:
    """Обработчик команды /add."""
    text = message.text[5:].strip()  # Убираем "/add "

    if not text:
        await message.answer("Использование: /add <текст заметки>")
        return

    # Разделяем на заголовок и содержимое
    parts = text.split(" ", 1)
    if len(parts) == 1:
        title = "Заметка"
        content = parts[0]
    else:
        title = parts[0]
        content = parts[1]

    note_id = db.add_note(title, content)

    log_user_action(
        message.from_user.id, 
        message.from_user.username or "unknown", 
        "add_note", 
        f"ID={note_id}, Title='{title}'"
    )

    await message.answer(
        f"✅ Заметка добавлена!\n\n"
        f"ID: {note_id}\n"
        f"Заголовок: {title}\n"
        f"Содержимое: {content}"
    )


@dp.message(Command("remind"))
async def cmd_remind(message: Message) -> None:
    """Обработчик команды /remind."""
    text = message.text[8:].strip()  # Убираем "/remind "

    if not text:
        await message.answer(
            "Использование: /remind <YYYY-MM-DD HH:MM> <текст>"
        )
        return

    # Парсим дату и время
    parts = text.split(" ", 2)
    if len(parts) < 3:
        await message.answer(
            "Использование: /remind <YYYY-MM-DD HH:MM> <текст>"
        )
        return

    try:
        due_at_str = f"{parts[0]} {parts[1]}"
        due_at = datetime.strptime(due_at_str, "%Y-%m-%d %H:%M")

        # Проверяем, что дата в будущем
        if due_at <= datetime.now():
            await message.answer("Дата напоминания должна быть в будущем!")
            return

        content = parts[2]

        # Разделяем на заголовок и содержимое
        content_parts = content.split(" ", 1)
        if len(content_parts) == 1:
            title = "Напоминание"
            note_content = content_parts[0]
        else:
            title = content_parts[0]
            note_content = content_parts[1]

        note_id = db.add_note(title, note_content, due_at_str)

        log_user_action(
            message.from_user.id, 
            message.from_user.username or "unknown", 
            "add_reminder", 
            f"ID={note_id}, Title='{title}', Due={due_at_str}"
        )

        await message.answer(
            f"⏰ Напоминание добавлено!\n\n"
            f"ID: {note_id}\n"
            f"Заголовок: {title}\n"
            f"Содержимое: {note_content}\n"
            f"Напоминание: {due_at_str}"
        )

    except ValueError:
        await message.answer(
            "Неверный формат даты! Используйте: YYYY-MM-DD HH:MM"
        )


@dp.message(Command("search"))
async def cmd_search(message: Message) -> None:
    """Обработчик команды /search."""
    query = message.text[8:].strip()  # Убираем "/search "

    if not query:
        await message.answer("Использование: /search <запрос>")
        return

    log_user_action(
        message.from_user.id, 
        message.from_user.username or "unknown", 
        "search", 
        f"query='{query}'"
    )

    results = db.search_notes(query, 10)

    if not results:
        await message.answer(f"🔍 По запросу '{query}' ничего не найдено.")
        return

    response = f"🔍 Результаты поиска по запросу '{query}':\n\n"

    for note in results:
        note_id, title, content, due_at, created_at = note

        response += f"ID: {note_id}\n"
        response += f"📌 {title}\n"
        response += f"📄 {content}\n"

        if due_at:
            response += f"⏰ Напоминание: {due_at}\n"

        response += f"📅 Создано: {created_at}\n"
        response += "─" * 20 + "\n"

    # Разбиваем длинные сообщения
    if len(response) > 4000:
        response = response[:4000] + "\n... (результаты обрезаны)"

    await message.answer(response)


@dp.message(Command("delete"))
async def cmd_delete(message: Message) -> None:
    """Обработчик команды /delete."""
    text = message.text[8:].strip()  # Убираем "/delete "

    if not text:
        await message.answer("Использование: /delete <ID заметки>")
        return

    try:
        note_id = int(text)
    except ValueError:
        await message.answer("ID должен быть числом!")
        return

    # Получаем информацию о заметке перед удалением
    note = db.get_note_by_id(note_id)
    if not note:
        await message.answer(f"❌ Заметка с ID {note_id} не найдена.")
        return

    # Удаляем заметку
    success = db.delete_note(note_id)

    if success:
        log_user_action(
            message.from_user.id, 
            message.from_user.username or "unknown", 
            "delete_note", 
            f"ID={note_id}, Title='{note[1]}'"
        )

        await message.answer(
            f"🗑️ Заметка удалена!\n\n"
            f"ID: {note_id}\n"
            f"Заголовок: {note[1]}\n"
            f"Содержимое: {note[2]}"
        )
    else:
        await message.answer(f"❌ Ошибка при удалении заметки с ID {note_id}.")


@dp.message(Command("list"))
async def cmd_list(message: Message) -> None:
    """Обработчик команды /list."""
    log_user_action(message.from_user.id, message.from_user.username or "unknown", "list")

    notes = db.get_recent_notes(5)

    if not notes:
        await message.answer("Заметок пока нет.")
        return

    response = "📝 Последние 5 заметок:\n\n"

    for note in notes:
        note_id, title, content, due_at, created_at = note

        response += f"ID: {note_id}\n"
        response += f"📌 {title}\n"
        response += f"📄 {content}\n"

        if due_at:
            response += f"⏰ Напоминание: {due_at}\n"

        response += f"📅 Создано: {created_at}\n"
        response += "─" * 20 + "\n"

    await message.answer(response)


async def main() -> None:
    """Основная функция запуска бота."""
    logger.info("Starting bot...")

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Please set BOT_TOKEN environment variable!")
        return

    logger.info("Bot started successfully")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
