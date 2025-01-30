## Анонимный чат для общения в телеграм боте

### Установка

Перед установкой необходимо переименовать файл `.env.example` в `.env` и настроить `.env` файл.
Для минимальной работы необходимо изменить следующие переменные:

- `TELEGRAM_TOKEN` - токен телеграм бота
- `SUBSCRIBE_TELEGRAM_CHANNEL` - ID канала для обязательной подписки
- `SUBSCRIBE_TELEGRAM_CHANNEL_LINK` - ссылка на канал для обязательной подписки
- `ADMIN_TELEGRAM_ID`
- `POSTGRES_PASSWORD`

⚠️ Обязательно добавьте бота в канал, на который пользователям следует подписаться.

#### Запуск через Docker

Выполните следующую команду:

```shell
docker compose up
# or docker compose up -d
```

#### Python - Windows

1. Установите PostgreSQL
2. Установите Redis
3. Запуск:

```shell
# Устанавливаем виртаульное окружение
python -m venv .venv
# Активируем его
.venv\Scripts\activate
# Обновялем pip
python -m pip install --upgrade pip
# Устанавливаем зависимости
python -m pip install -r requirements.txt

# Для запуска проекта запускаем модуль main.py
python main.py -le
```

### Функционал

- Поиск собеседника
- Настройка возраста собеседника
- Узнать кол-во пользователей находящихся в общении

### Используемые технологии

- База данных: `PostgreSQL`
- Временное хранилище: `Redis`

### Зависимости для разработчиков

Интерпретатор - `Python~=3.12.4`

- `aiogram~=3.17.0`
- `asyncpg~=0.30.0`
- `loguru~=0.7.3`
- `pyyaml~=6.0.2`
- `pydantic~=2.10.6`
- `python-dotenv~=1.0.1`
- `redis~=5.2.1`
