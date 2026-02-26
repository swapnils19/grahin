#!/bin/bash

# Grahin RAG Application - Development Setup Script
# This script automates the local development setup

set -e

echo "🚀 Setting up Grahin RAG Application for local development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.12+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.12" | bc -l) -eq 1 ]]; then
            print_status "Python $PYTHON_VERSION found ✓"
        else
            print_error "Python 3.12+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.12+"
        exit 1
    fi
}

# Check if Poetry is installed
check_poetry() {
    print_status "Checking Poetry installation..."
    if command -v poetry &> /dev/null; then
        print_status "Poetry found ✓"
    else
        print_error "Poetry not found. Please install Poetry:"
        echo "curl -sSL https://install.python-poetry.org | python3 -"
        exit 1
    fi
}

# Install dependencies with Poetry
install_dependencies() {
    print_status "Installing dependencies with Poetry..."
    poetry install
    print_status "Dependencies installed ✓"
}

# Check PostgreSQL
check_postgresql() {
    print_status "Checking PostgreSQL..."
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL found ✓"
    else
        print_warning "PostgreSQL not found. Please install PostgreSQL 13+"
        echo "Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
        echo "macOS: brew install postgresql"
        echo "Windows: Download from https://postgresql.org/download/windows/"
    fi
}

# Check Redis
check_redis() {
    print_status "Checking Redis..."
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            print_status "Redis is running ✓"
        else
            print_warning "Redis is installed but not running"
            echo "Start Redis: sudo systemctl start redis"
        fi
    else
        print_warning "Redis not found. Please install Redis 6+"
        echo "Ubuntu/Debian: sudo apt install redis-server"
        echo "macOS: brew install redis"
    fi
}

# Setup environment file
setup_env() {
    print_status "Setting up environment file..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status ".env file created from template ✓"

        # Generate secure secret key
        SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
        sed -i "s/your_super_secret_key_here/$SECRET_KEY/" .env
        print_status "Generated secure SECRET_KEY ✓"

        print_warning "Please edit .env file with your actual configuration:"
        echo "- DATABASE_URL: PostgreSQL connection string"
        echo "- CLAUDE_API_KEY: Your Anthropic Claude API key"
        echo "- REDIS_URL: Redis connection string"
    else
        print_warning ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p uploads chroma_db
    print_status "Directories created ✓"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    if [ -f ".env" ]; then
        poetry run python scripts/init_db.py
        print_status "Database initialized ✓"
    else
        print_warning "Please configure .env file first"
    fi
}

# Main setup process
main() {
    echo "Grahin RAG Application - Development Setup"
    echo "=========================================="

    check_python
    check_poetry
    install_dependencies
    check_postgresql
    check_redis
    setup_env
    create_directories

    echo ""
    print_status "Setup completed! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your actual configuration"
    echo "2. Make sure PostgreSQL and Redis are running"
    echo "3. Initialize database: poetry run python scripts/init_db.py"
    echo "4. Start development server: poetry run python scripts/start_dev.py"
    echo ""
    echo "Application will be available at: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo ""
    print_warning "Don't forget to:"
    echo "- Set your CLAUDE_API_KEY in .env"
    echo "- Configure DATABASE_URL for your PostgreSQL instance"
    echo "- Configure REDIS_URL for your Redis instance"
}

# Run the setup
main
