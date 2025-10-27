[![Python](https://img.shields.io/badge/python-3.8+-blue?logo=python)](https://python.org) [![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://www.docker.com/) [![Tested DBs](https://img.shields.io/badge/DBs-SQLite--Progress--Mongo--Neo4j--PostgreSQL--Cassandra-green?logo=mongodb)](#бэкенды-баз-данных) [![Frontend](https://img.shields.io/badge/frontend-HTML5--CSS3--TypeScript-blue?logo=html5)](#-полные-примеры-запуска-всех-компонентов) [![Monitoring](https://img.shields.io/badge/monitoring-FastAPI--Grafana--Prometheus-orange?logo=grafana)](#-полные-примеры-запуска-всех-компонентов)

# Телеграм-бот заметок + напоминаний (SQLite/Mongo/Neo4j/PostgreSQL/Cassandra/Progress)

**[🇷🇺 Русский README ниже]**

---

## 🚩 Features
- Telegram bot for notes & reminders
- Hot-swap DB: SQLite, MongoDB (Docker), Neo4j (Docker), PostgreSQL (Docker), Cassandra (Docker), In-memory (Progress)
- Dockerized stack, easy Compose up
- Unit, integration, and load test coverage
- FastAPI REST DB monitoring (see `/count/html` dashboard)
- **Modern web frontend** with HTML5, CSS3, TypeScript for reports, search, and monitoring
- Elasticsearch for advanced querying across all databases
- Grafana dashboards for monitoring and reporting
- MCP Cursor integration ready
- Full logging/reporting, HTML perf reports

---

## ✅ Quick Preview
```bash
# Switch to MongoDB backend, launch containerized DB & run bot:
docker compose -f mongo.docker-compose.yml up -d
set USE_DB_BACKEND=mongo
python bot.py

# Launch monitoring and frontend:
uvicorn db.monitor_db:app --host 0.0.0.0 --port 8001 &
cd frontend && python -m http.server 8000 &

# Access interfaces:
# Bot: Telegram
# Monitoring: http://localhost:8001/count/html
# Frontend Dashboard: http://localhost:8000
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
- **`Dockerfile.cassandra`** - Cassandra backend
- **`Dockerfile.progress`** - Progress (in-memory) backend

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

# Cassandra
docker compose -f cassandra.docker-compose.yml up -d
docker build -f dockerfiles/Dockerfile.cassandra -t tg-notes-bot:cassandra .
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:cassandra
```

Подробная документация: [dockerfiles/README.md](../dockerfiles/README.md)

---

# 🔍 Elasticsearch для запросов по всем БД

Elasticsearch предоставляет мощные возможности поиска и анализа данных из всех подключенных баз данных.

### Запуск Elasticsearch + Kibana:
```bash
docker compose -f elasticsearch.docker-compose.yml up -d
```

### Доступ к сервисам:
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

### Основные возможности:
- Полнотекстовый поиск по всем заметкам
- Агрегация и аналитика данных
- Визуализация данных через Kibana
- Индексирование данных из всех БД

---

# 📊 Grafana для мониторинга и отчётности

Grafana предоставляет комплексные дашборды для мониторинга производительности всех баз данных.

### Запуск Grafana + Prometheus:
```bash
docker compose -f grafana.docker-compose.yml up -d
```

### Доступ к сервисам:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### Основные возможности:
- Дашборды производительности БД
- Мониторинг метрик в реальном времени
- Алерты и уведомления
- Отчёты по использованию ресурсов

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
- **Cassandra** (wide-column БД через docker, масштабируемое хранение)

Переключение осуществляется переменной окружения:
```bash
set USE_DB_BACKEND=sqlite
set USE_DB_BACKEND=progress
set USE_DB_BACKEND=mongo
set USE_DB_BACKEND=neo4j
set USE_DB_BACKEND=postgresql
set USE_DB_BACKEND=cassandra
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

Для Cassandra требуется установленный и запущенный контейнер:
```bash
docker compose -f cassandra.docker-compose.yml up -d
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
| cassandra       | 18.45                    | 1.89            | 2500        |

### 3. End-to-End (E2E) Integration Testing
Комплексное тестирование всех бэкендов БД с генерацией отчётов для Grafana:

#### Запуск полного E2E теста:
```bash
cd notes-mcp-sqlite/test
python run_e2e_suite.py
```

#### Запуск только E2E интеграционного теста:
```bash
cd notes-mcp-sqlite/test
python test_e2e_integration.py
```

#### Что тестирует E2E:
- **CRUD операции**: создание, чтение, обновление, удаление заметок
- **Поиск**: полнотекстовый поиск по заголовкам и содержимому
- **Напоминания**: система напоминаний с временными метками
- **Производительность**: бенчмарки вставки, поиска и чтения
- **Статистика**: получение статистики по базе данных

#### Генерируемые отчёты:
1. **JSON Report** (`e2e_test_report_YYYYMMDD_HHMMSS.json`) - детальные результаты
2. **HTML Dashboard** (`reports/e2e_report_YYYYMMDD_HHMMSS.html`) - интерактивная панель с графиками
3. **Prometheus Metrics** (`reports/prometheus_metrics_YYYYMMDD_HHMMSS.txt`) - метрики для Grafana
4. **Grafana Metrics** (`grafana_metrics_YYYYMMDD_HHMMSS.json`) - JSON метрики для Grafana

#### Пример HTML Dashboard:
- 📊 Интерактивные графики производительности (Chart.js)
- 📋 Таблица сравнения всех бэкендов
- 🔍 Детальные результаты по каждому бэкенду
- 🏆 Рейтинг производительности

#### Интеграция с Grafana:
1. **Prometheus Metrics**: импортируйте `.txt` файл в Prometheus
2. **JSON Metrics**: используйте `.json` файл для создания дашбордов
3. **HTML Report**: откройте в браузере для визуализации

#### Конфигурация E2E теста:
```python
test_config = {
    'notes_count': 100,           # Количество заметок для тестирования
    'search_queries': ['test', 'note', 'important'],  # Поисковые запросы
    'reminder_hours': 24,         # Часы для тестирования напоминаний
    'performance_iterations': 3   # Итерации для бенчмарков
}
```

### 4. Логирование тестов
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

# 🚀 Полные примеры запуска всех компонентов

## 📋 Быстрый старт - пошаговые инструкции

### 1. Подготовка окружения
```bash
# Установка зависимостей
pip install -r requirements.txt

# Создание Docker сети (один раз)
docker network create neuroqc-net

# Настройка токена бота
set BOT_TOKEN=YOUR_BOT_TOKEN_HERE
```

### 2. Выбор и запуск базы данных

#### SQLite (по умолчанию, без Docker)
```bash
set USE_DB_BACKEND=sqlite
python bot.py
```

#### MongoDB
```bash
# Запуск MongoDB контейнера
docker compose -f mongo.docker-compose.yml up -d

# Переключение на MongoDB
set USE_DB_BACKEND=mongo
python bot.py
```

#### Neo4j
```bash
# Запуск Neo4j контейнера
docker compose -f neo4j.docker-compose.yml up -d

# Переключение на Neo4j
set USE_DB_BACKEND=neo4j
python bot.py
```

#### PostgreSQL
```bash
# Запуск PostgreSQL контейнера
docker compose -f postgresql.docker-compose.yml up -d

# Переключение на PostgreSQL
set USE_DB_BACKEND=postgresql
python bot.py
```

#### Cassandra
```bash
# Запуск Cassandra контейнера
docker compose -f cassandra.docker-compose.yml up -d

# Переключение на Cassandra
set USE_DB_BACKEND=cassandra
python bot.py
```

#### Progress (In-Memory)
```bash
# Переключение на Progress
set USE_DB_BACKEND=progress
python bot.py
```

### 3. Запуск мониторинга и веб-интерфейса

#### FastAPI мониторинг
```bash
# Запуск FastAPI сервера мониторинга
uvicorn db.monitor_db:app --host 0.0.0.0 --port 8001

# Открыть в браузере:
# http://localhost:8001/health - JSON статус
# http://localhost:8001/count/html - HTML дашборд
```

#### Веб-фронтенд (новый)
```bash
# Запуск HTTP сервера для фронтенда
cd frontend
python -m http.server 8000

# Открыть в браузере:
# http://localhost:8000 - Полный дашборд с графиками
```

### 4. Запуск дополнительных сервисов

#### Elasticsearch + Kibana
```bash
# Запуск Elasticsearch и Kibana
docker compose -f elasticsearch.docker-compose.yml up -d

# Доступ:
# Elasticsearch: http://localhost:9200
# Kibana: http://localhost:5601
```

#### Grafana + Prometheus
```bash
# Запуск Grafana и Prometheus
docker compose -f grafana.docker-compose.yml up -d

# Доступ:
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## 🧪 Тестирование

### Запуск всех тестов
```bash
cd test
set PYTHONPATH=..
python test_db_backends.py
```

### Генерация отчёта производительности
```bash
cd test
python report_perf.py
# Открыть db_perf_report.html в браузере
```

### Тестирование конкретной базы данных
```bash
# Тест только SQLite
set USE_DB_BACKEND=sqlite
python test_db_backends.py

# Тест только MongoDB
set USE_DB_BACKEND=mongo
python test_db_backends.py
```

## 🐳 Docker контейнеры

### Сборка специализированных образов
```bash
# SQLite образ
docker build -f dockerfiles/Dockerfile.sqlite -t tg-notes-bot:sqlite .

# MongoDB образ
docker build -f dockerfiles/Dockerfile.mongo -t tg-notes-bot:mongo .

# Neo4j образ
docker build -f dockerfiles/Dockerfile.neo4j -t tg-notes-bot:neo4j .

# PostgreSQL образ
docker build -f dockerfiles/Dockerfile.postgresql -t tg-notes-bot:postgresql .

# Cassandra образ
docker build -f dockerfiles/Dockerfile.cassandra -t tg-notes-bot:cassandra .

# Progress образ
docker build -f dockerfiles/Dockerfile.progress -t tg-notes-bot:progress .
```

### Запуск контейнеров
```bash
# MongoDB контейнер
docker compose -f mongo.docker-compose.yml up -d
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:mongo

# PostgreSQL контейнер
docker compose -f postgresql.docker-compose.yml up -d
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:postgresql
```

## 🔧 Утилиты и скрипты

### Создание тестовых данных
```bash
# Создание базы данных с тестовыми данными
python create_db.py

# Создание тестовых логов
python create_test_logs.py

# Очистка тестовых логов
python clean_test_logs.py
```

### Мониторинг и анализ
```bash
# Запуск мониторинга (legacy)
python monitor.py

# Тестирование новых функций
python test_new_features.py

# Демонстрационные запросы к БД
python demo_queries.py
```

## 📊 Полный стек для разработки

### Запуск всех сервисов одновременно
```bash
# Терминал 1: База данных
docker compose -f mongo.docker-compose.yml up -d

# Терминал 2: Бот
set USE_DB_BACKEND=mongo
python bot.py

# Терминал 3: FastAPI мониторинг
uvicorn db.monitor_db:app --host 0.0.0.0 --port 8001

# Терминал 4: Веб-фронтенд
cd frontend
python -m http.server 8000

# Терминал 5: Elasticsearch
docker compose -f elasticsearch.docker-compose.yml up -d

# Терминал 6: Grafana
docker compose -f grafana.docker-compose.yml up -d
```

### Проверка статуса всех сервисов
```bash
# Проверка Docker контейнеров
docker ps

# Проверка портов
netstat -an | findstr :8000  # Фронтенд
netstat -an | findstr :8001  # FastAPI
netstat -an | findstr :27017 # MongoDB
netstat -an | findstr :7475  # Neo4j HTTP
netstat -an | findstr :7688  # Neo4j Bolt
netstat -an | findstr :5432  # PostgreSQL
netstat -an | findstr :9042  # Cassandra
netstat -an | findstr :9200  # Elasticsearch
netstat -an | findstr :5601  # Kibana
netstat -an | findstr :3000  # Grafana
netstat -an | findstr :9090  # Prometheus
```

## 🎯 Типичные сценарии использования

### Сценарий 1: Быстрый старт с SQLite
```bash
set USE_DB_BACKEND=sqlite
python bot.py
# Бот работает с локальной SQLite базой
```

### Сценарий 2: Разработка с MongoDB
```bash
docker compose -f mongo.docker-compose.yml up -d
set USE_DB_BACKEND=mongo
python bot.py
uvicorn db.monitor_db:app --host 0.0.0.0 --port 8001
# Открыть http://localhost:8001/count/html
```

### Сценарий 3: Полный мониторинг
```bash
# Все сервисы
docker compose -f mongo.docker-compose.yml up -d
docker compose -f elasticsearch.docker-compose.yml up -d
docker compose -f grafana.docker-compose.yml up -d

# Приложения
set USE_DB_BACKEND=mongo
python bot.py &
uvicorn db.monitor_db:app --host 0.0.0.0 --port 8001 &
cd frontend && python -m http.server 8000 &

# Доступ к интерфейсам:
# Бот: Telegram
# Мониторинг: http://localhost:8001/count/html
# Фронтенд: http://localhost:8000
# Grafana: http://localhost:3000
# Kibana: http://localhost:5601
```

### Сценарий 4: Тестирование производительности
```bash
# Тест всех баз данных
cd test
set PYTHONPATH=..
python test_db_backends.py

# Генерация отчёта
python report_perf.py

# Просмотр результатов
start db_perf_report.html
```

---