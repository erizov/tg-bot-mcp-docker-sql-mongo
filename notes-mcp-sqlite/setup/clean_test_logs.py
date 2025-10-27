#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки тестовых логов.
"""

import os
import sys
from pathlib import Path


def setup_encoding():
    """Настраивает кодировку для Windows."""
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def clean_test_logs():
    """Удаляет тестовые лог-файлы."""
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print("📁 Папка logs не существует")
        return
    
    # Находим все лог-файлы
    log_files = list(logs_dir.glob("bot_*.log"))
    report_files = list(logs_dir.glob("bot_report_*.txt"))
    
    deleted_count = 0
    
    # Удаляем лог-файлы
    for log_file in log_files:
        try:
            log_file.unlink()
            print(f"🗑️  Удален: {log_file.name}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Ошибка при удалении {log_file.name}: {e}")
    
    # Удаляем отчеты
    for report_file in report_files:
        try:
            report_file.unlink()
            print(f"🗑️  Удален: {report_file.name}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Ошибка при удалении {report_file.name}: {e}")
    
    print(f"\n✅ Удалено файлов: {deleted_count}")
    
    # Проверяем, остались ли файлы
    remaining_files = list(logs_dir.glob("*"))
    if remaining_files:
        print(f"📁 Осталось файлов в logs/: {len(remaining_files)}")
        for file in remaining_files:
            print(f"  - {file.name}")
    else:
        print("📁 Папка logs пуста")


def main():
    """Основная функция."""
    setup_encoding()
    
    print("🧹 Очистка тестовых логов...")
    print()
    
    try:
        clean_test_logs()
        print("\n✅ Очистка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")


if __name__ == "__main__":
    main()
