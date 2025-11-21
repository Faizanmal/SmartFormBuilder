# ⚡ Quick Start Guide - Advanced Features

## 🚀 Get Up and Running in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Step 2: Run Migrations (1 minute)

```bash
cd backend
python manage.py migrate
```

### Step 3: Start Services (2 minutes)

**Option A: Quick Development Setup**
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Option B: Full Setup (with background tasks)**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend
cd backend
python manage.py runserver

# Terminal 3: Celery Worker
cd backend
celery -A backend worker -l info

# Terminal 4: Celery Beat
cd backend
celery -A backend beat -l info

# Terminal 5: Frontend
cd frontend
npm run dev
```

---

## 🎯 Try These Features First

### 1. Multi-Step Form (5 minutes)

**Create a multi-step form:**
```json
POST http://localhost:8000/api/v1/forms/
{
  "title": "Customer Survey",
  "steps": [
    {
      "step_number": 1,
      "title": "Personal Info",
      "fields": ["name", "email"]
    },
    {
      "step_number": 2,
      "title": "Preferences",
      "fields": ["interests", "budget"]
    }
  ]
}
```

**Save progress:**
```json
POST http://localhost:8000/api/v1/partial-submissions/save_progress/
{
  "form_slug": "customer-survey",
  "email": "user@example.com",
  "payload": {"name": "John", "email": "john@example.com"},
  "current_step": 1
}
```

### 2. A/B Testing (3 minutes)

**Create an A/B test:**
```json
POST http://localhost:8000/api/v1/ab-tests/
{
  "form": "form-id-here",
  "name": "Test Button Color",
  "variant_a_schema": {
    "button_color": "blue"
  },
  "variant_b_schema": {
    "button_color": "green"
  },
  "traffic_split": 50
}
```

**Start the test:**
```json
POST http://localhost:8000/api/v1/ab-tests/{test-id}/start/
```

### 3. View Analytics (2 minutes)

**Get dashboard data:**
```
GET http://localhost:8000/api/v1/forms/{form-id}/analytics/dashboard/
```

**Use React component:**
```tsx
import { AnalyticsDashboard } from '@/components/AnalyticsDashboard';

<AnalyticsDashboard formId="your-form-id" />
```

### 4. Lead Scoring (3 minutes)

**Automatic scoring on submission:**
Scores are calculated automatically when a form is submitted.

**View lead scores:**
```
GET http://localhost:8000/api/v1/lead-scores/
```

**Assign a lead:**
```json
POST http://localhost:8000/api/v1/lead-scores/{lead-id}/assign/
{
  "user_id": "team-member-id"
}
```

---

## 🛠️ Common Tasks

### Add Team Member
```json
POST http://localhost:8000/api/v1/teams/{team-id}/members/
{
  "user": "user-id",
  "role": "editor"  // viewer, editor, or admin
}
```

### Add Comment to Form
```json
POST http://localhost:8000/api/v1/forms/{form-id}/comments/
{
  "field_id": "email",
  "content": "Should we make this optional?"
}
```

### Share a Form
```json
POST http://localhost:8000/api/v1/form-shares/
{
  "form": "form-id",
  "shared_with_email": "colleague@example.com",
  "permission": "edit",  // view, submit, edit, or manage
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### Configure White-Label
```json
POST http://localhost:8000/api/v1/white-label/
{
  "custom_domain": "forms.mycompany.com",
  "logo_url": "https://mycompany.com/logo.png",
  "primary_color": "#667eea",
  "secondary_color": "#764ba2",
  "hide_branding": true
}
```

---

## 📋 Essential Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/smartformbuilder

# Redis (for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# Email (required for recovery & follow-ups)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@formforge.io

# AWS S3 (for file uploads)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# Security
SECRET_KEY=your-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 Quick Test

**Test if everything works:**

1. Visit admin panel: http://localhost:8000/admin
2. Create a form with steps
3. Submit the form (check multi-step works)
4. View analytics dashboard
5. Check Celery tasks are running: http://localhost:5555 (if using Flower)

---

## 📚 Next Steps

**Learn More:**
- 📖 Complete guide: `ADVANCED_FEATURES.md`
- 📘 Feature overview: `NEW_FEATURES_README.md`
- 📙 Implementation: `IMPLEMENTATION_COMPLETE.md`

**Common Issues:**

**Celery not working?**
```bash
# Make sure Redis is running
redis-cli ping  # Should return PONG

# Check Celery logs
celery -A backend worker -l debug
```

**Emails not sending?**
- Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
- For Gmail, use an "App Password" (not your regular password)
- Check spam folder

**File uploads failing?**
- Configure AWS_ACCESS_KEY_ID in .env
- Or set up local storage: `MEDIA_ROOT` and `MEDIA_URL`

---

## 🎉 You're Ready!

Start building advanced forms with:
- ✅ Multi-step workflows
- ✅ A/B testing
- ✅ Lead scoring
- ✅ Analytics
- ✅ Team collaboration
- ✅ And much more!

**Happy form building! 🚀**
