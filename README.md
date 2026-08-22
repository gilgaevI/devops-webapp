# DevOps WebApp

Небольшой pet-проект, который я делал для практики DevOps.

В проекте есть Flask backend, PostgreSQL и Nginx.
Запускается всё через Docker Compose.

Также настроил CI/CD через GitHub Actions и публикацию Docker image в GitHub Container Registry.

## Что используется

- Python / Flask
- PostgreSQL
- Docker
- Docker Compose
- Nginx
- Bash
- Git
- GitHub Actions
- GitHub Container Registry
- SQL
- YAML

## Как устроен проект

Примерная схема:

GitHub
   |
   v
GitHub Actions
   |
   +--> Tests
   |
   +--> Docker build
   |
   +--> Push image to GHCR
   |
   v
Docker Compose
   |
   +--> Nginx
   |
   +--> Flask
   |
   +--> PostgreSQL


Nginx принимает HTTP запросы и передаёт их Flask backend.

Flask работает с PostgreSQL.


## Что умеет API

### GET /health

Проверяет, что backend работает.

### GET /db

Проверяет подключение к PostgreSQL.

### GET /servers

Возвращает список серверов.

### POST /servers

Создаёт новый сервер.

Пример:

```json
{
  "name": "web01",
  "status": "up",
  "cpu": 70,
  "ram": 4096
}
