<div align="center">
  <h1>🔗 URL-Shortener</h1>
  <p><strong>Высокопроизводительный сервис для сокращения ссылок на FastAPI</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-14-336791?style=flat-square&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/Redis-7.2.4-DC382D?style=flat-square&logo=redis" alt="Redis">
    <img src="https://img.shields.io/badge/Docker-✓-2496ED?style=flat-square&logo=docker" alt="Docker">
    <img src="https://img.shields.io/badge/Aiogram-3.17.1-2CA5E0?style=flat-square&logo=telegram" alt="Aiogram">
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT">
  </p>
</div>

## ✨ О проекте

**URL-Shortener** — это полностью контейнеризированный сервис для создания коротких ссылок, написанный на современном стеке технологий. Проект создан с упором на производительность, масштабируемость и простоту развертывания.

Основные возможности:
- 🚀 **Мгновенные редиректы** благодаря кэшированию в Redis.
- 📊 **Детальная статистика** по каждой ссылке (количество переходов, дата создания).
- 🤖 **Telegram-бот** для создания коротких ссылок прямо из мессенджера.
- 🐳 **Docker-first подход** — весь стек поднимается одной командой.

## 🛠 Стек технологий

| Компонент       | Технология                                                                 |
|-----------------|----------------------------------------------------------------------------|
| **Язык**        | [Python 3.12](https://www.python.org/)                                    |
| **Веб-фреймворк** | [FastAPI](https://fastapi.tiangolo.com/)                                 |
| **База данных** | [PostgreSQL 14](https://www.postgresql.org/) + [SQLModel](https://sqlmodel.tiangolo.com/) (ORM) |
| **Кэш**         | [Redis 7](https://redis.io/)                                              |
| **Telegram Bot**| [Aiogram 3](https://docs.aiogram.dev/)                                    |
| **Контейнеризация** | [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) |
| **Тестирование**| [Pytest](https://docs.pytest.org/)                                        |

## 🚀 Быстрый старт

### Предварительные требования
- Установленные [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)
- (Опционально) Токен Telegram-бота от [@BotFather](https://t.me/botfather)

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
   
   # Telegram Bot (если нужен)
   TELEGRAM_TOKEN="ваш_токен_от_botfather"
   ```

3. **Запустите все сервисы**
   ```bash
   docker compose up -d --build
   ```

4. **Проверьте работу**
   - API сервис: [http://localhost:8000](http://localhost:8000)
   - Документация Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Telegram бот (если настроен): напишите `/start` вашему боту

## 📖 Использование

### 🔗 Создание короткой ссылки

#### Через API (cURL)
```bash
curl -X POST "http://localhost:8000/api/cutback" \
  -H "Content-Type: application/json" \
  -d '{"target_url": "https://example.com/very/long/url"}'
```

**Пример ответа:**
```json
{
  "slug": "aB3dE1f",
  "long_url": "https://example.com/very/long/url"
}
```

#### Через Telegram-бот
Отправьте боту команду:
```
/cutback https://example.com/very/long/url
```

### 🚦 Переход по короткой ссылке
Просто откройте в браузере:
```
http://localhost:8000/aB3dE1f
```
Вы будете автоматически перенаправлены на исходный URL.

### 📊 Получение статистики
Информация о конкретной ссылке доступна по эндпоинту `/info/{slug}`:
```bash
curl http://localhost:8000/api/info/aB3dE1f
```

**Пример ответа:**
```json
{
  "slug": "aB3dE1f",
  "long_url": "https://example.com/very/long/url",
  "count_clicks": 42,
  "date_created": "2026-02-28T10:30:00"
}
```

## 🧪 Тестирование

Запуск тестов внутри Docker-контейнера:
```bash
docker compose exec backend pytest -v
```

## 📁 Структура проекта

```
URL-Shortener/
├── .env.example          # Пример конфигурации
├── docker-compose.yml    # Оркестрация сервисов
├── backend/              # FastAPI приложение
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       └── app/
├── telegram_bot/         # Telegram бот на Aiogram
│   ├── Dockerfile
│   ├── requirements.txt
│   └── bot.py
└── README.md
```

## 🤝 Вклад в проект

Будем рады вашим идеям и улучшениям! Чтобы внести вклад:
1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m '✨ Add some amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## 📬 Контакты

Автор: **kite-house**  
GitHub: [@kite-house](https://github.com/kite-house)

---

<div align="center">
  ⭐ Если проект оказался полезным, не забудьте поставить звезду!
</div>


