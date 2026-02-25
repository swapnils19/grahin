#!/bin/bash

# Grahin RAG Application - WSL Ubuntu Setup Script
# Fixes externally-managed-environment issues

set -e

echo "🔧 Setting up Grahin RAG Application for WSL Ubuntu..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_status "Python $PYTHON_VERSION found ✓"
        
        # Check if it's externally managed
        if python3 -m pip --version 2>&1 | grep -q "externally-managed-environment"; then
            print_warning "Python environment is externally managed"
            return 1
        else
            print_status "Python environment is not externally managed ✓"
            return 0
        fi
    else
        print_error "Python 3 not found"
        exit 1
    fi
}

# Solution 1: Create virtual environment
create_venv() {
    print_status "Creating virtual environment (Solution 1)..."
    
    # Remove existing venv if it exists
    if [ -d "venv" ]; then
        print_warning "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create new virtual environment
    python3 -m venv venv
    print_status "Virtual environment created ✓"
    
    # Activate and install
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    print_status "Dependencies installed in virtual environment ✓"
    
    print_status "To activate the virtual environment in the future, run:"
    echo "source venv/bin/activate"
}

# Solution 2: Use pipx (alternative)
install_with_pipx() {
    print_status "Installing with pipx (Solution 2)..."
    
    # Install pipx if not present
    if ! command -v pipx &> /dev/null; then
        print_status "Installing pipx..."
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
        
        # Add pipx to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    print_status "Installing packages with pipx..."
    # Note: pipx is for isolated applications, not libraries
    # This is just for demonstration
}

# Solution 3: Use --user flag
install_user_packages() {
    print_status "Installing packages with --user flag (Solution 3)..."
    
    python3 -m pip install --user -r requirements.txt
    print_status "Packages installed in user space ✓"
    
    print_warning "Add ~/.local/bin to your PATH:"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
}

# Solution 4: Use system package manager
install_system_packages() {
    print_status "Installing system packages (Solution 4)..."
    
    # Update package list
    sudo apt update
    
    # Install Python packages via apt (limited availability)
    sudo apt install -y \
        python3-fastapi \
        python3-uvicorn \
        python3-sqlalchemy \
        python3-psycopg2 \
        python3-redis \
        python3-pil \
        python3-pypdf2
    
    print_status "System packages installed ✓"
    print_warning "Not all packages are available via apt. Some may need pip install."
}

# Solution 5: Configure pip to ignore external management
configure_pip() {
    print_status "Configuring pip to ignore external management (Solution 5)..."
    
    # Create pip configuration directory
    mkdir -p ~/.config/pip
    
    # Add configuration to ignore external management
    cat >> ~/.config/pip/pip.conf << EOF
[global]
break-system-packages = true
EOF
    
    print_status "Pip configured ✓"
    print_warning "This allows pip to install packages system-wide"
    print_warning "Use with caution as it may conflict with system packages"
}

# Main menu
main() {
    echo "Grahin RAG Application - WSL Ubuntu Setup"
    echo "=========================================="
    echo ""
    echo "The 'externally-managed-environment' error occurs because"
    echo "newer Python versions prevent pip from modifying system packages."
    echo ""
    echo "Choose a solution:"
    echo ""
    echo "1) Virtual Environment (RECOMMENDED)"
    echo "2) Use --user flag"
    echo "3) Configure pip to ignore external management"
    echo "4) Install system packages (limited)"
    echo "5) Show manual fix instructions"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            create_venv
            ;;
        2)
            install_user_packages
            ;;
        3)
            configure_pip
            python3 -m pip install -r requirements.txt
            ;;
        4)
            install_system_packages
            ;;
        5)
            echo ""
            echo "Manual Fix Instructions:"
            echo "======================"
            echo ""
            echo "Option A: Virtual Environment (Best)"
            echo "  python3 -m venv venv"
            echo "  source venv/bin/activate"
            echo "  pip install -r requirements.txt"
            echo ""
            echo "Option B: User Installation"
            echo "  python3 -m pip install --user -r requirements.txt"
            echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
            echo ""
            echo "Option C: Force System Installation"
            echo "  python3 -m pip install --break-system-packages -r requirements.txt"
            echo ""
            echo "Option D: Configure Pip"
            echo "  mkdir -p ~/.config/pip"
            echo "  echo '[global]' > ~/.config/pip/pip.conf"
            echo "  echo 'break-system-packages = true' >> ~/.config/pip/pip.conf"
            echo "  python3 -m pip install -r requirements.txt"
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    print_status "Setup completed! 🎉"
    
    if [ "$choice" = "1" ]; then
        echo ""
        echo "Next steps:"
        echo "1. Activate virtual environment: source venv/bin/activate"
        echo "2. Configure .env file"
        echo "3. Initialize database: python scripts/init_db.py"
        echo "4. Start server: python scripts/start_dev.py"
    fi
}

# Check environment first
if check_python; then
    echo "No external management detected. Proceeding with normal setup..."
    python3 -m pip install -r requirements.txt
else
    main
fi
