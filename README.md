<div align="center">
  <h1>🔗 URL-Shortener</h1>
  <p><strong>Высокопроизводительный сервис для сокращения ссылок на FastAPI с современным веб-интерфейсом</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-14-336791?style=flat-square&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/Redis-7.2.4-DC382D?style=flat-square&logo=redis" alt="Redis">
    <img src="https://img.shields.io/badge/Docker-✓-2496ED?style=flat-square&logo=docker" alt="Docker">
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT">
    <img src="https://img.shields.io/badge/HTML5-CSS3-orange?style=flat-square&logo=html5" alt="HTML5/CSS3">
    <img src="https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=flat-square&logo=javascript" alt="JavaScript">
  </p>
</div>

## ✨ О проекте

**URL-Shortener** — это полностью контейнеризированный сервис для создания коротких ссылок, написанный на современном стеке технологий. Проект создан с упором на производительность, масштабируемость и удобство использования.

### Основные возможности:
- 🚀 **Мгновенные редиректы** благодаря кэшированию в Redis.
- 📊 **Детальная статистика** по каждой ссылке (количество переходов, дата создания).
- 🎨 **Современный веб-интерфейс** с анимированным фоном, поддержкой темной темы и адаптивным дизайном.
- ⚙️ **Гибкие настройки** — возможность задать свой вариант ссылки (custom slug) или выбрать её длину.
- 🐳 **Docker-first подход** — весь стек поднимается одной командой.

## 🛠 Стек технологий

