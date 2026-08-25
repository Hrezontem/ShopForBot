# ShopForBot

> ⚠️ **Work In Progress**: This project is under active development. Features and database schemas may change.

A Telegram e-commerce bot powered by a Django backend and PostgreSQL, containerized with Docker and using `uv` for dependency management.

---

## 🛠 Tech Stack
- **Python**: 3.14
- **Backend**: Django 6.1+ (with Jazzmin admin)
- **Bot**: aiogram 3.x
- **Database**: PostgreSQL 15
- **Tooling**: Docker, Docker Compose, `uv`

---

## 🚀 Quick Start (Docker)

### 1. Environment Setup
Copy the environment template and fill in your database credentials:
```bash
cp .env.example .env
```
*(Edit `.env` and set a secure `POSTGRES_PASSWORD`)*

### 2. Start Services
Build and run the containers in the background:
```bash
docker compose up --build -d
```

### 3. Initialize Database
Apply migrations and create an admin user:
```bash
docker compose exec django uv run python back/manage.py migrate
docker compose exec django uv run python back/manage.py createsuperuser
```

---

## 🤖 Bot Configuration (Critical)

The bot token is **not** stored in `.env`. It is read directly from the PostgreSQL database via Django. 

**To make the bot work, follow these exact steps:**

1. **Get a Token**: Message [@BotFather](https://t.me/BotFather) on Telegram, create a new bot, and copy the API token.
2. **Add to Database**: 
   - Go to [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - Log in with your superuser credentials.
   - Navigate to the Bot Configuration model and add your token.
   - Save the changes.
3. **Restart the Bot**: The bot container **must** be restarted to read the new token from the database:
   ```bash
   docker compose restart bot
   ```
4. **Verify**: Check the logs to ensure it connected successfully:
   ```bash
   docker compose logs -f bot
   ```
   *(You should see "Bot started successfully" or similar polling messages).*

---

## 🔧 Essential Commands

| Command | Description |
|---------|-------------|
| `docker compose up --build -d` | Build and start all services in background |
| `docker compose down` | Stop and remove all containers |
| `docker compose restart bot` | Restart bot (required after changing token in DB) |
| `docker compose logs -f bot` | View real-time bot logs |
| `docker compose exec django bash` | Open shell inside Django container |

---

## ⚠️ Common Issues

**Bot doesn't respond after adding the token**  
→ You forgot to restart the bot container. Run: `docker compose restart bot`.

**`FileNotFoundError` when sending images**  
→ Linux (Docker) is case-sensitive. Ensure the filename in your code exactly matches the file on disk (e.g., `menu.png`, not `Menu.PNG`). Always use absolute paths via Django settings:  
`Path(settings.MEDIA_ROOT) / 'bot' / 'menu.png'`

**`ModuleNotFoundError: No module named 'core'`**  
→ Ensure `PYTHONPATH=/app/back` is set in the `bot` service environment in `docker-compose.yml`.

---

## 📂 Project Structure
```text
ShopForBot/
├── back/               # Django app (core settings, manage.py, media)
├── bot/                # aiogram bot (handlers, middleware, bot.py)
├── docker-compose.yml  # Container orchestration
├── pyproject.toml      # Unified dependencies
└── .env.example        # Environment template
```
```

### Accompanying Files (Keep them minimal)

**`.env.example`**
```env
POSTGRES_DB=shopforbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_SETTINGS_MODULE=core.settings
```

**`.gitignore`**
```text
.venv/
__pycache__/
*.pyc
.env
media/
staticfiles/
.vscode/
.idea/
.DS_Store
```

This version is clean, direct, and ensures anyone (including your future self) knows exactly what to do to get the bot running, especially the critical "add token -> restart bot" step.
