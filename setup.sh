#!/bin/bash

# SmartFormBuilder - Quick Setup Script
# This script sets up the development environment for SmartFormBuilder

set -e

echo "🚀 SmartFormBuilder - Quick Setup"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend/manage.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Backend Setup
echo "📦 Setting up Backend..."
cd backend

# Install Python dependencies
echo "  → Installing Python dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "  → Creating .env file..."
    cat > .env << EOF
# Django Settings
DEBUG=True
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/smartformbuilder

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key-here
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret-here

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@formforge.io

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
    echo "  ✅ .env file created. Please update with your API keys."
else
    echo "  ✅ .env file already exists"
fi

# Run migrations
echo "  → Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "  ✅ Backend setup complete!"
echo ""

# Frontend Setup
cd ../frontend
echo "📦 Setting up Frontend..."

# Install Node dependencies
echo "  → Installing Node dependencies..."
npm install

# Check for .env.local file
if [ ! -f ".env.local" ]; then
    echo "  → Creating .env.local file..."
    cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_EMBED_BASE_URL=http://localhost:3000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=$(openssl rand -base64 32)
EOF
    echo "  ✅ .env.local file created"
else
    echo "  ✅ .env.local file already exists"
fi

echo "  ✅ Frontend setup complete!"
echo ""

cd ..

# Summary
echo "✨ Setup Complete!"
echo "=================="
echo ""
echo "To start development:"
echo ""
echo "  Backend (Django):"
echo "    cd backend"
echo "    python manage.py runserver"
echo ""
echo "  Frontend (Next.js):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Create a superuser (optional):"
echo "    cd backend"
echo "    python manage.py createsuperuser"
echo ""
echo "📚 Documentation:"
echo "  - Features: FEATURES.md"
echo "  - Backend API: http://localhost:8000/api/v1/"
echo "  - Frontend: http://localhost:3000"
echo ""
echo "⚠️  Don't forget to:"
echo "  1. Update API keys in backend/.env"
echo "  2. Start Redis (for Celery): redis-server"
echo "  3. Start Celery worker: cd backend && celery -A backend worker -l info"
echo ""
echo "Happy coding! 🎉"
