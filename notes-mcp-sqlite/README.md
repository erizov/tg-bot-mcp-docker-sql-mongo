[![Python](https://img.shields.io/badge/python-3.8+-blue?logo=python)](https://python.org) [![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://www.docker.com/) [![Tested DBs](https://img.shields.io/badge/DBs-SQLite--Progress--Mongo--Neo4j--PostgreSQL--ProgressServer-green?logo=mongodb)](#бэкенды-баз-данных)

# Телеграм-бот заметок + напоминаний (SQLite/Mongo/Neo4j/PostgreSQL/Progress)

**[🇷🇺 Русский README ниже]**

---

## 🚩 Features
- Telegram bot for notes & reminders
- Hot-swap DB: SQLite, MongoDB (Docker), Neo4j (Docker), PostgreSQL (Docker), In-memory (Progress), Progress Server
- Dockerized stack, easy Compose up
- Unit, integration, and load test coverage
- FastAPI REST DB monitoring (see `/count/html` dashboard)
- MCP Cursor integration ready
- Full logging/reporting, HTML perf reports

---

## ✅ Quick Preview
```bash
# Switch to MongoDB backend, launch containerized DB & run bot:
docker compose -f mongo.docker-compose.yml up -d
set USE_DB_BACKEND=mongo
python bot.py
```

---

# 🚀 Docker usage: полный стек и команды

- **Создать сеть для всех Compose-сервисов** (только 1 раз):
  ```bash
  docker network create neuroqc-net
  ```
- **Запустить MongoDB для бота и мониторинга**:
  ```bash
  docker compose -f mongo.docker-compose.yml up -d
  ```
- **Запустить монитор через FastAPI**
  ```bash
  uvicorn db.monitor_db:app --host 0.0.0.0 --port 8001
  # или в Docker: пример docker-compose api-сервиса
  ```
- **Просмотр статуса и логов**:
  ```bash
  docker ps           # Список контейнеров
  docker logs neuro-qc-mongo
  docker compose -f mongo.docker-compose.yml logs
  ```
- **Стоп и удаление контейнеров**:
  ```bash
  docker compose -f mongo.docker-compose.yml down
  docker volume rm tg-bot-mcp-docker-sql-mongo_mongodata  # очистить тестовые данные
  ```

- **Открыть веб-мониторинг**: [http://localhost:8001/count/html](http://localhost:8001/count/html) — Dashboard

- **Просмотр производительности:**
  - Открой `test/db_perf_report.html` в браузере (после python report_perf.py)

---

# 🐳 Специализированные Dockerfiles

В папке `dockerfiles/` находятся специализированные Dockerfiles для каждого backend:

- **`Dockerfile.sqlite`** - SQLite backend (по умолчанию)
- **`Dockerfile.mongo`** - MongoDB backend
- **`Dockerfile.neo4j`** - Neo4j backend
- **`Dockerfile.postgresql`** - PostgreSQL backend
- **`Dockerfile.progress`** - Progress (in-memory) backend
- **`Dockerfile.progress-server`** - Progress Server backend

### Примеры использования:

```bash
# SQLite (по умолчанию)
docker build -f dockerfiles/Dockerfile.sqlite -t tg-notes-bot:sqlite .

# MongoDB
docker compose -f mongo.docker-compose.yml up -d
docker build -f dockerfiles/Dockerfile.mongo -t tg-notes-bot:mongo .
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:mongo

# PostgreSQL
docker compose -f postgresql.docker-compose.yml up -d
docker build -f dockerfiles/Dockerfile.postgresql -t tg-notes-bot:postgresql .
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:postgresql
```

Подробная документация: [dockerfiles/README.md](../dockerfiles/README.md)

---

# 📦 Быстрое переключение backend и запрос
```python
import os
from db.database_selector import get_database_backend
os.environ["USE_DB_BACKEND"] = "mongo"  # sqlite, progress, or mongo

db = get_database_backend()
print(db.get_stats())
```

---

# Телеграм-бот заметок + напоминаний (SQLite + MCP)

Проект включает телеграм-бота для создания заметок и напоминаний с интеграцией SQLite через MCP (Model Context Protocol) для работы в Cursor.

## Структура проекта

```
notes-mcp-sqlite/
├── .cursor/
│   └── mcp.json          # Конфигурация MCP для Cursor
├── logs/                 # Папка с логами (создается автоматически)
├── notes.db              # База данных SQLite
├── bot.py                # Основной код телеграм-бота
├── create_db.py          # Скрипт создания БД с тестовыми данными
├── monitor.py            # Скрипт мониторинга и анализа
├── test_new_features.py  # Тестирование новых функций
├── create_test_logs.py   # Создание тестовых логов
├── clean_test_logs.py    # Очистка тестовых логов
├── requirements.txt      # Python зависимости
├── README.md            # Этот файл
├── MCP_SETUP.md         # Инструкции по настройке MCP
└── CHANGELOG.md         # Список изменений
```

## База данных

База данных `notes.db` содержит таблицу `notes` со следующими полями:

- `id` - уникальный идентификатор (INTEGER PRIMARY KEY)
- `title` - заголовок заметки (TEXT)
- `content` - содержимое заметки (TEXT)
- `due_at` - дата и время напоминания (DATETIME, может быть NULL)
- `created_at` - дата создания (DATETIME, по умолчанию CURRENT_TIMESTAMP)

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Создание базы данных

База данных уже создана с тестовыми данными. Если нужно пересоздать:

```bash
python create_db.py
```

### 3. Настройка бота

1. Создайте бота через [@BotFather](https://t.me/BotFather) в Telegram
2. Получите токен бота
3. Установите переменную окружения:

```bash
# Windows PowerShell
$env:BOT_TOKEN="YOUR_BOT_TOKEN_HERE"

# Windows CMD
set BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Linux/macOS
export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

### 4. Запуск бота

```bash
python bot.py
```

## Команды бота

- `/start` или `/help` - показать справку
- `/add <текст>` - создать заметку
- `/remind <YYYY-MM-DD HH:MM> <текст>` - создать заметку с напоминанием
- `/list` - показать 5 последних заметок
- `/search <запрос>` - поиск по содержимому заметок
- `/delete <ID>` - удалить заметку по ID
- `/stats` - показать статистику заметок

### Примеры использования

```
/add Купить молоко
/add Важная встреча Встреча с клиентом в 15:00
/remind 2024-01-15 15:00 Встреча с командой
/search важно
/search встреча
/delete 5
/stats
/list
```

## MCP интеграция с Cursor

### Настройка MCP

Конфигурация MCP уже настроена в файле `.cursor/mcp.json`. Путь к базе данных указан абсолютный:

```json
{
  "mcpServers": {
    "SQLite": {
      "command": "npx",
      "args": ["-y", "mcp-sqlite", "E:/Python/Cursor/3/neuro-bot-telegram-remainder-mcp/notes-mcp-sqlite/notes.db"]
    }
  }
}
```

### Активация MCP в Cursor

1. Откройте Cursor
2. Перейдите в настройки (Ctrl+,)
3. Найдите раздел "MCP"
4. Скопируйте содержимое `.cursor/mcp.json` в настройки MCP
5. Перезапустите Cursor

### Примеры запросов через MCP

После настройки MCP вы можете использовать естественный язык для работы с базой данных в Cursor Composer:

#### Просмотр структуры базы данных
```
Покажи все таблицы и их поля
```

#### Получение последних заметок
```
Выведи заметки за последние 3 дня (новые сверху)
```

#### Поиск напоминаний
```
Покажи напоминания на ближайшие 24 часа
```

#### Поиск по содержимому
```
Найди заметки, где в заголовке есть "важно"
```

#### Дополнительные примеры запросов
```
Покажи все заметки без напоминаний
Сколько всего заметок в базе?
Покажи заметки, созданные сегодня
Найди все напоминания на завтра
Покажи заметки с напоминаниями, отсортированные по дате
```

## Тестовые данные

В базе данных уже есть 10 тестовых записей, включая:
- Обычные заметки без напоминаний
- Заметки с напоминаниями на разные даты
- Заметки с ключевым словом "важно" в заголовке

## Технические детали

- **Фреймворк**: aiogram 3.4.1
- **База данных**: SQLite
- **MCP сервер**: mcp-sqlite
- **Язык**: Python 3.8+
- **Кодировка**: UTF-8

## Новые функции (v2.0)

### 🔍 Поиск по содержимому
Команда `/search` позволяет искать заметки по заголовку или содержимому:
- `/search важно` - найдет все заметки со словом "важно"
- `/search встреча` - найдет заметки о встречах
- Поиск работает по частичному совпадению (LIKE %query%)

### 🗑️ Удаление заметок
Команда `/delete` позволяет удалять заметки по ID:
- `/delete 5` - удалит заметку с ID 5
- Перед удалением показывается информация о заметке
- Удаление логируется для безопасности

### 📊 Статистика
Команда `/stats` показывает подробную статистику:
- Общее количество заметок
- Количество заметок с напоминаниями
- Количество заметок без напоминаний
- Количество заметок за последние 7 дней

### 📝 Логирование и мониторинг
- Все действия пользователей логируются в файлы `logs/bot_YYYYMMDD.log`
- Логи содержат информацию о пользователях, действиях и времени
- Скрипт `monitor.py` для анализа работы бота
- Скрипт `test_new_features.py` для тестирования функций

## Мониторинг и анализ

### Просмотр логов
```bash
# Запуск мониторинга
python monitor.py

# Тестирование новых функций
python test_new_features.py

# Создание тестовых логов для демонстрации
python create_test_logs.py

# Очистка тестовых логов
python clean_test_logs.py
```

### Структура логов
Логи сохраняются в папке `logs/` с именем `bot_YYYYMMDD.log` и содержат:
- Время действия
- ID и имя пользователя
- Тип действия (add_note, delete_note, search, etc.)
- Детали действия

## Возможные улучшения

- Реализовать систему категорий
- Интегрировать с календарем
- Добавить уведомления о приближающихся напоминаниях
- Реализовать экспорт/импорт заметок
- Добавить команду редактирования заметок
- Реализовать систему тегов

# --- БЭКЕНДЫ БАЗ ДАННЫХ ---

Проект поддерживает несколько вариантов backend для хранения заметок:

- **SQLite** (файл `notes.db`)
- **Progress (In-Memory)** — RAM only, не сохраняет данные между перезапусками
- **MongoDB** (поддерживается через docker, используется MCP и отдельные сервисы)
- **Neo4j** (графовая БД через docker, поддерживает связи между заметками)
- **PostgreSQL** (реляционная БД через docker, поддерживает полнотекстовый поиск)
- **Progress Server** (HTTP API сервер для внешних систем)

Переключение осуществляется переменной окружения:
```bash
set USE_DB_BACKEND=sqlite
set USE_DB_BACKEND=progress
set USE_DB_BACKEND=mongo
set USE_DB_BACKEND=neo4j
set USE_DB_BACKEND=postgresql
set USE_DB_BACKEND=progress_server
```

Для MongoDB требуется установленный и запущенный контейнер:
```bash
docker compose -f mongo.docker-compose.yml up -d
```

Для Neo4j требуется установленный и запущенный контейнер:
```bash
docker compose -f neo4j.docker-compose.yml up -d
```

Для PostgreSQL требуется установленный и запущенный контейнер:
```bash
docker compose -f postgresql.docker-compose.yml up -d
```

Для Progress Server требуется установленный и запущенный контейнер:
```bash
docker compose -f progress-server.docker-compose.yml up -d
```

---

# --- ТЕСТИРОВАНИЕ, ЛОГИРОВАНИЕ И ПЕРФОРМАНС ---

### 1. Запуск unit/integration/load тестов для всех БД:
В папке `test/`:
```bash
cd notes-mcp-sqlite/test
set PYTHONPATH=..
python test_db_backends.py
```

### 2. Запуск производительных тестов и генерация отчёта
```bash
python report_perf.py
```
После завершения откройте файл `test/db_perf_report.html` в браузере.

#### Пример таблицы отчёта:
| Backend         | Insert time (s, 500 rec) | Lookup time (s) | Total notes |
|-----------------|--------------------------|-----------------|-------------|
| sqlite          | 14.51                    | 2.07            | 1500        |
| progress        | 12.90                    | 2.47            | 2000        |
| mongo           | 14.65                    | 1.18            | 2500        |
| neo4j           | 16.23                    | 1.45            | 2500        |
| postgresql      | 15.87                    | 1.32            | 2500        |
| progress_server | 18.12                    | 2.89            | 2500        |

### 3. Логирование тестов
- Детально логируются ошибки, время вставки/чтения, статистика вставленных заметок и очистка после теста.
- Все события тестов доступны как console log, так и (опц) в файлах logs/

---

# --- ПОДКЛЮЧЕНИЕ И РАБОТА С MongoDB ---

## Консоль и GUI
1. Открыть shell контейнера MongoDB:
    ```bash
    docker exec -it neuro-qc-mongo mongosh
    ```
2. Подключиться с GUI, например "Compass":
    - URI: mongodb://localhost:27017

## Python:
```python
from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['notes_db']
for n in db.notes.find().limit(5):
    print(n)
```

## Примеры CLI-запросов:
```javascript
use notes_db
db.notes.find().limit(5).pretty()
```

---

# --- MONITORING / FASTAPI ENDPOINTS ---

В директории db/monitor_db.py реализован FastAPI REST API для мониторинга любой backend:

- Старт сервиса:
   ```bash
   uvicorn db.monitor_db:app --reload --port 8001
   ```
- Эндпоинты:
   - `/health` — JSON-статус, info по backend'у
   - `/count` — общее число заметок
   - `/count/html` — HTML-дашборд (рек. для браузера)

  Пример запуска: [http://localhost:8001/count/html](http://localhost:8001/count/html)


---

*monitor.py* из корня теперь legacy и НЕ используется для новых верификаций, весь мониторинг — через FastAPI.

---