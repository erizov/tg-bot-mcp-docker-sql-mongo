#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт для работы с базой данных заметок.
Показывает примеры запросов, которые можно выполнять через MCP.
"""

import sqlite3
import sys
from datetime import datetime, timedelta


def setup_encoding():
    """Настраивает кодировку для Windows."""
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def execute_query(query, description):
    """Выполняет SQL запрос и выводит результат."""
    print(f"\n{'='*50}")
    print(f"Query: {description}")
    print(f"SQL: {query}")
    print(f"{'='*50}")
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            # Получаем названия колонок
            columns = [description[0] for description in cursor.description]
            print(f"Columns: {', '.join(columns)}")
            print(f"Results ({len(results)} rows):")
            
            for i, row in enumerate(results, 1):
                print(f"{i}. {dict(zip(columns, row))}")
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def main():
    """Основная функция демонстрации."""
    setup_encoding()
    
    print("SQLite Notes Database Demo")
    print("This demonstrates queries that can be run through MCP in Cursor")
    
    # 1. Показать все таблицы и их поля
    execute_query(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='notes'",
        "Show table structure"
    )
    
    # 2. Показать все заметки
    execute_query(
        "SELECT id, title, content, due_at, created_at FROM notes ORDER BY created_at DESC",
        "Show all notes (newest first)"
    )
    
    # 3. Заметки за последние 3 дня
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    execute_query(
        f"SELECT id, title, content, due_at, created_at FROM notes WHERE created_at >= '{three_days_ago}' ORDER BY created_at DESC",
        "Show notes from last 3 days"
    )
    
    # 4. Напоминания на ближайшие 24 часа
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tomorrow = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    execute_query(
        f"SELECT id, title, content, due_at FROM notes WHERE due_at IS NOT NULL AND due_at BETWEEN '{now}' AND '{tomorrow}' ORDER BY due_at ASC",
        "Show reminders for next 24 hours"
    )
    
    # 5. Поиск заметок с "важно" в заголовке
    execute_query(
        "SELECT id, title, content, due_at FROM notes WHERE title LIKE '%важно%' OR title LIKE '%Важно%'",
        "Find notes with 'важно' in title"
    )
    
    # 6. Статистика
    execute_query(
        "SELECT COUNT(*) as total_notes, COUNT(due_at) as notes_with_reminders FROM notes",
        "Show statistics"
    )
    
    # 7. Заметки без напоминаний
    execute_query(
        "SELECT id, title, content FROM notes WHERE due_at IS NULL ORDER BY created_at DESC",
        "Show notes without reminders"
    )
    
    print(f"\n{'='*50}")
    print("Demo completed! These queries can be run through MCP in Cursor")
    print("using natural language commands.")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
