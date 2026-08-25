# D:\Projects\ShopForBot\bot\Dockerfile
FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Копируем зависимости
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# Копируем весь проект
COPY . .

# Бот не открывает порты, поэтому EXPOSE не нужен
CMD ["uv", "run", "python", "bot/bot.py"]
