# AI RAG Application

A production-ready AI-powered RAG (Retrieval-Augmented Generation) application with user authentication and multi-tenant file management.

## Features

- **User Authentication**: Secure JWT-based authentication with user registration and login
- **File Management**: Upload and manage files (PDF, DOCX, TXT, images) with user isolation
- **RAG Functionality**: Ask questions about your uploaded documents using Claude LLM
- **Vector Search**: Semantic search across your document collection
- **Conversation History**: Persistent chat conversations with context
- **Production Ready**: Docker containerization with PostgreSQL and Redis

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Authentication**: JWT, bcrypt, OAuth2
- **AI/ML**: LangChain, Claude LLM, ChromaDB
- **Database**: PostgreSQL, Redis
- **File Processing**: Pillow, PyPDF2, python-docx
- **Infrastructure**: Docker, Nginx, Uvicorn

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Claude API key
- Python 3.11+ (for local development)

### Environment Setup

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_app
REDIS_URL=redis://localhost:6379/0
CLAUDE_API_KEY=your_claude_api_key_here
SECRET_KEY=your_super_secret_key_here
```

### Docker Deployment

1. Build and start the application:
```bash
docker-compose up --build
```

2. The application will be available at `http://localhost`

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL and Redis instances

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Files
- `POST /api/files/upload` - Upload file
- `GET /api/files/` - List user files
- `GET /api/files/{file_id}` - Get file details
- `DELETE /api/files/{file_id}` - Delete file

### Chat & Search
- `POST /api/chat/chat` - Send chat message
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}` - Get conversation
- `DELETE /api/chat/conversations/{id}` - Delete conversation
- `GET /api/chat/search` - Search documents
- `GET /api/chat/files-summary` - Get files summary

## Usage Example

1. Register a user:
```bash
curl -X POST "http://localhost/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}'
```

2. Login:
```bash
curl -X POST "http://localhost/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

3. Upload a file:
```bash
curl -X POST "http://localhost/api/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

4. Chat with your documents:
```bash
curl -X POST "http://localhost/api/chat/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the main topic of the uploaded document?"}'
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (Web/Mobile)  │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ChromaDB      │
                       │   Vector Store  │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Claude LLM    │
                       │   (Anthropic)   │
                       └─────────────────┘
```

## Security Features

- JWT-based authentication with secure token handling
- Password hashing with bcrypt
- User data isolation (multi-tenancy)
- File upload validation and size limits
- CORS configuration
- Environment variable management

## Monitoring & Logging

- Structured logging with `structlog`
- Health check endpoint at `/health`
- Ready for Prometheus/Grafana integration

## Development

### Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Add new feature"
```

Apply migrations:
```bash
alembic upgrade head
```

### Testing

Run tests:
```bash
pytest
```

## Production Deployment

1. Configure environment variables
2. Set up PostgreSQL and Redis clusters
3. Configure SSL certificates
4. Set up monitoring and logging
5. Configure backup strategies
6. Scale with load balancers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
