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
- Python 3.11+ (рекомендуется 3.12 или 3.13)
- aiogram 3
- PostgreSQL
- SQLAlchemy (async)
- Alembic
- python-dotenv
- Docker Compose
- VS Code

## Первый запуск (шаг за шагом)
1. Создайте виртуальное окружение и активируйте его:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Обновите пакетные инструменты и установите зависимости:
```bash
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
```

3. Создайте `.env` из шаблона:
```bash
cp .env.example .env
```
Заполните значения:
- `BOT_TOKEN` — токен от @BotFather
- `ADMIN_ID` — ваш числовой Telegram ID
- `DATABASE_URL` — URL подключения к PostgreSQL

4. Запустите PostgreSQL через Docker Compose:
```bash
docker compose up -d
```

5. Примените миграции:
```bash
alembic upgrade head
```

6. Запустите бота:
```bash
python -m bot.main
```

## Важно для Python 3.14 (ошибка `pydantic-core` / `pyo3-ffi`)
Если при `pip install -r requirements.txt` вы видите ошибку вида:
`configured Python interpreter version (3.14) is newer than PyO3's maximum supported version` — значит pip пытается собрать старую версию `pydantic-core` из исходников.

Что сделать:
1. Убедитесь, что используете актуальный pip:
```bash
python -m pip install -U pip setuptools wheel
```
2. Установите зависимости заново (в чистом venv):
```bash
pip install --no-cache-dir -r requirements.txt
```
3. Если появляется конфликт `aiogram`/`pydantic`, не фиксируйте `pydantic` вручную — в проекте он должен подбираться автоматически через зависимость `aiogram`.
4. Проверьте, что Python не слишком новый для части экосистемы на вашей машине. Самый стабильный вариант для учебного/прикладного проекта: Python 3.12/3.13.

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
