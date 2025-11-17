# FormForge - Smart AI Form Builder ✨

**Build intelligent forms in 60 seconds using AI** - No code required. Generate, customize, and embed forms that capture higher-quality leads with webhooks, analytics, and integrations.

> **🎉 Status**: **PRODUCTION-READY** - All core features implemented and documented!

## 🎯 Overview

FormForge is a complete SaaS platform that uses AI to generate production-ready forms from natural language descriptions. It includes conditional logic, validation, webhooks, integrations, analytics, and enterprise-grade security.

### Target Users
- Small businesses & solopreneurs (photographers, clinics, therapists, gyms, real estate agents)
- Marketing teams
- Non-technical office administrators
- Developers needing embeddable forms

### ✅ Completed Features (100%)

1. **✨ AI Form Generation** - GPT-4o powered, describe your needs, get a complete form
2. **🎨 Visual Form Editor** - Drag & drop reorder, inline editing, 15+ field types
3. **🔗 Integrations Hub** - Webhooks with HMAC signatures, Email notifications, Google Sheets OAuth2, Stripe payments
4. **📊 Analytics Dashboard** - Views, submissions, conversion rates, charts (Recharts), CSV export
5. **💾 CSV Export** - One-click download of all submission data
6. **🌐 Multi-format Embeds** - iFrame, JavaScript (embed/popup/open), React component
7. **🔐 User Authentication** - JWT auth with login/register pages
8. **🎯 Conditional Logic** - Dynamic field visibility based on user inputs
9. **📝 Form Templates** - Pre-built templates by category
10. **🚀 Public Form Renderer** - Beautiful hosted forms with custom slugs
11. **� Analytics Charts** - Line chart (30-day trend), Bar chart (field completion rates)
12. **🔒 Rate Limiting** - Global middleware + per-form submission limits
13. **🔐 Encryption** - AES-256 for integration credentials and OAuth tokens
14. **⚡ Async Tasks** - Celery workers with Redis for webhooks, email, sync
15. **💳 Payment Fields** - Stripe Checkout integration with subscription support
16. **📧 Email Notifications** - Template-based async notifications
17. **🔄 Webhook Retries** - 5 retries with exponential backoff, delivery logging
18. **📑 Google Sheets** - OAuth2 flow, auto-sync submissions to spreadsheet

