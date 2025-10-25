#!/bin/bash
# Quick Start Script for BJJ CRM System
# Usage: ./quick_start.sh

set -e

echo "🥋 BJJ Academy CRM System - Quick Start"
echo "========================================"

# Colors
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

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the bjj_crm directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(echo "$python_version < 3.9" | bc -l)" -eq 1 ]; then
    print_error "Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

print_status "Python version: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Check if database exists
if [ ! -f "bjj_crm.db" ]; then
    print_status "Initializing database with sample data..."
    python scripts/init_db.py
else
    print_warning "Database already exists. Skipping initialization."
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration before running the application"
fi

print_status "🎉 Setup completed successfully!"
echo ""
print_status "Next steps:"
echo "1. Edit .env file with your Telegram bot token and other settings"
echo "2. Run the application: python main.py"
echo "3. Or use the GUI launcher if available"
echo ""
print_status "For deployment to server, run: ./scripts/deploy.sh"
echo ""
print_status "Documentation available in docs/ directory"
echo "- User Guide: docs/USER_GUIDE.md"
echo "- Technical Docs: docs/TECHNICAL_DOCS.md"
echo ""
print_status "Ready to start! 🚀"
