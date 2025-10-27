# Инструкция по запуску бота

## ✅ Проблема решена!

Бот успешно запускается, но нужно настроить токен Telegram.

## 🔧 Как исправить:

### 1. Создайте бота в Telegram
1. Откройте Telegram
2. Найдите бота [@BotFather](https://t.me/BotFather)
3. Отправьте команду `/newbot`
4. Следуйте инструкциям для создания бота
5. Скопируйте полученный токен

### 2. Установите токен
Выберите один из способов:

#### Способ 1: Переменная окружения (рекомендуется)
```bash
# Windows PowerShell
$env:BOT_TOKEN="YOUR_BOT_TOKEN_HERE"

# Windows CMD
set BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Linux/macOS
export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

#### Способ 2: Создать файл .env
Создайте файл `.env` в папке `notes-mcp-sqlite/`:
```
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
```

### 3. Запустите бота
```bash
cd notes-mcp-sqlite
python bot.py
```

## 📋 Пример токена
Токен выглядит примерно так:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
```

## ✅ Проверка работы
После установки токена бот должен запуститься и показать:
```
2025-10-26 16:45:00 - notes_bot - INFO - Starting bot...
2025-10-26 16:45:00 - notes_bot - INFO - Bot started successfully
```

## 🚀 Тестирование
1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Попробуйте команды:
   - `/add Тестовая заметка`
   - `/list`
   - `/stats`

## 📝 Логи
После работы бота логи будут созданы в папке `logs/` и можно будет запустить мониторинг:
```bash
python monitor.py
```
