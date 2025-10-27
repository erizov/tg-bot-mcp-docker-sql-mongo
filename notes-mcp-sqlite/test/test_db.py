#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки базы данных.
"""

import sqlite3
import sys


def test_database():
    """Тестирует базу данных и выводит информацию."""
    # Устанавливаем UTF-8 кодировку для вывода
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()

    # Подсчет записей
    cursor.execute('SELECT COUNT(*) FROM notes')
    total_notes = cursor.fetchone()[0]
    print(f"Total notes: {total_notes}")

    # Примеры записей
    cursor.execute('SELECT id, title, content, due_at FROM notes LIMIT 3')
    print("\nSample notes:")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Title: {row[1]}, Content: {row[2]}, Due: {row[3]}")

    # Заметки с напоминаниями
    cursor.execute('SELECT COUNT(*) FROM notes WHERE due_at IS NOT NULL')
    reminders_count = cursor.fetchone()[0]
    print(f"\nNotes with reminders: {reminders_count}")

    # Заметки без напоминаний
    cursor.execute('SELECT COUNT(*) FROM notes WHERE due_at IS NULL')
    notes_count = cursor.fetchone()[0]
    print(f"Notes without reminders: {notes_count}")

    conn.close()
    print("\nDatabase test completed successfully!")


if __name__ == "__main__":
    test_database()
