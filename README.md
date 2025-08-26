# Delivery Service

Сервис для управления доставкой посылок с современной архитектурой FastAPI.

## Архитектура

- **FastAPI** - асинхронный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Celery** - асинхронная обработка задач
- **Redis** - кэширование и брокер сообщений
- **MySQL** - основная база данных
- **Docker** - контейнеризация и оркестрация


## Быстрый запуск

### Требования
- Установить Docker и Docker Compose

### 1) Создайте файл .env в корне проекта
Пример минимальной конфигурации (можете скопировать как есть и при необходимости изменить пароли/имена):

```env
# --- Инициализация MySQL ---
MYSQL_DB=delivery
MYSQL_USER=delivery
MYSQL_PASSWORD=deliverypass
MYSQL_ROOT_PASSWORD=devrootpass

# --- Приложение ---
# Подключение к БД (внутри docker-сети хост у БД — "mysql", порт 3306)
DATABASE_URL=mysql+aiomysql://delivery:deliverypass@mysql:3306/delivery

# Redis (внутри docker-сети хост у Redis — "redis")
REDIS_URL=redis://redis:6379/0

# Celery (используем Redis как брокер и backend результатов)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Секрет для сессий
SESSION_SECRET=change_this_dev_secret

# Необязательные параметры
# CBR_URL=https://www.cbr-xml-daily.ru/daily_json.js
# EXRATE_TTL_SECONDS=3600
```

- MySQL проброшен на хост-машину на порт 3307 (`localhost:3307`). Внутри контейнеров используется стандартный порт 3306 и хост `mysql`.
- Redis проброшен на `localhost:6379` и доступен внутри сети по хосту `redis`.

### 2) Соберите и поднимите контейнеры
```bash
docker compose up -d --build
```

При старте:
- БД MySQL и Redis поднимутся
- Сервис API выполнит миграции Alembic и инициализацию базовых данных
- Запустится FastAPI на порту 8000
- Поднимутся Celery worker и Celery beat

### 3) Проверьте, что API доступен
- Swagger UI: http://localhost:8000/docs

### 4) Команды для просмотра логов
- Логи сервиса API: `docker compose logs -f api`
- Логи Celery worker: `docker compose logs -f celery-worker`
- Логи Celery beat: `docker compose logs -f celery-beat`
- Логи MySQL: `docker compose logs -f mysql`
- Логи Redis: `docker compose logs -f redis`

### Остановка
- Остановить контейнеры: `docker compose down`
- Остановить и удалить тома (полная очистка данных БД): `docker compose down -v`

## API Endpoints

- **Swagger UI**: http://localhost:8000/docs

### Основные эндпоинты:
- `GET /parcel-types` - типы посылок
- `POST /parcels/register` - регистрация посылки
- `GET /parcels` - список посылок
- `GET /parcels/{id}` - информация о посылке
- `POST /tasks/compute-costs` - пересчет стоимости