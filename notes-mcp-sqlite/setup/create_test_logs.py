#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания тестовых логов бота.
Имитирует работу бота и создает логи для демонстрации мониторинга.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def setup_encoding():
    """Настраивает кодировку для Windows."""
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def create_test_logs():
    """Создает тестовые логи для демонстрации мониторинга."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Создаем лог файл с сегодняшней датой
    today = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"bot_{today}.log"
    
    # Тестовые данные логов
    test_logs = [
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Database initialized successfully",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Starting bot...",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Bot started successfully",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=12345, username=@testuser, action=start, details=",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=12345, username=@testuser, action=add_note, details=ID=11, Title='Тестовая заметка'",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Note added: ID=11, Title='Тестовая заметка', Due=None",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=12345, username=@testuser, action=search, details=query='важно'",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Search performed: query='важно', results=2",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=12345, username=@testuser, action=list, details=",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=67890, username=@anotheruser, action=start, details=",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=67890, username=@anotheruser, action=stats, details=",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=12345, username=@testuser, action=delete_note, details=ID=5, Title='Купить продукты'",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Note deleted: ID=5",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - WARNING - Attempt to delete non-existent note: ID=999",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - ERROR - Database connection failed: database is locked",
    ]
    
    # Записываем тестовые логи
    with open(log_file, 'w', encoding='utf-8') as f:
        for log_entry in test_logs:
            f.write(log_entry + '\n')
    
    print(f"✅ Создан тестовый лог-файл: {log_file}")
    print(f"📝 Добавлено {len(test_logs)} записей")
    
    # Создаем дополнительный лог файл за вчера
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    yesterday_log = logs_dir / f"bot_{yesterday}.log"
    
    yesterday_logs = [
        f"{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Database initialized successfully",
        f"{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=11111, username=@yesterdayuser, action=start, details=",
        f"{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - User action: user_id=11111, username=@yesterdayuser, action=add_note, details=ID=12, Title='Вчерашняя заметка'",
        f"{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')} - notes_bot - INFO - Note added: ID=12, Title='Вчерашняя заметка', Due=None",
    ]
    
    with open(yesterday_log, 'w', encoding='utf-8') as f:
        for log_entry in yesterday_logs:
            f.write(log_entry + '\n')
    
    print(f"✅ Создан дополнительный лог-файл: {yesterday_log}")
    print(f"📝 Добавлено {len(yesterday_logs)} записей")
    
    return log_file, yesterday_log


def main():
    """Основная функция."""
    setup_encoding()
    
    print("🔧 Создание тестовых логов для демонстрации мониторинга...")
    print()
    
    try:
        log_files = create_test_logs()
        
        print()
        print("📊 Статистика созданных логов:")
        for log_file in log_files:
            if log_file.exists():
                size = log_file.stat().st_size
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                print(f"  📁 {log_file.name}: {lines} строк, {size} байт")
        
        print()
        print("✅ Тестовые логи созданы успешно!")
        print("💡 Теперь можно запустить 'python monitor.py' для анализа логов")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых логов: {e}")


if __name__ == "__main__":
    main()
