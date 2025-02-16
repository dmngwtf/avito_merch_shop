# Avito Merch Shop

## 1. Запуск проекта

```sh
git clone https://dmngwtf/your-project.git
docker-compose up --build -d
```
Приложение доступно по адресу: [http://localhost:8000](http://localhost:8000)

## 2. Локальный запуск (без Docker)
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 3. Тестирование

### Юнит, интеграционные и E2E тесты
```sh
pytest --maxfail=1 --disable-warnings
```
### Покрытие кода
```sh
pip install coverage
coverage run --source=app -m pytest
coverage report -m
```

## 4. Нагрузочное тестирование (Locust)
```sh
pip install locust
locust -f locustfile.py --host http://localhost:8000
```

## 5. Структура проекта
- **app/** – код FastAPI
- **tests/** – тесты (юнит, интеграция, E2E)
- **locustfile.py** – сценарии нагрузочного тестирования
- **Dockerfile** – сборка контейнера
- **docker-compose.yml** – конфигурация сервисов


