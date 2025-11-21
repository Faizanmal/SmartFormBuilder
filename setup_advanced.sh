#!/bin/bash

# SmartFormBuilder Advanced Features Setup Script
# This script helps set up all the new advanced features

set -e

echo "🚀 SmartFormBuilder Advanced Features Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -f "setup.sh" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo -e "${YELLOW}⚠️  Redis is not installed. Some features require Redis.${NC}"
    echo "Install Redis: sudo apt-get install redis-server (Ubuntu) or brew install redis (Mac)"
else
    echo -e "${GREEN}✓ Redis found${NC}"
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not installed. You'll need it for production.${NC}"
else
    echo -e "${GREEN}✓ PostgreSQL found${NC}"
fi

echo ""
echo "📦 Installing Backend Dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

echo ""
echo "🗄️  Setting up Database..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate

echo -e "${GREEN}✓ Database migrations complete${NC}"

# Create superuser if needed
echo ""
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "📦 Installing Frontend Dependencies..."
cd ../frontend

npm install

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

echo ""
echo "⚙️  Configuration Checklist"
echo "=========================="
echo ""
echo "Please configure the following in backend/.env:"
echo ""
echo "  📧 Email (for form recovery & follow-ups):"
echo "     EMAIL_HOST=smtp.gmail.com"
echo "     EMAIL_HOST_USER=your-email@gmail.com"
echo "     EMAIL_HOST_PASSWORD=your-app-password"
echo ""
echo "  🔴 Redis (for Celery & caching):"
echo "     CELERY_BROKER_URL=redis://localhost:6379/0"
echo "     REDIS_URL=redis://localhost:6379/0"
echo ""
echo "  ☁️  AWS S3 (for file uploads):"
echo "     AWS_ACCESS_KEY_ID=your-key"
echo "     AWS_SECRET_ACCESS_KEY=your-secret"
echo "     AWS_STORAGE_BUCKET_NAME=your-bucket"
echo ""
echo "  🔐 Security:"
echo "     SECRET_KEY=your-secret-key"
echo "     DEBUG=True  (set to False in production)"
echo ""
echo "  🌐 Frontend URL:"
echo "     FRONTEND_URL=http://localhost:3000"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating template...${NC}"
    cat > backend/.env << EOF
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smartformbuilder

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@smartformbuilder.com

# AWS S3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1

# Security
SECRET_KEY=change-me-to-a-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend
FRONTEND_URL=http://localhost:3000
EOF
    echo -e "${GREEN}✓ Created .env template at backend/.env${NC}"
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your actual credentials${NC}"
fi

echo ""
echo "🚀 Starting Services"
echo "===================="
echo ""
echo "You need to run these commands in separate terminals:"
echo ""
echo "  Terminal 1 - Backend:"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo ""
echo "  Terminal 2 - Celery Worker:"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    celery -A backend worker -l info"
echo ""
echo "  Terminal 3 - Celery Beat (scheduler):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    celery -A backend beat -l info"
echo ""
echo "  Terminal 4 - Frontend:"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Optional - Redis:"
echo "    redis-server"
echo ""

echo ""
echo "📚 Documentation"
echo "================"
echo ""
echo "  📖 Complete Feature Guide: ADVANCED_FEATURES.md"
echo "  📘 What's New: NEW_FEATURES_README.md"
echo "  📙 Quick Reference: QUICK_REFERENCE.md"
echo ""

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "  1. Edit backend/.env with your credentials"
echo "  2. Start Redis (if not running): redis-server"
echo "  3. Start the services (see commands above)"
echo "  4. Visit http://localhost:3000"
echo ""
echo "🎉 Happy form building!"
