FROM python:3.13-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY src/ ./src/

# Порт для FastAPI
EXPOSE 8000

# Запуск бэкенда
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "auto"]
