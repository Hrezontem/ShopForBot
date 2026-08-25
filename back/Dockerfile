# D:\Projects\ShopForBot\back\Dockerfile
FROM python:3.14-slim

# Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Копируем только корневой pyproject.toml и uv.lock
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости
RUN uv sync --no-dev --no-install-project

# Копируем весь проект
COPY . .

EXPOSE 8000

# Запускаем manage.py из папки back
CMD ["uv", "run", "python", "back/manage.py", "runserver", "0.0.0.0:8000"]
