<div align="center">
  <h1>🔗 URL-Shortener</h1>
  <p><strong>Высокопроизводительный сервис для сокращения ссылок на FastAPI с современным веб-интерфейсом</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.12.10-blue?style=flat-square&logo=python" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-0.136.0-009688?style=flat-square&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/SQLAlchemy-2.0.49-red?style=flat-square&logo=sqlalchemy" alt="SQLAlchemy">
    <img src="https://img.shields.io/badge/Alembic-1.18.4-FFB300?style=flat-square&logo=python" alt="Alembic">
    <img src="https://img.shields.io/badge/PostgreSQL-17-336791?style=flat-square&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/Redis-7.4-DC382D?style=flat-square&logo=redis" alt="Redis">
    <img src="https://img.shields.io/badge/Docker-✓-2496ED?style=flat-square&logo=docker" alt="Docker">
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT">
    <img src="https://img.shields.io/badge/HTML5-CSS3-orange?style=flat-square&logo=html5" alt="HTML5/CSS3">
    <img src="https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=flat-square&logo=javascript" alt="JavaScript">
    <img src="https://img.shields.io/badge/Nginx-1.27-009639?style=flat-square&logo=nginx" alt="Nginx">
  </p>
</div>

## ✨ О проекте

**URL-Shortener** — это полностью контейнеризированный сервис для создания коротких ссылок, написанный на современном стеке технологий. Проект создан с упором на производительность, масштабируемость и удобство использования.

### Основные возможности:
- 🚀 **Мгновенные редиректы** благодаря кэшированию в Redis.
- 📊 **Детальная статистика** по каждой ссылке (количество переходов, дата создания).
- 🎨 **Современный веб-интерфейс** с анимированным фоном, поддержкой темной темы и адаптивным дизайном.
- ⚙️ **Гибкие настройки** — возможность задать свой вариант ссылки (custom slug) или выбрать её длину.
- 🗄️ **Управление схемой БД** через Alembic миграции (отдельный сервис).
- 🐳 **Docker-first подход** — весь стек поднимается одной командой.
- 🛡️ **Защита API** — встроенное ограничение запросов с автоблокировкой
- 📈 **Точная аналитика** — автоматический сброс данных из Redis в PostgreSQL

## 🛠 Стек технологий

