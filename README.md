# 📦 Бэкенд MAX Bot API

## 🏗️ Архитектура

```
src/
├── main_fastapi.py      # Точка входа FastAPI
├── database/            # Работа с БД
│   ├── models.py        # SQLAlchemy модели
│   └── __init__.py      # Движок, сессии
├── api/                 # REST API эндпоинты
│   ├── buttons.py       # Кнопки меню
│   ├── forms.py         # Формы заявок
│   ├── submissions.py   # Создание заявок
│   ├── my.py            # Мои заявки
│   └── __init__.py      # Экспорт роутеров
├── admin/               # Админ-панель (sqladmin)
│   └── views.py         # Вьюшки моделей
├── schemas/             # Pydantic схемы
│   ├── buttons.py
│   ├── forms.py
│   ├── submissions.py
│   └── common.py
├── bot/                 # Telegram бот
│   ├── handlers/        # Обработчики команд
│   ├── keyboards/       # Клавиатуры
│   └── services/        # Сервисы (parser.py)
└── config/              # Конфигурация
    └── settings.py      # Переменные окружения
```

---

## 🚀 Технологии

| Компонент | Технология |
|-----------|-----------|
| Фреймворк | FastAPI 0.115.12 |
| Асинхронность | asyncio + uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| БД | PostgreSQL + asyncpg |
| Валидация | Pydantic 2.10.6 |
| Админка | sqladmin 0.20.1 |
| Бот | aiomax 2.12.4 |
| Парсинг | pandas + lxml + BeautifulSoup4 |

---

## 📡 API Endpoints

### **Корневые**
| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Статус приложения |

### **Расписание**
| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/groups` | Список групп |
| `GET` | `/api/schedule/{group_name}` | Расписание группы |

### **Кнопки**
| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/buttons` | Все активные кнопки |
| `GET` | `/api/buttons/{button_id}/form` | Форма для кнопки |

### **Заявки**
| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/submissions` | Создать заявку |
| `GET` | `/api/submissions/my` | Мои заявки |

### **Админка**
| Путь | Описание |
|------|----------|
| `/admin` | Панель управления |

---

## 🗄️ База Данных

### Таблицы (8 шт.)

```
roles                    users
├─ id                    ├─ id
└─ name                  ├─ first_name
                         ├─ second_name
buttons                  ├─ login (unique)
├─ id                    ├─ max_id (unique)
├─ title                 ├─ role_id (FK → roles)
├─ icon                  └─ password
├─ is_active
└─ sort_order            submissions
                         ├─ id
forms                    ├─ button_id (FK → buttons)
├─ id                    ├─ user_id (FK → users)
├─ button_id (FK → buttons) ├─ status
├─ title                 ├─ admin_comment
└─ description           ├─ created_at
                         └─ updated_at
questions
├─ id                    submission_answers
├─ question_text         ├─ id
├─ field_type            ├─ submission_id (FK → submissions)
├─ placeholder           ├─ question_id (FK → questions)
├─ options (JSON)        ├─ answer_value
├─ validation_regex      └─ created_at
└─ is_active

form_questions
├─ id
├─ form_id (FK → forms)
├─ question_id (FK → questions)
├─ sort_order
└─ is_required
```

---

## 📂 Основные модули

### **1. main_fastapi.py**
Точка входа приложения.
- Инициализация FastAPI
- CORS настройки
- Подключение роутеров
- Админ-панель (sqladmin)
- API расписания (парсинг Excel)

### **2. database/models.py**
SQLAlchemy модели:
- `Role` - роли пользователей
- `User` - пользователи
- `Button` - кнопки меню
- `Form` - формы заявок
- `Question` - вопросы
- `FormQuestion` - связь форм с вопросами
- `Submission` - заявки
- `SubmissionAnswer` - ответы

### **3. API модули**

#### **buttons.py**
```python
GET /api/buttons
```
Возвращает все активные кнопки меню.

#### **forms.py**
```python
GET /api/buttons/{button_id}/form
```
Возвращает форму с вопросами для кнопки.

#### **submissions.py**
```python
POST /api/submissions
```
Создаёт заявку с ответами на вопросы.

#### **my.py**
```python
GET /api/submissions/my
```
Возвращает все заявки текущего пользователя.

### **4. admin/views.py**
Админ-панель на sqladmin:
- `UserAdmin` - пользователи
- `ButtonAdmin` - кнопки
- `FormAdmin` - формы + вопросы
- `QuestionAdmin` - справочник вопросов
- `SubmissionAdmin` - заявки с ответами

Аутентификация: по логину/паролю (сессии).

### **5. schemas/*.py**
Pydantic схемы для валидации:
- `Button`, `ButtonResponse`
- `FormResponse`, `QuestionResponse`
- `SubmissionCreate`, `SubmissionResponse`
- `SubmissionListItem`, `SubmissionsListResponse`

### **6. bot/**
Telegram бот (aiomax):
- **handlers/** - обработка команд и callback
- **keyboards/** - меню и кнопки
- **services/parser.py** - парсинг сайта

**Важно:** Бот не использует БД, работает со статическими данными из `settings.py`.

---

## 🔐 Аутентификация

### API (Frontend)
- Заголовок `X-User-Id` для идентификации
- Временно: `default=1`
- **Нужно заменить на JWT/session**

### Админка
- Логин/пароль через форму
- Сессии через `SessionMiddleware`
- Роль "Админ" обязательна

---

## ⚙️ Конфигурация

### Переменные окружения (`.env`)
```env
# БД
DB_USER=postgres
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
DB_NAME=maxbot

# Секреты
SECRET_KEY=your-secret-key
TOKEN_BOT=telegram-bot-token
```

### settings.py
- `DATABASE_URL` - синхронный (Alembic)
- `DATABASE_URL_ASYNC` - асинхронный (бот/API)
- `SECTIONS` - структура сайта для бота

---

## 📊 Бизнес-логика

### Поток заявки:
```
1. User → GET /api/buttons
2. User → GET /api/buttons/{id}/form
3. User → POST /api/submissions
4. Admin → просматривает в /admin/submission
5. Admin → меняет статус (new → processing → ready → issued)
```

### Статусы заявок:
- `new` - 🔵 Новая
- `processing` - 🟡 В обработке
- `ready` - 🟢 Готова
- `issued` - ✅ Выдана
- `rejected` - 🔴 Отклонена
- `canceled` - ⚫ Отменена

---

## 🐳 Docker

### Dev (docker-compose.yml)
- API на порту 8000
- Frontend на порту 5173 (Vite dev server)
- Hot reload включён

### Prod (docker-compose.prod.yml)
- Nginx раздает фронтенд
- API на внутреннем network
- Port 80 для всего

---

## 📝 Скрипты

| Файл | Назначение |
|------|-----------|
| `clear_and_seed.py` | Очистка + тестовые данные |
| `migrate.py` | Миграция БД (удаление лишних таблиц) |

---

## 🔧 Проблемы и TODO

- [ ] **JWT аутентификация** вместо `X-User-Id`
- [ ] **Хеширование паролей** (сейчас plain text)
- [ ] **Email поле** в User (сейчас только login)
- [ ] **Валидация форм** на бэкенде
- [ ] **Файлы** (загрузка в заявках)
- [ ] **Pagination** для списка заявок
- [ ] **WebSocket** уведомления о статусе

---

## 📞 Контакты

- **API документация**: http://localhost:8000/docs
- **Админка**: http://localhost:8000/admin
- **Логин админа**: `admin` / `admin123`
