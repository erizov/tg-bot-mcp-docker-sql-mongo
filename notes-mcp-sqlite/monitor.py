#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для мониторинга и анализа логов телеграм-бота.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import re


class BotMonitor:
    """Класс для мониторинга и анализа работы бота."""
    
    def __init__(self, db_path: str = "notes.db", logs_dir: str = "logs"):
        self.db_path = db_path
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
    
    def get_database_stats(self) -> dict:
        """Получает статистику базы данных."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Общая статистика
        cursor.execute("SELECT COUNT(*) FROM notes")
        stats['total_notes'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NOT NULL")
        stats['notes_with_reminders'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notes WHERE due_at IS NULL")
        stats['notes_without_reminders'] = cursor.fetchone()[0]
        
        # Статистика по дням
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM notes
            WHERE created_at >= date('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        stats['daily_stats'] = dict(cursor.fetchall())
        
        # Топ заголовков
        cursor.execute("""
            SELECT title, COUNT(*) as count
            FROM notes
            GROUP BY title
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_titles'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def analyze_logs(self) -> dict:
        """Анализирует логи бота."""
        log_files = list(self.logs_dir.glob("bot_*.log"))
        
        if not log_files:
            return {
                "error": "No log files found",
                "message": "Бот еще не запускался или логи не создавались",
                "suggestion": "Запустите бота командой 'python bot.py' для создания логов"
            }
        
        # Берем последний лог файл
        latest_log = max(log_files, key=os.path.getmtime)
        
        analysis = {
            "log_file": str(latest_log),
            "file_size": os.path.getsize(latest_log),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(latest_log)),
            "total_lines": 0,
            "user_actions": defaultdict(int),
            "errors": [],
            "daily_activity": defaultdict(int),
            "unique_users": set()
        }
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            for line in f:
                analysis["total_lines"] += 1
                
                # Парсим строки логов
                if "User action:" in line:
                    # Извлекаем информацию о действиях пользователей
                    match = re.search(r'user_id=(\d+), username=@(\w+), action=(\w+)', line)
                    if match:
                        user_id, username, action = match.groups()
                        analysis["user_actions"][action] += 1
                        analysis["unique_users"].add(f"{username}({user_id})")
                
                if "ERROR" in line:
                    analysis["errors"].append(line.strip())
                
                # Анализ активности по дням
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                if date_match:
                    date = date_match.group(1)
                    analysis["daily_activity"][date] += 1
        
        # Конвертируем set в list для JSON сериализации
        analysis["unique_users"] = list(analysis["unique_users"])
        analysis["unique_users_count"] = len(analysis["unique_users"])
        
        return analysis
    
    def generate_report(self) -> str:
        """Генерирует отчет о работе бота."""
        db_stats = self.get_database_stats()
        log_analysis = self.analyze_logs()
        
        report = []
        report.append("=" * 60)
        report.append("ОТЧЕТ О РАБОТЕ ТЕЛЕГРАМ-БОТА ЗАМЕТОК")
        report.append("=" * 60)
        report.append(f"Время генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Статистика базы данных
        report.append("📊 СТАТИСТИКА БАЗЫ ДАННЫХ:")
        report.append(f"  📝 Всего заметок: {db_stats['total_notes']}")
        report.append(f"  ⏰ С напоминаниями: {db_stats['notes_with_reminders']}")
        report.append(f"  📄 Без напоминаний: {db_stats['notes_without_reminders']}")
        report.append("")
        
        # Статистика активности за последние дни
        if db_stats['daily_stats']:
            report.append("📅 АКТИВНОСТЬ ПО ДНЯМ (последние 7 дней):")
            for date, count in list(db_stats['daily_stats'].items())[:7]:
                report.append(f"  {date}: {count} заметок")
            report.append("")
        
        # Топ заголовков
        if db_stats['top_titles']:
            report.append("🏆 ТОП ЗАГОЛОВКОВ:")
            for title, count in list(db_stats['top_titles'].items())[:5]:
                report.append(f"  '{title}': {count} раз")
            report.append("")
        
        # Анализ логов
        if "error" in log_analysis:
            report.append("📋 АНАЛИЗ ЛОГОВ:")
            report.append(f"  ⚠️  {log_analysis['message']}")
            report.append(f"  💡 {log_analysis['suggestion']}")
            report.append("")
        else:
            report.append("📋 АНАЛИЗ ЛОГОВ:")
            report.append(f"  📁 Файл лога: {log_analysis['log_file']}")
            report.append(f"  📏 Размер файла: {log_analysis['file_size']} байт")
            report.append(f"  📝 Всего строк: {log_analysis['total_lines']}")
            report.append(f"  👥 Уникальных пользователей: {log_analysis['unique_users_count']}")
            report.append("")
            
            # Статистика действий
            if log_analysis['user_actions']:
                report.append("🎯 СТАТИСТИКА ДЕЙСТВИЙ:")
                for action, count in log_analysis['user_actions'].items():
                    report.append(f"  {action}: {count} раз")
                report.append("")
            
            # Ошибки
            if log_analysis['errors']:
                report.append("❌ ОШИБКИ:")
                for error in log_analysis['errors'][-5:]:  # Последние 5 ошибок
                    report.append(f"  {error}")
                report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None) -> str:
        """Сохраняет отчет в файл."""
        if filename is None:
            filename = f"bot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_report()
        
        report_path = self.logs_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(report_path)
    
    def get_health_status(self) -> dict:
        """Получает статус здоровья системы."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "database": "healthy",
            "logs": "healthy",
            "issues": []
        }
        
        # Проверка базы данных
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM notes")
            conn.close()
        except Exception as e:
            status["database"] = "error"
            status["issues"].append(f"Database error: {str(e)}")
        
        # Проверка логов
        log_files = list(self.logs_dir.glob("bot_*.log"))
        if not log_files:
            status["logs"] = "warning"
            status["issues"].append("No log files found")
        
        return status


def main():
    """Основная функция для запуска мониторинга."""
    # Настраиваем кодировку для Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    
    monitor = BotMonitor()
    
    print("Анализ работы телеграм-бота...")
    print()
    
    # Генерируем и выводим отчет
    report = monitor.generate_report()
    print(report)
    
    # Сохраняем отчет
    report_path = monitor.save_report()
    print(f"\nОтчет сохранен: {report_path}")
    
    # Проверяем статус системы
    health = monitor.get_health_status()
    print(f"\nСтатус системы: {health['database']} (DB), {health['logs']} (Logs)")
    
    if health['issues']:
        print("Обнаруженные проблемы:")
        for issue in health['issues']:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()
