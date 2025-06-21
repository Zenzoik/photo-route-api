# 📸 Photo Route Mapper

> **Live Demo:** [zenzoik.fun](https://zenzoik.fun)

Веб-приложение для автоматического построения интерактивных маршрутов из фотографий с GPS-данными. Загружайте фото с геолокацией — система автоматически извлечет координаты из EXIF и построит ваш маршрут на карте.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-zenzoik.fun-brightgreen)](https://zenzoik.fun)
![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Быстрый старт

### Предварительные требования

- [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)
- Git

### Установка и запуск

```bash
# 1. Клонирование репозитория
git clone https://github.com/Zenzoik/photo-route-api.git
cd photo-route-api

# 2. Настройка окружения
cp .env.example .env

# 3. Запуск приложения
docker-compose up -d

# 4. Проверка работоспособности
curl http://localhost:8080/
```

**🎉 Готово!** Приложение доступно на http://localhost:8080

### Первое использование

1. Откройте http://localhost:8080 в браузере
2. Перетащите или выберите фотографии с GPS-данными
3. Нажмите "Загрузить фото"
4. Перейдите на "Посмотреть маршрут" для просмотра карты

## ✨ Основные возможности

- 🗺️ **Автоматическое построение маршрутов** из GPS-координат фотографий
- 📷 **Поддержка популярных форматов**: JPEG, HEIC с автоматическим извлечением EXIF
- 🖼️ **Интерактивная карта** с маркерами и превью фотографий
- 🔗 **Шаринг маршрутов** через уникальные ссылки
- 📱 **Адаптивный интерфейс** с drag & drop загрузкой
- 🐳 **Полная контейнеризация** для простого развертывания

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Database     │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │───▶│ • FastAPI       │───▶│ • PostgreSQL    │
│ • Leaflet Maps  │    │ • Python 3.11   │    │ • PostGIS       │
│ • Drag & Drop   │    │ • Async/Await   │    │ • Spatial Data  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ File Processing │
                       │                 │
                       │ • EXIF Parser   │
                       │ • GPS Extract   │
                       │ • Image Convert │
                       └─────────────────┘
```

### Технический стек

**Backend:**
- **[FastAPI](https://fastapi.tiangolo.com/)** - современный async веб-фреймворк
- **[SQLAlchemy 2.0](https://sqlalchemy.org/)** - асинхронная ORM
- **[PostgreSQL](https://postgresql.org/) + [PostGIS](https://postgis.net/)** - пространственная база данных
- **[Pillow](https://pillow.readthedocs.io/) + piexif** - обработка изображений
- **[Alembic](https://alembic.sqlalchemy.org/)** - миграции базы данных

**Frontend:**
- **[Leaflet.js](https://leafletjs.com/)** - интерактивные карты
- **Vanilla JavaScript** - без дополнительных фреймворков
- **Responsive CSS** - адаптивный дизайн

**DevOps:**
- **[Docker](https://docker.com/) + Compose** - контейнеризация
- **[Uvicorn](https://uvicorn.org/)** - ASGI сервер

## 📱 Использование

### 1. Загрузка фотографий

<img src="docs/upload-demo.gif" alt="Загрузка фотографий" width="600">

1. Перейдите на главную страницу (http://localhost:8080)
2. Перетащите фотографии в область загрузки или нажмите для выбора
3. Убедитесь, что фотографии содержат GPS-данные
4. Нажмите "Загрузить фото"

### 2. Просмотр маршрута

<img src="docs/map-demo.gif" alt="Просмотр маршрута" width="600">

1. После загрузки нажмите "Посмотреть маршрут"
2. На карте отобразятся точки вашего маршрута
3. Кликните на маркеры для просмотра фотографий
4. Используйте кнопку "Поделиться маршрутом" для создания публичной ссылки

### 3. Управление фотографиями

- **Просмотр всех фото**: кнопка "Показать фото"
- **Удаление конкретного фото**: крестик на миниатюре
- **Очистка всех фото**: кнопка "Удалить мои фото"

## 🔌 API Документация

После запуска доступна автоматическая документация:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/uploadfiles/` | Загрузка нескольких фотографий |
| `GET` | `/api/v1/photos/` | Список фотографий пользователя |
| `GET` | `/api/v1/route/` | Получение маршрута |
| `GET` | `/api/v1/shared_route/{token}` | Публичный доступ к маршруту |
| `DELETE` | `/api/v1/photos/{id}` | Удаление фотографии |

### Пример API запроса

```bash
# Загрузка фотографий
curl -X POST "http://localhost:8080/api/v1/uploadfiles/" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg"

# Получение маршрута
curl -H "Cookie: session_token=your-session-token" \
  "http://localhost:8080/api/v1/route/"
```

## 📁 Структура проекта

```
photo-route-api/
├── app/                     # Основное приложение
│   ├── api/v1/             # API эндпоинты
│   │   └── upload.py       # Загрузка и управление фото
│   ├── crud/               # Операции с базой данных
│   │   └── photo.py        # CRUD для фотографий
│   ├── db/                 # Конфигурация БД
│   │   ├── models.py       # SQLAlchemy модели
│   │   └── session.py      # Управление сессиями
│   ├── schemas/            # Pydantic схемы
│   │   └── photo.py        # Схемы для API
│   ├── services/           # Бизнес-логика
│   │   └── exif_service.py # Обработка EXIF данных
│   └── main.py             # Точка входа приложения
├── static/                 # Статические файлы
│   ├── css/               # Стили
│   └── js/                # JavaScript
├── templates/             # HTML шаблоны
├── uploads/               # Загруженные файлы (создается автоматически)
├── docker-compose.yml     # Docker конфигурация
├── Dockerfile            # Docker образ
└── requirements.txt      # Python зависимости
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```bash
# Основные настройки
DATABASE_URL=postgresql+asyncpg://photo_user:photo-map@db:5432/photo_route

# Дополнительные параметры (опционально)
MAX_UPLOAD_SIZE=10485760  # Максимальный размер файла (10MB)
DEBUG=false              # Режим отладки
CORS_ORIGINS=*           # CORS политика
```

### Настройка для production

Для production развертывания создайте `.env.prod`:

```bash
DATABASE_URL=postgresql+asyncpg://your_user:secure_password@db:5432/photo_route_prod
DEBUG=false
CORS_ORIGINS=https://your-domain.com
```

## 🧪 Тестирование

### Проверка работоспособности

```bash
# Статус контейнеров
docker-compose ps

# Логи приложения
docker-compose logs web

# Проверка API
curl http://localhost:8080/health

# Тест базы данных
docker-compose exec db psql -U photo_user -d photo_route -c "\dt"
```

### Отладка

```bash
# Просмотр логов в реальном времени
docker-compose logs -f

# Подключение к контейнеру
docker-compose exec web bash

# Проверка переменных окружения
docker-compose exec web env | grep DATABASE
```

## 🔧 Разработка

### Запуск в режиме разработки

```bash
# Клонирование для разработки
git clone https://github.com/Zenzoik/photo-route-api.git
cd photo-route-api

# Установка зависимостей (опционально, для IDE)
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Запуск с автоперезагрузкой
docker-compose up --build
```

### Создание миграций

```bash
# Создание новой миграции
docker-compose exec web alembic revision --autogenerate -m "Description"

# Применение миграций
docker-compose exec web alembic upgrade head
```

## 🌟 Особенности реализации

### Обработка изображений
- **Асинхронная обработка** EXIF данных без блокировки I/O
- **Поддержка HEIC** формата с автоконвертацией в JPEG
- **Валидация GPS** координат и временных меток
- **Оптимизация памяти** при обработке больших файлов

### Геопространственные возможности
- **PostGIS индексы** для быстрого поиска по координатам
- **Автоматическая маршрутизация** между точками по времени
- **Расчет расстояний** на уровне базы данных
- **Spatial queries** для кластеризации близких точек

### Архитектурные решения
- **Session-based** аутентификация через cookies
- **Async/await** архитектура для высокой производительности
- **Repository pattern** для абстракции работы с данными
- **Dependency injection** через FastAPI

## 🚀 Production Deployment

Для развертывания в production среде смотрите подробное руководство в [DEPLOYMENT.md](DEPLOYMENT.md).

Краткие шаги:
1. Настройте VPS с Docker
2. Получите SSL сертификаты
3. Настройте Nginx reverse proxy
4. Используйте `docker-compose.prod.yml`

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📋 Требования к фотографиям

- **Формат**: JPEG, JPG, HEIC
- **Размер**: до 10MB на файл
- **GPS данные**: обязательны (встроены в EXIF)
- **Время съемки**: автоматически извлекается из EXIF

## 🐛 Известные ограничения

- Фотографии без GPS-данных игнорируются
- Поддерживаются только современные браузеры (ES6+)
- Максимум 50 фотографий за один upload
- Session-based авторизация (без постоянных аккаунтов)

## 📊 Производительность

- **Startup time**: ~3 секунды
- **Upload speed**: 10MB файл ~2 секунды
- **Map rendering**: 100 точек ~500ms
- **Database**: поддержка 10k+ фотографий на сессию

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## 🙏 Благодарности

- [OpenStreetMap](https://www.openstreetmap.org/) за картографические данные
- [Leaflet](https://leafletjs.com/) за библиотеку интерактивных карт
- [FastAPI](https://fastapi.tiangolo.com/) за отличный веб-фреймворк

---

**Автор**: [Zenzoik](https://github.com/Zenzoik)  
**Live Demo**: [zenzoik.fun](https://zenzoik.fun)  
**Создано**: 2024

⭐ Поставьте звездочку, если проект оказался полезным!