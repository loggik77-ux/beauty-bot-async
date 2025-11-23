# Beauty Bot Async API

FastAPI приложение для управления записями в салоне красоты.

## Технологии

- **FastAPI** - современный веб-фреймворк
- **SQLModel** - ORM на основе SQLAlchemy и Pydantic
- **PostgreSQL** - база данных
- **psycopg3** - асинхронный драйвер PostgreSQL
- **Alembic** - миграции базы данных

## Локальная разработка

### Требования

- Python 3.11+
- PostgreSQL

### Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # или
   source .venv/bin/activate  # Linux/Mac
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корне проекта:
   ```env
   DATABASE_URL=postgresql+psycopg.async://postgres:postgres@localhost:5432/beautybot
   ```

5. Создайте базу данных:
   ```sql
   CREATE DATABASE beautybot;
   ```

6. Запустите миграции (опционально):
   ```bash
   alembic upgrade head
   ```

7. Запустите сервер:
   ```bash
   uvicorn main:app --reload
   ```

API будет доступно по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

## Деплой на Railway

### Подготовка

1. Убедитесь, что все файлы закоммичены в Git
2. Файлы для Railway уже настроены:
   - `Procfile` - команда запуска
   - `runtime.txt` - версия Python
   - `requirements.txt` - зависимости

### Шаги деплоя

1. Зайдите на [Railway](https://railway.app)
2. Создайте новый проект
3. Подключите ваш GitHub репозиторий
4. Добавьте PostgreSQL базу данных:
   - В проекте нажмите "New" → "Database" → "Add PostgreSQL"
   - Railway автоматически создаст переменную `DATABASE_URL`

5. Railway автоматически определит проект как Python и запустит его
6. Приложение будет доступно по URL, который Railway предоставит

### Переменные окружения

Railway автоматически устанавливает:
- `DATABASE_URL` - подключение к PostgreSQL
- `PORT` - порт для приложения (используется в Procfile)

### Миграции на Railway

После деплоя можно запустить миграции через Railway CLI:

```bash
railway run alembic upgrade head
```

Или через веб-интерфейс Railway: Settings → Deploy → Run Command → `alembic upgrade head`

## API Endpoints

### POST /appointments/
Создание новой записи

**Body:**
```json
{
  "salon_id": 1,
  "client_tg_id": 123456789,
  "service_name": "Стрижка",
  "start_at": "2024-01-15T14:00:00",
  "duration_min": 60
}
```

### GET /appointments/free-slots/
Получение свободных слотов

**Query параметры:**
- `salon_id` (int) - ID салона
- `date_str` (str) - дата в формате YYYY-MM-DD
- `duration_min` (int, optional) - длительность в минутах (по умолчанию 60)

### GET /appointments/my/
Получение записей клиента

**Query параметры:**
- `client_tg_id` (int) - Telegram ID клиента

### PATCH /appointments/{appointment_id}/cancel
Отмена записи

**Query параметры:**
- `client_tg_id` (int) - Telegram ID клиента

## Структура проекта

```
beauty-bot-async/
├── main.py              # Точка входа приложения
├── database.py          # Конфигурация БД
├── models.py            # SQLModel модели
├── schemas.py           # Pydantic схемы
├── crud.py              # CRUD операции
├── routers/             # API роутеры
│   └── appointment.py   # Эндпоинты записей
├── alembic/             # Миграции БД
├── requirements.txt     # Зависимости
├── Procfile             # Команда запуска для Railway
└── runtime.txt          # Версия Python
```

## Примечания

- При первом запуске приложение автоматически создает таблицы в БД
- Для продакшена рекомендуется использовать миграции Alembic вместо автоматического создания таблиц
- Railway автоматически конвертирует `postgresql://` в `postgresql+psycopg://` в коде

