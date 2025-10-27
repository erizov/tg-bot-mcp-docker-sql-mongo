#!/usr/bin/env python3
"""
Скрипт для создания базы данных SQLite с таблицей notes и тестовыми данными.
"""

import sqlite3
import datetime
from pathlib import Path


def create_database():
    """Создает базу данных и таблицу notes с тестовыми данными."""
    db_path = Path("notes.db")

    # Удаляем существующую БД если есть
    if db_path.exists():
        db_path.unlink()

    # Создаем новую БД
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаем таблицу notes
    cursor.execute("""
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            due_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Добавляем тестовые данные
    test_notes = [
        ("Важная встреча", "Встреча с клиентом в 15:00", "2024-01-15 15:00:00"),
        ("Купить продукты", "Молоко, хлеб, яйца", None),
        ("Позвонить маме", "Позвонить маме на выходных", "2024-01-14 18:00:00"),
        ("Подготовить презентацию", "Слайды для проекта X", "2024-01-16 10:00:00"),
        ("Записаться к врачу", "Проверить здоровье", None),
        ("Важно: оплатить счета", "Коммунальные услуги до 20 числа", "2024-01-20 23:59:00"),
        ("Изучить новый фреймворк", "React для фронтенда", None),
        ("Важно: дедлайн проекта", "Сдать проект до конца месяца", "2024-01-31 23:59:00"),
        ("Встреча с командой", "Еженедельный стендап", "2024-01-17 09:00:00"),
        ("Купить подарок", "День рождения друга", "2024-01-18 12:00:00"),
    ]

    for title, content, due_at in test_notes:
        cursor.execute("""
            INSERT INTO notes (title, content, due_at)
            VALUES (?, ?, ?)
        """, (title, content, due_at))

    conn.commit()
    conn.close()

    print(f"Database created: {db_path.absolute()}")
    print(f"Added {len(test_notes)} test records")


if __name__ == "__main__":
    create_database()
