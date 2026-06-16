# SPKBOT MAX - Docker Setup

## Запуск

1. Скопируйте `.env.example` в `.env` и заполните:
```bash
cp .env.example .env
```

2. Запустите все сервисы:
```bash
docker-compose up -d --build
```

3. Примените миграции:
```bash
docker-compose exec backend alembic upgrade head
```

4. (Опционально) Заполните базу тестовыми данными:
```bash
docker-compose exec backend python clear_and_seed.py
```

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| **db** | 5432 | PostgreSQL |
| **backend** | 8000 | FastAPI REST API |
| **frontend** | 80 | React + Nginx |
| **bot** | - | Telegram/MAX Bot |

## Управление

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (удалит БД!)
docker-compose down -v

# Пересобрать образы
docker-compose up -d --build

# Посмотреть логи
docker-compose logs -f backend
docker-compose logs -f bot
docker-compose logs -f frontend

# Выполнить команды в контейнере
docker-compose exec backend python clear_and_seed.py
docker-compose exec backend alembic upgrade head
```

## Доступы

- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
- Admin Panel: `http://localhost:8000/admin`
- Database: `localhost:5432`
