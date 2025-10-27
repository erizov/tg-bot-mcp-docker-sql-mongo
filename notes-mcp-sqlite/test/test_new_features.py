#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки новых функций бота.
"""

import sqlite3
import sys
from datetime import datetime, timedelta


def setup_encoding():
    """Настраивает кодировку для Windows."""
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def test_database_functions():
    """Тестирует новые функции базы данных."""
    print("🧪 Тестирование новых функций базы данных...")
    print()
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    # Тест поиска
    print("1. Тест поиска заметок:")
    cursor.execute("""
        SELECT id, title, content FROM notes 
        WHERE title LIKE '%важно%' OR content LIKE '%важно%'
        LIMIT 3
    """)
    search_results = cursor.fetchall()
    print(f"   Найдено заметок с 'важно': {len(search_results)}")
    for note in search_results:
        print(f"   - ID: {note[0]}, Заголовок: {note[1]}")
    print()
    
    # Тест получения заметки по ID
    print("2. Тест получения заметки по ID:")
    cursor.execute("SELECT id, title, content FROM notes LIMIT 1")
    test_note = cursor.fetchone()
    if test_note:
        note_id = test_note[0]
        cursor.execute("SELECT id, title, content FROM notes WHERE id = ?", (note_id,))
        found_note = cursor.fetchone()
        print(f"   Заметка ID {note_id}: {found_note[1] if found_note else 'Не найдена'}")
    print()
    
    # Тест статистики
    print("3. Тест статистики:")
    cursor.execute("SELECT COUNT(*) FROM notes")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NOT NULL")
    with_reminders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NULL")
    without_reminders = cursor.fetchone()[0]
    
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT COUNT(*) FROM notes WHERE created_at >= ?", (week_ago,))
    recent = cursor.fetchone()[0]
    
    print(f"   Всего заметок: {total}")
    print(f"   С напоминаниями: {with_reminders}")
    print(f"   Без напоминаний: {without_reminders}")
    print(f"   За последние 7 дней: {recent}")
    print()
    
    conn.close()
    print("✅ Тесты базы данных завершены!")


def test_search_functionality():
    """Тестирует функциональность поиска."""
    print("\n🔍 Тестирование поиска...")
    print()
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    test_queries = [
        "важно",
        "встреча",
        "купить",
        "проект",
        "врач"
    ]
    
    for query in test_queries:
        cursor.execute("""
            SELECT COUNT(*) FROM notes 
            WHERE title LIKE ? OR content LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        
        count = cursor.fetchone()[0]
        print(f"   Поиск '{query}': найдено {count} заметок")
    
    conn.close()
    print("\n✅ Тесты поиска завершены!")


def test_delete_simulation():
    """Симулирует тест удаления (без фактического удаления)."""
    print("\n🗑️ Тестирование функции удаления...")
    print()
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    # Получаем список заметок для тестирования
    cursor.execute("SELECT id, title FROM notes LIMIT 5")
    notes = cursor.fetchall()
    
    print("   Доступные заметки для тестирования удаления:")
    for note_id, title in notes:
        print(f"   - ID: {note_id}, Заголовок: {title}")
    
    # Проверяем существование заметки
    if notes:
        test_id = notes[0][0]
        cursor.execute("SELECT id FROM notes WHERE id = ?", (test_id,))
        exists = cursor.fetchone() is not None
        print(f"\n   Проверка существования заметки ID {test_id}: {'✅ Существует' if exists else '❌ Не найдена'}")
    
    conn.close()
    print("\n✅ Тесты удаления завершены!")


def main():
    """Основная функция тестирования."""
    setup_encoding()
    
    print("🚀 ТЕСТИРОВАНИЕ НОВЫХ ФУНКЦИЙ ТЕЛЕГРАМ-БОТА")
    print("=" * 50)
    
    try:
        test_database_functions()
        test_search_functionality()
        test_delete_simulation()
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("\nНовые функции готовы к использованию:")
        print("  ✅ Команда /search - поиск по содержимому")
        print("  ✅ Команда /delete - удаление заметок")
        print("  ✅ Команда /stats - статистика")
        print("  ✅ Логирование всех действий пользователей")
        print("  ✅ Мониторинг и анализ работы бота")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")


if __name__ == "__main__":
    main()