| Компонент | Технология |
|-----------|------------|
| **Язык (Backend)** | [Python 3.12](https://www.python.org/) |
| **Веб-фреймворк (Backend)** | [FastAPI](https://fastapi.tiangolo.com/) |
| **База данных** | [PostgreSQL 14](https://www.postgresql.org/) + [SQLModel](https://sqlmodel.tiangolo.com/) (ORM) |
| **Кэш** | [Redis 7](https://redis.io/) |
| **Фронтенд** | HTML5, CSS3 (кастомные анимации), JavaScript (Vanilla) |
| **Контейнеризация** | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) |
| **Тестирование** | [Pytest](https://docs.pytest.org/) |

## 🚀 Быстрый старт

### Предварительные требования
- Установленные [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)

### Установка и запуск

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/kite-house/URL-Shortener.git
   cd URL-Shortener
Настройте переменные окружения

Скопируйте файл с примером конфигурации и отредактируйте его под себя:

bash
cp .env.example .env
Минимально необходимые настройки:

ini
MODE="DEV"

# PostgreSQL
DB_USER="postgres"
DB_PASS="postgres"
DB_HOST="backend_db"
DB_PORT="5432"
DB_NAME="url_shortener"

# Redis
REDIS_HOST="cache"
REDIS_PORT="6379"
Запустите все сервисы

bash
docker compose up -d --build
Проверьте работу

Веб-интерфейс: http://localhost:8000

Документация API (Swagger): http://localhost:8000/docs

📖 Использование
🌐 Веб-интерфейс
Главная страница сервиса предлагает интуитивно понятный интерфейс для работы со ссылками.

Функция	Описание
Сокращение ссылки	Вставьте длинную ссылку в поле ввода и нажмите кнопку "Сократить"
Свой вариант ссылки	Введите желаемую часть короткой ссылки (например, my-link)
Длина ссылки	Выберите длину генерируемой ссылки с помощью слайдера (от 3 до 10 символов)
Копирование	Скопируйте полученную короткую ссылку одним кликом
Темная тема	Переключайтесь между светлой и темной темой интерфейса
🔗 Создание короткой ссылки через API
Эндпоинт: POST /api/shorten

Параметры запроса:

url (обязательный) — исходный длинный URL

custom_slug (опционально) — желаемая кастомная часть

length (опционально) — желаемая длина генерируемой части

Примеры запросов (cURL):

bash
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
Пример ответа:

json
{
  "status_code": 200,
  "cached": True,
  "message": "Ссылка успешно создана!"
  "content": {
    "slug": "my-page",
    "short_url": "http://localhost:8000/api/my-page",
    "long_url": "https://example.com/very/long/url"
  }
}
🚦 Переход по короткой ссылке
Просто откройте в браузере:

text
http://localhost:8000/api/ваш_slug
Вы будете автоматически перенаправлены на исходный URL.

📊 Получение статистики
Эндпоинт: GET /api/info/{slug}

bash
curl http://localhost:8000/api/info/my-page
Пример ответа:

json
{
  status_code = 200,
  content = {
      "success" : True,
      "message" : "Успешно найден!",
      "data" : {
          "slug" : "my-page",
          "short_url" : f"http://localhost:8000/api/my-page",
          "long_url" : https://example.com,
          "count_clicks" : 13,
          "date_created" : "10.03.2026"
      } 
  }
🧪 Тестирование
Запуск тестов внутри Docker-контейнера:

bash
docker compose exec backend pytest -v
📁 Структура проекта
text
URL-Shortener/
├── .env.example                    # Пример конфигурации
├── docker-compose.yml              # Оркестрация всех сервисов
├── README.md                       # Документация
├── backend/                        # FastAPI приложение
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini                  # Конфигурация pytest
│   └── src/                        # Исходный код бэкенда
│       ├── api/                     # Эндпоинты API
│       │   ├── configuration.py
│       │   ├── dependencies.py
│       │   └── shortener.py
│       ├── core/                    # Ядро приложения
│       │   ├── config.py
│       │   ├── exceptions.py
│       │   └── redis.py
│       ├── db/                       # Работа с базой данных
│       │   ├── crud.py
│       │   ├── db.py
│       │   └── models.py
│       ├── schemas/                   # Pydantic схемы
│       ├── tests/                      # Тесты
│       │   ├── __init__.py
│       │   ├── test_data.py
│       │   ├── fixtures/                # Фикстуры для тестов
│       │   │   ├── client_fixtures.py
│       │   │   ├── db_fixtures.py
│       │   │   └── redis_fixtures.py
│       │   ├── integration/              # Интеграционные тесты
│       │   │   └── test_api.py
│       │   └── unit/                      # Модульные тесты
│       │       └── test_slug_generator.py
│       └── utils/                         # Вспомогательные модули
│           ├── helpers.py
│           └── conflict.py
├── frontend/                               # Статические файлы веб-интерфейса
│   ├── assets/                              # Ресурсы (изображения, шрифты)
│   ├── css/
│   │   └── style.css                        # Стили с анимациями и темами
│   ├── js/
│   │   ├── api.js                           # Модуль для работы с API
│   │   └── ui.js                            # Модуль для управления интерфейсом
│   ├── Dockerfile
│   └── index.html                           # Главная страница

🎨 Особенности интерфейса
Анимированный градиентный фон с плавающими сферами

Плавные анимации при наведении и взаимодействии

Адаптивный дизайн для мобильных устройств

Валидация форм в реальном времени с подсказками

Уведомления (toast-сообщения) об успехе или ошибке

Горячие клавиши — закрытие результата по Escape

🤝 Вклад в проект
Будем рады вашим идеям и улучшениям! Чтобы внести вклад:

Форкните репозиторий

Создайте ветку для фичи (git checkout -b feature/amazing-feature)

Закоммитьте изменения (git commit -m '✨ Add some amazing feature')

Запушьте ветку (git push origin feature/amazing-feature)

Откройте Pull Request

📄 Лицензия
Проект распространяется под лицензией MIT. Подробности в файле LICENSE.

📬 Контакты
Автор: kite-house
GitHub: @kite-house

<div align="center"> ⭐ Если проект оказался полезным, не забудьте поставить звезду! <br><br> <sub>Сделано с ❤️ для сообщества</sub> </div> ```
