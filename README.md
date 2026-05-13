# Telegram-бот для бронирования столов в баре

## Описание проекта
Информационная система на базе Telegram-бота для автоматизации бронирования столиков и консультирования клиентов бара. Бот предоставляет справочную информацию, оформляет/изменяет/отменяет брони, сохраняет заявки в PostgreSQL и уведомляет администратора.

## Функции
- Главное меню:
  - Получить информацию
  - Забронировать стол
  - Изменить бронь
  - Отменить бронь
  - Связаться с администратором
- Справочная информация:
  - режим работы
  - адрес
  - меню
  - правила бронирования
  - акции
  - контакты
- Создание брони через FSM с валидацией полей.
- Изменение и отмена брони по номеру телефона.
- Админ-панель (`/admin`):
  - просмотр новых заявок
  - подтверждение/отклонение
  - просмотр всех бронирований
  - смена статуса

## Технологии
- Python
- aiogram 3
- PostgreSQL
- SQLAlchemy (async)
- Alembic
- python-dotenv
- Docker Compose
- VS Code

## Установка зависимостей
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка окружения
1. Скопируйте шаблон:
```bash
cp .env.example .env
```
2. Заполните переменные в `.env`:
- `BOT_TOKEN`
- `ADMIN_ID`
- `DATABASE_URL`

## Запуск PostgreSQL через Docker Compose
```bash
docker compose up -d
```

## Миграции БД
```bash
alembic upgrade head
```

## Запуск бота
```bash
python -m bot.main
```

## Структура проекта
```text
bot/
  main.py
  config.py
  database.py
  models.py
  keyboards.py
  states.py
  handlers/
    user.py
    booking.py
    admin.py
    info.py
  services/
    reservation_service.py
    notification_service.py
migrations/
.env.example
requirements.txt
docker-compose.yml
README.md
```
