# FormForge - Smart AI Form Builder

Build intelligent forms in 60 seconds using AI. No code required. Generate, customize, and embed forms that capture higher-quality leads with webhooks, analytics, and integrations.

## Overview

FormForge is a complete SaaS platform that uses AI to generate production-ready forms from natural language descriptions. It includes conditional logic, validation, webhooks, integrations, analytics, enterprise-grade security, conversational interfaces, A/B testing, predictive analytics, and more.

### Target Users
- Small businesses and solopreneurs
- Marketing teams
- Non-technical administrators
- Developers needing embeddable forms
- Enterprise teams

## Features

### Core Features
- **AI Form Generation**: GPT-4o powered, describe your needs and get a complete form
- **Visual Form Builder**: Drag & drop editor with 21 field types and live preview
- **Field Types**: Text, Email, Phone, Textarea, Number, Date, Time, Select, Multi-select, Checkbox, Radio, File Upload, URL, Payment, Slider, Rating, Signature, Address, Calculated, Heading, Divider
- **Integrations**: Webhooks, Email notifications, Google Sheets OAuth2, Stripe payments
- **Analytics**: Dashboard with views, submissions, conversion rates, charts, CSV export
- **Embeds**: iFrame, JavaScript, React component
- **Authentication**: JWT auth with login/register
- **Conditional Logic**: Visual rule builder
- **Templates**: Pre-built templates by category
- **Public Forms**: Hosted forms with custom slugs
- **Rate Limiting**: Global middleware and per-form limits
- **Encryption**: AES-256 for credentials
- **Async Tasks**: Celery with Redis
- **Payments**: Stripe integration
- **Multi-step Forms**: Wizard-style with progress

### Advanced Features
- Conversational Forms (chatbot-style)
- A/B Testing
- Progressive Web App (PWA)
- Internationalization (i18n)
- Predictive Analytics
- Scheduling
- Themes & Branding
- Collaboration (teams, real-time editing)
- Mobile Optimization
- Advanced Security (GDPR, 2FA, SSO)
- Smart Notifications
- Workflow Automation
- Lead Scoring
- Version Control
- Voice Design
- Performance Monitoring
- Integration Marketplace
- Compliance & Accessibility

### Emerging Technology Features
- AI Layout Optimizer
- Voice & Multimodal Input
- Zero-knowledge Encryption
- Advanced Integrations
- Mobile & PWA Enhancements
- Workflow Automation
- UX & Design Tools
- Performance & Scalability
- Developer Experience

For detailed emerging features, see [EMERGING_FEATURES_SUMMARY.md](EMERGING_FEATURES_SUMMARY.md).

## Tech Stack

### Backend
- Django 5.2.7 + Django REST Framework 3.15.2
- PostgreSQL 14+ (JSONB support)
- JWT Authentication
- OpenAI GPT-4o
- Stripe API
- Celery + Redis
- Encryption (Cryptography)
- Django Channels (WebSockets)

### Frontend
- Next.js 16.0.1 (App Router)
- shadcn/ui + Tailwind CSS
- Recharts
- Axios
- TypeScript
- PWA support

### Infrastructure
- Gunicorn, Nginx
- Docker, Docker Compose
- SSL (Let's Encrypt)

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- OpenAI API Key
- Stripe Account (for payments)

## Installation

### Quick Development Setup (SQLite)

```bash
cd SmartFormBuilder

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Set USE_SQLITE=True
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

```bash
# Frontend (new terminal)
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- Admin: http://localhost:8000/admin

### Full Production Setup (PostgreSQL + Redis)

1. Set up PostgreSQL and Redis.
2. Configure .env with database credentials, API keys.
3. Run migrations and start servers as above.

## Usage

1. Register/Login at http://localhost:3000
2. Create a form using AI: Describe your form in natural language.
3. Customize in the visual builder.
4. Publish and embed or share the public link.
5. View analytics and submissions.

## API

See [API.md](API.md) for complete API reference.

## Documentation

- [SETUP.md](SETUP.md) - Development setup
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [FRONTEND_COMPLETE.md](FRONTEND_COMPLETE.md) - Frontend architecture
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - Implementation summary
- [EMERGING_FEATURES_QUICK_REFERENCE.md](EMERGING_FEATURES_QUICK_REFERENCE.md) - Emerging features

## Contributing

Contributions are welcome. Please follow the standard Git workflow.

## License

Proprietary - All rights reserved.

## Support

- Email: support@formforge.io
- Documentation: https://docs.formforge.io