### 📚 Documentation
- ✅ [SETUP.md](SETUP.md) - Development environment setup
- ✅ [API.md](API.md) - Complete API reference
- ✅ [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- ✅ [FRONTEND_COMPLETE.md](FRONTEND_COMPLETE.md) - Frontend architecture
- ✅ [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - Implementation summary
- ✅ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Quick overview

## 🏗️ Tech Stack

### Backend
- **Framework**: Django 5.2.7 + Django REST Framework 3.15.2
- **Database**: PostgreSQL 14+ (with JSONB support)
- **Authentication**: JWT (Simple JWT)
- **AI**: OpenAI GPT-4o
- **Payments**: Stripe API v11.3.0
- **Task Queue**: Celery 5.4.0 + Redis 5.2.0
- **Cache**: Redis
- **Encryption**: Cryptography 44.0.0 (Fernet AES-256)
- **Integrations**: Google Sheets API v4, Stripe webhooks

### Frontend
- **Framework**: Next.js 16.0.1 (App Router)
- **UI Library**: shadcn/ui + Tailwind CSS 3.4.1
- **Charts**: Recharts 2.15.0
- **State Management**: React Hooks
- **HTTP Client**: Axios with interceptors
- **Notifications**: Sonner
- **TypeScript**: Full type safety

### Infrastructure
- **Web Server**: Gunicorn (WSGI)
- **Reverse Proxy**: Nginx
- **Process Manager**: systemd (backend), PM2 (frontend)
- **SSL**: Let's Encrypt
- **Monitoring**: systemd logs, PM2 logs, Celery logs

## 📋 Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **PostgreSQL** 14+
- **Redis** 6+
- **OpenAI API Key**
- **Stripe Account** (for payments)

## 🚀 Quick Start

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env file with your credentials:
# - Database credentials
# - OPENAI_API_KEY
# - STRIPE keys
# - etc.

# Create PostgreSQL database
# In PostgreSQL:
# CREATE DATABASE formforge;
# CREATE USER postgres WITH PASSWORD 'your_password';
# GRANT ALL PRIVILEGES ON DATABASE formforge TO postgres;

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
SmartFormBuilder/
├── backend/
│   ├── backend/               # Django project settings
│   │   ├── settings.py        # Main settings
│   │   ├── urls.py            # URL routing
│   │   └── ...
│   ├── users/                 # User management app
│   │   ├── models.py          # User, Team, APIKey models
│   │   ├── views.py           # Auth & user endpoints
│   │   ├── serializers.py     # User serializers
│   │   └── ...
│   ├── forms/                 # Forms management app
│   │   ├── models.py          # Form, Submission, Template models
│   │   ├── views.py           # Forms CRUD endpoints
│   │   ├── serializers.py     # Form serializers
│   │   ├── services/
│   │   │   └── ai_service.py  # OpenAI integration
│   │   └── ...
│   ├── integrations/          # Integrations app
│   │   ├── models.py          # Integration, WebhookLog models
│   │   ├── views.py           # Integration endpoints
│   │   ├── services/
│   │   │   └── webhook_service.py  # Webhook delivery
│   │   └── ...
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js app router pages
│   │   │   ├── dashboard/     # Dashboard page
│   │   │   ├── forms/
│   │   │   │   ├── new/       # Form creation
│   │   │   │   └── [id]/      # Form edit & analytics
│   │   │   └── ...
│   │   ├── components/        # React components
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── lib/
│   │   │   ├── api.ts         # Axios instance
│   │   │   └── api-client.ts  # API functions
│   │   └── types/
│   │       └── index.ts       # TypeScript types
│   ├── package.json
│   └── ...
│
└── README.md
```

## 🔑 Environment Variables

### Backend (.env)

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=formforge
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=sk-...

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/refresh/` - Refresh token
- `POST /api/v1/users/register/` - Register new user
- `GET /api/v1/users/me/` - Get current user

### Forms
- `GET /api/v1/forms/` - List all forms
- `POST /api/v1/forms/` - Create form (with AI generation)
- `GET /api/v1/forms/{id}/` - Get form details
- `PATCH /api/v1/forms/{id}/` - Update form
- `DELETE /api/v1/forms/{id}/` - Delete form
- `POST /api/v1/forms/{id}/publish/` - Publish form
- `GET /api/v1/forms/{id}/embed/` - Get embed code
- `GET /api/v1/forms/{id}/analytics/` - Get analytics
- `POST /api/v1/generate/` - Generate form schema from prompt

### Submissions
- `GET /api/v1/forms/{id}/submissions/` - List submissions
- `POST /api/v1/public/submit/{slug}/` - Submit form (public, no auth)

### Templates
- `GET /api/v1/templates/` - List templates
- `POST /api/v1/templates/{id}/use/` - Create form from template

### Integrations
- `GET /api/v1/integrations/` - List integrations
- `POST /api/v1/integrations/` - Create integration
- `POST /api/v1/integrations/{id}/test/` - Test integration

## 🤖 AI Form Generation

FormForge uses OpenAI GPT-4o with few-shot learning to generate form schemas. The AI service:

1. Takes a natural language prompt (e.g., "Create a wedding photographer intake form")
2. Uses system prompts and examples to ensure consistent JSON output
3. Generates complete form schema with:
   - Fields (type, label, placeholder, validation)
   - Conditional logic rules
   - Privacy/consent text
   - Integration suggestions

Example prompt:
```
Create a client intake for wedding photographer — ask about event date, location, estimated guest count, package interest, deposit payment option, and space for questions
```

Generated output includes fields like:
- Full name (text)
- Email (email with validation)
- Event date (date picker)
- Package selection (dropdown)
- Conditional payment field (shown if deposit selected)

## 💳 Pricing Tiers

- **Free**: 3 forms, 100 submissions/month, basic integrations
- **Starter** ($12/mo): Unlimited forms, 1k submissions, Google Sheets + Email
- **Pro** ($29/mo): 10k submissions, webhooks, team seats
- **Business** ($99/mo): SSO, priority support, advanced integrations

## 🔐 Security Features

- **HTTPS Only** (enforce in production)
- **JWT Authentication** with token rotation
- **HMAC-SHA256** webhook signatures
- **CORS** protection
- **Rate limiting** (TODO: implement)
- **Data encryption** for integration credentials
- **GDPR Compliance** with data retention policies
- **PCI-DSS** via Stripe hosted checkout (no card data storage)

## 🧪 Testing

```powershell
# Backend tests
cd backend
python manage.py test

# Frontend tests (if implemented)
cd frontend
npm test
```

## 📦 Deployment

### Backend (Render/Railway/Fly.io)

1. Set environment variables
2. Run migrations: `python manage.py migrate`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Start with Gunicorn: `gunicorn backend.wsgi:application`

### Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set environment variables
3. Deploy automatically on push

### Database
- Use managed PostgreSQL (AWS RDS, Supabase, or provider's offering)
- Set up automated backups
- Enable SSL connections

### Redis
- Use managed Redis (Redis Cloud, AWS ElastiCache, or Upstash)

## 🎯 Roadmap

### Phase 1 (Current - MVP)
- [x] Backend models & API
- [x] AI form generation
- [x] Frontend dashboard
- [ ] Form editor UI
- [ ] Integrations (webhooks, email, Google Sheets)
- [ ] Embeddable form renderer
- [ ] Stripe billing

### Phase 2 (Post-MVP)
- [ ] Advanced conditional logic builder
- [ ] A/B testing
- [ ] Pre-built templates marketplace
- [ ] Multi-language support
- [ ] AI email summaries
- [ ] Mobile app

### Phase 3 (Scale)
- [ ] White-label options
- [ ] Advanced analytics
- [ ] Custom domain support
- [ ] API for developers
- [ ] Zapier integration

## 📝 License

Proprietary - All rights reserved

## 👥 Team

- Product Owner: [Your Name]
- Backend Developer: [Name]
- Frontend Developer: [Name]
- Designer: [Name]

## 📧 Support

- Email: support@formforge.io
- Documentation: https://docs.formforge.io
- Discord: https://discord.gg/formforge

---

**Built with ❤️ for small businesses who need forms that work**