| Компонент | Технология |
|-----------|------------|
| **Язык (Backend)** | [Python 3.12.10](https://www.python.org/) |
| **Веб-фреймворк (Backend)** | [FastAPI 0.136.0](https://fastapi.tiangolo.com/) |
| **ORM** | [SQLAlchemy 2.0.49](https://www.sqlalchemy.org/) |
| **Миграции БД** | [Alembic 1.18.4](https://alembic.sqlalchemy.org/) |
| **База данных** | [PostgreSQL 17.4](https://www.postgresql.org/) |
| **Кэш** | [Redis 7.4](https://redis.io/) |
| **Веб-сервер (Frontend)** | [Nginx](https://nginx.org/) |
| **Фронтенд** | HTML5, CSS3, JavaScript (Vanilla) |
| **Контейнеризация** | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) |
| **Тестирование** | [Pytest](https://docs.pytest.org/) |
| **Нагрузочное тестирование** | [Locust](https://locust.io/) |

## 🚀 Быстрый старт

### Предварительные требования
- Установленные [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)

### Установка и запуск

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/kite-house/URL-Shortener.git
   cd URL-Shortener
   ```

2. **Настройте переменные окружения**
   
   Скопируйте файл с примером конфигурации и отредактируйте его под себя:
   ```bash
   cp .env.example .env
   ```
   
   Минимально необходимые настройки:
   ```ini
   # ==================================================
   # ⚙️ REQUIRED ENVIRONMENT VARIABLES
   # ==================================================
   
   # 🚀 Application Mode
   MODE=DEV  # DEV, TEST, or PROD
   BACKEND_PORT=8000
   BACKEND_HOST=0.0.0.0
   FRONTEND_PORT=80
   
   # ==================================================
   # 🗄️ Database (PostgreSQL)
   # ==================================================
   DB_USER=postgres
   DB_PASS=postgres
   DB_HOST=postgres_db
   DB_PORT=5432
   DB_NAME=postgres_db
   
   # ==================================================
   # ⚡ Redis (Cache)
   # ==================================================
   REDIS_HOST=cache
   REDIS_PORT=6379
   REDIS_PASSWORD=1234
   ```

3. **Запустите все сервисы**
   ```bash
   docker compose up -d --build
   ```
   
   > **Примечание:** Сервис `migrations` автоматически применяет миграции перед запуском backend. Backend запускается только после успешного завершения миграций.

4. **Проверьте работу**
   - Веб-интерфейс: http://localhost
   - Документация API (Swagger): http://localhost:8000/docs

## 📊 Нагрузочное тестирование

Проект прошел нагрузочное тестирование с помощью **Locust** для проверки производительности и стабильности под нагрузкой.

### Результаты тестирования

| Пользователей | RPS | Spawn Rate | Ошибки |
|--------------|-----|------------|--------|
| 150 | 70 | 15/сек | 0% |
| 300 | 143 | 30/сек | 0% |
| 500 | 160 | 50/сек | 0% |
| 1000 | 150 | 100/сек | 1% |

### Ключевые выводы

✅ **Отличная линейная масштабируемость** до 500 пользователей  
✅ **Максимальный RPS:** 160 при 500 concurrent пользователях  
✅ **Стабильность:** 100% успешных запросов до 500 пользователей  
✅ **Высокая эффективность кэширования** — RPS вырос на 57% по сравнению с предыдущей версией  
⚠️ **Предел мощности:** при 1000 пользователях RPS падает на 6%, появляются единичные ошибки (1%)  
🎯 **Рекомендация:** оптимальная рабочая нагрузка — до 500 пользователей. Для 1000+ требуется горизонтальное масштабирование.

### Как запустить нагрузочные тесты

1. **Установите Locust**
   ```bash
   pip install locust
   ```

2. **Запустите приложение**
   ```bash
   echo "MODE=TEST" >> .env
   docker-compose up -d --build
   ```

3. **Запустите Locust**
   ```bash
   # Веб-интерфейс
   locust -f backend/tests/load_testing.py --host=http://localhost:8000
   
   # Или консольный режим
   locust -f backend/tests/load_testing.py --host=http://localhost:8000 \
     --headless --users 500 --spawn-rate 50 --run-time 5m --html=report.html
   ```

4. **Откройте веб-интерфейс Locust** → http://localhost:8089

5. **После тестирования полностью очистите окружение
  ```bash
  docker-compose down -v
  ```

## 🗄️ Управление миграциями (Alembic)

Проект использует **Alembic** для управления схемой базы данных. Миграции запускаются в отдельном сервисе `migrations`, который выполняется один раз при старте.

### Архитектура миграций

```yaml
migrations:
  container_name: migrations
  build: ./backend
  command: alembic upgrade head  # Применяет миграции при запуске
  depends_on:
    postgres_db:
      condition: service_healthy
  restart: "no"  # Запускается один раз и останавливается
```

Backend зависит от `migrations` и запускается только после успешного применения миграций.

### Команды для работы с миграциями

```bash
# Создать новую миграцию (на основе изменений в моделях)
docker compose exec backend alembic revision --autogenerate -m "Описание изменений"

# Применить все ожидающие миграции вручную
docker compose exec backend alembic upgrade head

# Откатить последнюю миграцию
docker compose exec backend alembic downgrade -1

# Показать текущую версию БД
docker compose exec backend alembic current

# Показать историю миграций
docker compose exec backend alembic history

# Откатить все миграции
docker compose exec backend alembic downgrade base

# Перезапустить миграции (полезно после сброса БД)
docker compose up -d --force-recreate migrations
```

### Структура миграций

```
backend/
├── alembic/
│   ├── versions/          # Сгенерированные миграции
│   │   └── xxx_migration_name.py
│   ├── env.py            # Конфигурация Alembic
│   └── script.py.mako    # Шаблон для создания миграций
└── alembic.ini           # Основной конфиг Alembic
```

## 🧪 Тестирование

Запуск тестов внутри Docker-контейнера:

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit test_runner
```

## 📖 Использование

### 🌐 Веб-интерфейс

Главная страница сервиса предлагает интуитивно понятный интерфейс для работы со ссылками.

| Функция | Описание |
|---------|----------|
| **Сокращение ссылки** | Вставьте длинную ссылку в поле ввода и нажмите кнопку "Сократить" |
| **Свой вариант ссылки** | Введите желаемую часть короткой ссылки (например, my-link) |
| **Длина ссылки** | Выберите длину генерируемой ссылки с помощью слайдера (от 3 до 10 символов) |
| **Копирование** | Скопируйте полученную короткую ссылку одним кликом |
| **Темная тема** | Переключайтесь между светлой и темной темой интерфейса |

### 🔗 Создание короткой ссылки через API

**Эндпоинт:** `POST /api/shorten`

**Параметры запроса:**
- `url` (обязательный) — исходный длинный URL
- `custom_slug` (опционально) — желаемая кастомная часть
- `length` (опционально) — желаемая длина генерируемой части

**Примеры запросов (cURL):**

```bash
# Без дополнительных параметров
curl -X POST "http://localhost:8000/api/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'

# С кастомным slug
curl -X POST "http://localhost:8000/api/shorten?custom_slug=my-page" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'

# С указанием длины
curl -X POST "http://localhost:8000/api/shorten?length=5" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

**Пример ответа (новая ссылка):**

```json
{
  "success": true,
  "cached": true,
  "message": "Ссылка успешно создана!",
  "data": {
    "slug": "my-page",
    "short_url": "http://localhost:8000/api/my-page",
    "long_url": "https://example.com/very/long/url",
    "is_new": true
  }
}
```

**Пример ответа (существующая ссылка):**

```json
{
  "success": true,
  "message": "Ссылка уже зарегистрирована в сервисе!",
  "data": {
    "slug": "existing-slug",
    "short_url": "http://localhost:8000/api/existing-slug",
    "long_url": "https://example.com/very/long/url",
    "is_new": false
  }
}
```

### 🚦 Переход по короткой ссылке

**Просто откройте в браузере:**
```
http://localhost:8000/api/{ваш_slug}
```
Вы будете автоматически перенаправлены на исходный URL.

### 📊 Получение статистики

**Эндпоинт:** `GET /api/info/{slug}`

```bash
curl http://localhost:8000/api/info/my-page
```

**Пример ответа:**

```json
{
  "success": true,
  "message": "Успешно найден!",
  "data": {
    "slug": "my-page",
    "short_url": "http://localhost:8000/api/my-page",
    "long_url": "https://example.com",
    "count_clicks": 13,
    "date_created": "2026-03-10"
  }
}
```

## 🛡️ Rate Limiting

API защищено интеллектуальной системой ограничения запросов для предотвращения злоупотреблений и DDoS-атак.

### Правила ограничений

| Эндпоинт | Лимит | Период |
|----------|-------|--------|
| `POST /api/shorten` | 10 запросов | 1 минута |
| `GET /api/info/*` | 20 запросов | 1 минута |
| `GET /api/{slug}` (редирект) | 30 запросов | 1 минута |
| Глобально (все эндпоинты) | 500 запросов | 1 час |

### Механизм работы

- При превышении лимита возвращается HTTP 429 (Too Many Requests)
- После 5 превышений пользователь блокируется на 1 час
- Блокировка снимается автоматически по истечении времени
- Redis используется для хранения счётчиков запросов

### Отключение rate limiting

Для нагрузочного тестирования rate limit можно отключить:

```bash
# Установите MODE=TEST в .env или передайте при запуске
MODE=TEST docker compose up -d --build
```

## 📁 Структура проекта

```
URL-Shortener/
├── backend/                        # FastAPI приложение
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini                  # Конфигурация pytest
│   ├── alembic.ini                 # Конфигурация Alembic
│   ├── migrations/                 # Миграции БД
│   │   ├── versions/               # Файлы миграций
│   │   ├── env.py                  # Конфигурация окружения
│   │   └── script.py.mako          # Шаблон миграций
│   ├── src/                        # Исходный код бэкенда
│   │   ├── api/                    # Эндпоинты API
│   │   │   ├── configuration.py
│   │   │   ├── dependencies.py
│   │   │   └── shortener.py
│   │   ├── core/                   # Ядро приложения
│   │   │   ├── config.py
│   │   │   ├── exceptions.py
│   │   │   ├── logging.py
│   │   │   └── redis.py
│   │   ├── db/                     # Работа с базой данных
│   │   │   ├── crud.py
│   │   │   ├── db.py
│   │   │   └── models.py
│   │   ├── schemas/                # Pydantic схемы
|   |   |   └── urls.py
|   |   └── services/               # Сервисы
│   │       ├── cache.py
│   │       ├── slug_generator.py
│   │       ├── url_checker.py
│   │       └── validators.py
│   └── tests/                      # Тесты
│       └── e2e/                    # e2e
│           │   └── test_workflow.py
│           ├── integration/        # Интеграционные тесты
│           │   ├── test_api_config.py
│           │   ├── test_api_info.py
│           │   ├── test_api_redirect.py
│           │   ├── test_api_shorten.py
│           │   └── test_rate_limit.py
│           ├── unit/               # Модульные тесты
│           │   ├── test_cache.py
│           │   ├── test_models.py
│           │   ├── test_url_checker.py
│           │   └── test_validators.py
│           ├── conftest.py
│           └── load_testing.py     # Нагрузочное тестирование
├── frontend/                       # Статические файлы веб-интерфейса
│   ├── assets/                     # Ресурсы (изображения, шрифты)
│   ├── css/
│   │   └── style.css               # Стили с анимациями и темами
│   ├── js/
│   │   ├── api.js                  # Модуль для работы с API
│   │   └── ui.js                   # Модуль для управления интерфейсом
│   ├── 404.html
│   ├── Dockerfile
│   ├── expired.html
│   └── index.html                  # Главная страница
├── .env.example                    # Пример конфигурации
├── docker-compose.yml              # Оркестрация всех сервисов
├── docker-compose.test.yml         # Тестовое окружение
└── README.md                       # Документация
```

## 🎨 Особенности интерфейса

- Анимированный градиентный фон с плавающими сферами
- Плавные анимации при наведении и взаимодействии
- Адаптивный дизайн для мобильных устройств
- Валидация форм в реальном времени с подсказками
- Уведомления (toast-сообщения) об успехе или ошибке
- Горячие клавиши — закрытие результата по Escape
- Автоматическая очистка URL от пробелов и лишних символов

## 🤝 Вклад в проект

Будем рады вашим идеям и улучшениям! Чтобы внести вклад:

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m '✨ Add some amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле LICENSE.
