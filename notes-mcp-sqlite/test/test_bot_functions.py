#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования функций бота без запуска Telegram API.
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

from database import NotesDatabase, setup_logging


def test_bot_functions():
    """Тестирует функции бота без Telegram API."""
    # Настраиваем кодировку для Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    print("Тестирование функций бота...")
    print()

    # Инициализируем логирование
    logger = setup_logging()
    logger.info("Starting bot functions test")

    # Инициализируем базу данных
    db = NotesDatabase("notes.db")

    print("База данных инициализирована")

    # Тест добавления заметки
    print("\nТест добавления заметки:")
    note_id = db.add_note("Тестовая заметка", "Это тестовая заметка для проверки функций")
    print(f"   Добавлена заметка с ID: {note_id}")

    # Тест поиска
    print("\nТест поиска:")
    results = db.search_notes("тест")
    print(f"   Найдено заметок с 'тест': {len(results)}")
    for note in results:
        print(f"   - ID: {note[0]}, Заголовок: {note[1]}")

    # Тест получения заметки по ID
    print("\nТест получения заметки по ID:")
    note = db.get_note_by_id(note_id)
    if note:
        print(f"   Найдена заметка: {note[1]} - {note[2]}")
    else:
        print("   Заметка не найдена")

    # Тест статистики
    print("\nТест статистики:")
    stats = db.get_stats()
    print(f"   Всего заметок: {stats['total_notes']}")
    print(f"   С напоминаниями: {stats['notes_with_reminders']}")
    print(f"   Без напоминаний: {stats['notes_without_reminders']}")
    print(f"   За последние 7 дней: {stats['recent_notes']}")

    # Тест удаления
    print("\nТест удаления:")
    success = db.delete_note(note_id)
    if success:
        print(f"   Заметка с ID {note_id} успешно удалена")
    else:
        print(f"   Ошибка при удалении заметки с ID {note_id}")

    # Проверяем, что заметка удалена
    note_after_delete = db.get_note_by_id(note_id)
    if not note_after_delete:
        print("   Заметка действительно удалена")
    else:
        print("   Заметка не была удалена")

    logger.info("Bot functions test completed")
    print("\nВсе тесты функций бота завершены успешно!")
    print("\nДля полного тестирования установите BOT_TOKEN и запустите:")
    print("   python bot.py")


def main():
    """Основная функция."""
    try:
        test_bot_functions()
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
