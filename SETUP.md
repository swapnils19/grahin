# Local Development Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Git

## Step 1: Environment Setup

1. **Clone the repository** (already done):
   ```bash
   cd /home/swapnil/projects/rag-app
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Database Setup

1. **Install PostgreSQL** (if not already installed):
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```
   
   **macOS:**
   ```bash
   brew install postgresql
   brew services start postgresql
   ```
   
   **Windows:** Download from [postgresql.org](https://postgresql.org/download/windows/)

2. **Create database**:
   ```bash
   sudo -u postgres createdb grahin
   sudo -u postgres createuser --interactive
   # Create a user with same name as your system user
   ```

3. **Install Redis** (if not already installed):
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt install redis-server
   sudo systemctl start redis
   ```
   
   **macOS:**
   ```bash
   brew install redis
   brew services start redis
   ```

## Step 3: Environment Configuration

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your actual configuration:
   ```env
   # Database
   DATABASE_URL=postgresql://your_username:your_password@localhost:5432/grahin
   REDIS_URL=redis://localhost:6379/0

   # Claude API (get from https://console.anthropic.com/)
   CLAUDE_API_KEY=sk-ant-api03-your-actual-claude-api-key

   # JWT (generate a secure random string)
   SECRET_KEY=your-super-secret-random-string-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # File Storage
   UPLOAD_DIR=./uploads
   MAX_FILE_SIZE=50MB

   # Vector Store
   CHROMA_PERSIST_DIR=./chroma_db

   # Logging
   LOG_LEVEL=INFO
   ```

3. **Generate a secure SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

## Step 4: Database Initialization

1. **Create database tables**:
   ```bash
   python scripts/init_db.py
   ```

2. **Or use Alembic manually**:
   ```bash
   # Create initial migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migrations
   alembic upgrade head
   ```

## Step 5: Start Development Server

1. **Create necessary directories**:
   ```bash
   mkdir -p uploads chroma_db
   ```

2. **Start the application**:
   ```bash
   # Method 1: Using the provided script
   python scripts/start_dev.py
   
   # Method 2: Direct uvicorn command
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Verify the server is running**:
   - Open http://localhost:8000 in your browser
   - Check health endpoint: http://localhost:8000/health

## Step 6: Test the Application

1. **Register a new user**:
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "password123",
       "full_name": "Test User"
     }'
   ```

2. **Login to get token**:
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=password123"
   ```

3. **Upload a test file** (replace `YOUR_TOKEN`):
   ```bash
   curl -X POST "http://localhost:8000/api/files/upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test_document.pdf"
   ```

## Development Tools

### Code Quality

1. **Install development dependencies**:
   ```bash
   pip install black isort flake8 mypy pytest
   ```

2. **Code formatting**:
   ```bash
   black app/
   isort app/
   ```

3. **Linting**:
   ```bash
   flake8 app/
   mypy app/
   ```

### Testing

1. **Run tests**:
   ```bash
   pytest
   ```

2. **Run with coverage**:
   ```bash
   pytest --cov=app tests/
   ```

## Common Issues & Solutions

### Database Connection Issues

**Error**: `could not connect to server`
**Solution**: 
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database exists: `sudo -u postgres psql -l`
- Check connection string in `.env`

### Redis Connection Issues

**Error**: `Redis connection failed`
**Solution**:
- Check if Redis is running: `sudo systemctl status redis`
- Test connection: `redis-cli ping`

### Import Errors

**Error**: `ModuleNotFoundError`
**Solution**:
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### File Upload Issues

**Error**: `File too large`
**Solution**: Increase `MAX_FILE_SIZE` in `.env`

### Claude API Issues

**Error**: `Invalid API key`
**Solution**:
- Verify API key from Anthropic console
- Check `CLAUDE_API_KEY` in `.env`

## Development Workflow

1. **Make changes to code**
2. **Restart server** (auto-reload should handle this)
3. **Test changes**
4. **Format code**: `black app/ && isort app/`
5. **Run tests**: `pytest`
6. **Commit changes**: `git add . && git commit -m "Your message"`

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `CLAUDE_API_KEY` | Anthropic Claude API key | - |
| `SECRET_KEY` | JWT signing secret | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `UPLOAD_DIR` | File upload directory | `./uploads` |
| `MAX_FILE_SIZE` | Maximum file size | `50MB` |
| `CHROMA_PERSIST_DIR` | Vector store directory | `./chroma_db` |
| `LOG_LEVEL` | Logging level | `INFO` |

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Monitoring

- **Application logs**: Console output
- **Database logs**: PostgreSQL logs
- **Redis logs**: Redis logs

## Next Steps

1. Create a test user and upload some documents
2. Test the chat functionality
3. Explore the API documentation
4. Start building your frontend or integrate with other services
