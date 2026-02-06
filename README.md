# Trade Tree

`Trade Tree` — сервис на **FastAPI + PostgreSQL** для работы с каталогом товаров и заказами.

Проект демонстрирует:
- иерархию категорий (дерево);
- операции с заказами и позициями заказа;
- агрегатные SQL-запросы (статистика по клиентам и категориям);
- миграции схемы через Alembic;
- скрипт заполнения БД тестовыми данными.

## Функциональность

### Что умеет API
- Получить количество дочерних категорий для категорий первого уровня.
- Получить статистику клиентов по сумме заказов.
- Добавить товар в заказ:
  - с блокировкой строки товара (`FOR UPDATE`);
  - с проверкой остатка;
  - с `upsert` в `order_items`.

## Структура проекта

```text
trade-tree/
├── app/
│   ├── api/
│   │   ├── catalog/
│   │   │   ├── categories.py      # эндпоинт аналитики по категориям
│   │   │   ├── orders.py          # эндпоинты заказов и статистики
│   │   │   └── schemas.py         # Pydantic-схемы
│   │   └── router.py              # объединение роутеров
│   ├── db.py                      # engine + SessionLocal + get_db
│   ├── main.py                    # создание FastAPI-приложения
│   ├── models.py                  # ORM-модели
│   ├── seed.py                    # генерация тестовых данных
│   └── settings.py                # настройки из .env
├── alembic/
│   ├── versions/001_baseline.py   # базовая миграция
│   └── README.md                  # Запросы, схема БД
├── docker-compose.yml             # PostgreSQL
├── requirements.txt
└── README.md
```

## Требования

- Python **3.14+** (см. `pyproject.toml`)
- PostgreSQL **16+**
- pip / venv

## Быстрый старт

### 1) Поднять PostgreSQL

```bash
docker compose up -d db
```

По умолчанию из `docker-compose.yml`:
- host: `localhost`
- port: `5432`
- db: `shop`
- user: `postgres`
- password: `postgres`

### 2) Создать и активировать виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Установить зависимости

```bash
pip install -r requirements.txt
```

### 4) Создать `.env` в корне проекта

Пример:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/shop
APP_NAME=Trade Tree API
VERSION=1.0.0
API_PREFIX=/api/v1
```

> В коде используются переменные окружения: `DATABASE_URL`, `APP_NAME`, `VERSION`, `API_PREFIX`.

### 5) Применить миграции

```bash
alembic upgrade head
```

### 6) Запустить приложение

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Документация будет доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Seed: наполнение базы тестовыми данными

Скрипт `app/seed.py` создаёт:
- дерево категорий;
- 3 клиентов;
- 200 000 товаров;
- 300 заказов с позициями.

Запуск:

```bash
python -m app.seed
```

Если база уже заполнена (в таблице `categories` есть данные), скрипт выведет:

```text
DB already seeded, skipping
```

При успешном выполнении:

```text
Seed done.
```

## Примеры API-запросов

Ниже примеры для случая, когда `API_PREFIX=/api/v1`.

### 1) Статистика клиентов

**Endpoint**

```http
GET /api/v1/orders/clients/statistics
```

**curl**

```bash
curl -X GET "http://localhost:8000/api/v1/orders/clients/statistics"
```

**Пример ответа**

```json
[
  {
    "name": "ООО Ромашка",
    "total_amount": 1452300
  },
  {
    "name": "ИП Иванов",
    "total_amount": 1210000
  }
]
```

### 2) Количество дочерних категорий (для 1-го уровня)

**Endpoint**

```http
GET /api/v1/categories/children-count
```

**curl**

```bash
curl -X GET "http://localhost:8000/api/v1/categories/children-count"
```

**Пример ответа**

```json
[
  {
    "id": 1,
    "name": "Бытовая техника",
    "children_count": 3
  },
  {
    "id": 2,
    "name": "Компьютеры",
    "children_count": 2
  }
]
```

### 3) Добавить товар в заказ

**Endpoint**

```http
POST /api/v1/orders/{order_id}/items
```

**curl**

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 123,
    "quantity": 2
  }'
```

**Пример успешного ответа**

```json
{
  "order_id": 1,
  "product_id": 123,
  "new_qty": 5,
  "remaining_stock": 42
}
```

**Коды ошибок**
- `404` — заказ или товар не найден.
- `409` — недостаточно товара на складе.
- `500` — внутренняя ошибка сервера.

## Полезные команды

```bash
# создать новую миграцию
alembic revision -m "your_migration_name"

# откатить на одну миграцию
alembic downgrade -1

# проверить применённую ревизию
alembic current
```

## Примечания

- В `seed.py` генерируется большой объём данных (200k товаров), первый запуск может занять заметное время.
- Если хотите быстрее локально проверить API, уменьшите количество создаваемых товаров в `app/seed.py`.
