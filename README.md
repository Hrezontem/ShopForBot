# 🛒 ShopForBot

![Status: Work In Progress](https://img.shields.io/badge/Status-Work%20In%20Progress-yellow)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

> ⚠️ **DISCLAIMER: This project is currently under active development.**  
> Features, database schemas, and API endpoints are subject to change without notice. It is not yet ready for production use.

**ShopForBot** is a Telegram-based e-commerce bot powered by a robust Django backend. It is designed to provide a seamless shopping experience through Telegram, managed via a comprehensive Django administration panel. The project is containerized with Docker and utilizes the modern, ultra-fast `uv` package manager for dependency resolution.

---

## 🛠 Technology Stack

- **Language**: Python 3.14
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (for blazing-fast dependency management)
- **Backend Framework**: Django 6.1+ 
  - `django-jazzmin` (Enhanced admin UI)
  - `django-phonenumber-field` (Phone number validation)
- **Telegram Bot Framework**: `aiogram` 3.x (Async Python bot library)
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **Environment Management**: `.env` files via `python-dotenv`

---

## 📂 Project Structure

The project follows a monorepo-style structure with a single `pyproject.toml` managing dependencies for both the backend and the bot.

```text
ShopForBot/
├── back/                   # Django Backend Application
│   ├── core/               # Project settings (settings.py, urls.py, wsgi.py)
│   ├── media/              # User-uploaded media files (e.g., product images)
│   └── manage.py           # Django command-line utility
├── bot/                    # Telegram Bot Application (aiogram)
│   ├── handlers/           # Command and message handlers (e.g., /start, /cart)
│   ├── middleware/         # Custom middleware (logging, state management)
│   └── bot.py              # Bot entry point and initialization script
├── docker-compose.yml      # Docker orchestration configuration
├── pyproject.toml          # Unified dependency manifest for the entire project
├── uv.lock                 # Locked dependency versions for reproducible builds
├── .env.example            # Template for environment variables
└── README.md               # This file
