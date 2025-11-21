# Advanced Features Implementation Guide

## 🚀 Overview

This document provides comprehensive details about the advanced features implemented in SmartFormBuilder. All features are production-ready and follow best practices for scalability, security, and user experience.

---

## 📋 Table of Contents

1. [Multi-Step Forms](#multi-step-forms)
2. [Advanced Field Types](#advanced-field-types)
3. [AI-Powered Optimization](#ai-powered-optimization)
4. [Team Collaboration](#team-collaboration)
5. [Analytics & Reporting](#analytics--reporting)
6. [Lead Management](#lead-management)
7. [White-Label & Enterprise](#white-label--enterprise)
8. [Compliance & Security](#compliance--security)
9. [API Documentation](#api-documentation)
10. [Setup & Configuration](#setup--configuration)

---

## 🎯 Multi-Step Forms

### Features

- **Wizard-Style Navigation**: Step-by-step form completion with progress indicators
- **Save & Resume**: Users can save progress and return later via email link
- **Conditional Branching**: Show/hide steps based on previous responses
- **Form Abandonment Recovery**: Automatic email reminders for incomplete forms
- **Progress Tracking**: Real-time progress bars and step indicators

### Backend Implementation

**Models**: `FormStep`, `PartialSubmission`

**Services**: `MultiStepFormService`

**Key Methods**:
- `save_partial_submission()`: Save user progress
- `get_partial_submission()`: Resume from token
- `mark_abandoned()`: Identify abandoned forms
- `validate_step_transition()`: Check conditional logic

### API Endpoints

```
POST /api/partial-submissions/save_progress/
GET /api/partial-submissions/resume/?token={resume_token}
GET /api/forms/{form_id}/steps/
```

### Frontend Component

Use the `MultiStepForm` component:

```tsx
import { MultiStepForm } from '@/components/MultiStepForm';

<MultiStepForm
  formSchema={formSchema}
  onSubmit={handleSubmit}
  autoSave={true}
  resumeData={resumeData}
/>
```

### Configuration

In your form schema:

```json
{
  "steps": [
    {
      "step_number": 1,
      "title": "Personal Information",
      "description": "Tell us about yourself",
      "fields": ["name", "email", "phone"],
      "conditional_logic": {
        "type": "all",
        "rules": [
          {
            "field_id": "email",
            "operator": "not_equals",
            "value": ""
          }
        ]
      }
    }
  ]
}
```

---

## 🔧 Advanced Field Types

### Calculated Fields

Automatically compute values based on formulas:

```json
{
  "type": "calculated",
  "formula": "quantity * price * 1.1",
  "label": "Total with Tax"
}
```

**Supported Functions**:
- Basic operators: `+`, `-`, `*`, `/`
- `SUM(field1, field2, field3)`
- `IF(condition, true_value, false_value)`

### File Upload with Preview

Handle file uploads with cloud storage:

```python
from forms.services.advanced_fields_service import AdvancedFieldService

file_data = AdvancedFieldService.handle_file_upload(
    file=uploaded_file,
    form_id=form.id,
    field_id='resume',
    allowed_extensions=['pdf', 'doc', 'docx']
)
```

**Configuration**:
- Set `AWS_STORAGE_BUCKET_NAME` in settings
- Configure S3 credentials
- Or use local storage with `MEDIA_ROOT`

### Signature Capture

Legal-compliant signature fields:

```json
{
  "type": "signature",
  "label": "Sign Here",
  "required": true,
  "legal_text": "I agree to the terms and conditions"
}
```

### Dynamic Dropdowns

Populate options from APIs or previous responses:

```json
{
  "type": "select",
  "dynamic_options": {
    "source_type": "api",
    "source_config": {
      "url": "https://api.example.com/cities",
      "method": "GET",
      "options_path": "data.cities"
    }
  }
}
```

### Custom Validation

Regular expressions and cross-field validation:

```json
{
  "validation": {
    "regex": "^[A-Z]{2}\\d{6}$",
    "error_message": "Format must be XX123456"
  }
}
```

---

## 🤖 AI-Powered Optimization

### A/B Testing

Test different form variations:

**Create A/B Test**:
```python
POST /api/ab-tests/
{
  "form": "form_id",
  "name": "Test Button Color",
  "variant_a_schema": {...},
  "variant_b_schema": {...},
  "traffic_split": 50
}
```

**Start Test**:
```python
POST /api/ab-tests/{id}/start/
```

**Get Results**:
```python
GET /api/ab-tests/{id}/results/
```

Returns statistical significance, conversion rates, and recommended winner.

### Automated Follow-ups

Create email sequences triggered by submissions:

```python
from forms.services.follow_up_service import FollowUpService

sequences = [
    {
        'hours': 1,
        'subject': 'Thank you!',
        'content': 'Hi {{name}}, thanks for your submission...'
    },
    {
        'hours': 24,
        'subject': 'Next steps',
        'content': 'Here are your next steps...'
    }
]

FollowUpService.create_follow_up_sequence(form, submission, sequences)
```

### Form Abandonment Recovery

Automatic recovery emails sent to users who start but don't complete forms:

**Celery Task** (runs hourly):
```python
@shared_task
def process_abandoned_forms():
    from forms.services.abandonment_service import AbandonmentRecoveryService
    return AbandonmentRecoveryService.batch_send_recovery_emails(max_emails=100)
```

**Configuration**:
```python
# settings.py
ABANDONMENT_THRESHOLD_HOURS = 24
RECOVERY_EMAIL_EXPIRY_HOURS = 72
```

---

## 👥 Team Collaboration

### Role-Based Permissions

Three access levels:
- **Viewer**: Read-only access
- **Editor**: Can edit forms
- **Admin**: Full management access

**Add Team Member**:
```python
POST /api/teams/{team_id}/members/
{
  "user": "user_id",
  "role": "editor"
}
```

### Form Sharing

Share forms with granular permissions:

```python
POST /api/form-shares/
{
  "form": "form_id",
  "shared_with_email": "user@example.com",
  "permission": "edit",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### Comments & Annotations

Add comments to form fields:

```python
POST /api/forms/{form_id}/comments/
{
  "field_id": "email",
  "content": "Should we make this optional?"
}
```

**Resolve Comment**:
```python
POST /api/forms/{form_id}/comments/{comment_id}/resolve/
```

### Version History

Automatic version snapshots created when publishing:

```python
# Automatically creates version
form.create_version()

# Revert to previous version
POST /api/forms/{form_id}/revert/
{
  "version_id": "version_uuid"
}
```

---

## 📊 Analytics & Reporting

### Analytics Dashboard

Comprehensive analytics with:
- Conversion funnel analysis
- Field-level engagement metrics
- Device and geography breakdowns
- Time-series data
- Heat maps

**Frontend Component**:
```tsx
import { AnalyticsDashboard } from '@/components/AnalyticsDashboard';

<AnalyticsDashboard formId={formId} />
```

**API Endpoint**:
```
GET /api/forms/{form_id}/analytics/dashboard/
  ?date_from=2024-01-01
  &date_to=2024-12-31
```

### Event Tracking

Track user interactions:

```python
from forms.services.analytics_service import FormAnalyticsService

FormAnalyticsService.track_event(
    form=form,
    session_id=session_id,
    event_type='field_focus',
    request=request,
    field_id='email',
    field_label='Email Address'
)
```

**Event Types**:
- `view`: Form viewed
- `start`: Form started
- `field_focus`: Field focused
- `field_blur`: Field blurred
- `field_error`: Validation error
- `step_complete`: Step completed
- `abandon`: Form abandoned
- `submit`: Form submitted

### Heat Maps

Visualize field engagement:

```python
GET /api/forms/{form_id}/analytics/dashboard/
```

Returns heat map data showing:
- Focus count per field
- Error rates
- Engagement intensity

---

## 💼 Lead Management

### Lead Scoring

Automatically score leads based on submission data:

```python
from forms.services.lead_scoring_service import LeadScoringService

lead_score = LeadScoringService.calculate_lead_score(submission)

# Returns:
# {
#   'total_score': 75,
#   'quality': 'hot',  # cold, warm, hot, qualified
#   'score_breakdown': {...}
# }
```

### Scoring Rules

Customize scoring logic:

```python
SCORING_RULES = {
    'email_domain': {
        'business_domains': 10,
        'free_domains': -5,
    },
    'phone_provided': 15,
    'company_name_provided': 20,
    'budget_range': {
        'high': 30,
        'medium': 15,
        'low': 5,
    }
}
```

### Lead Assignment

Auto-assign leads to team members:

```python
# Assign manually
POST /api/lead-scores/{lead_id}/assign/
{
  "user_id": "team_member_id"
}

# Auto-assign based on workload
LeadScoringService.auto_assign_lead(lead_score, team_members)
```

### Lead Status Tracking

Track lead progress through sales funnel:

```python
POST /api/lead-scores/{lead_id}/update_status/
{
  "status": "contacted",  # pending, contacted, negotiating, won, lost
  "notes": "Called customer, interested in premium package"
}
```

---

## 🏢 White-Label & Enterprise

### White-Label Configuration

Customize branding for agencies:

```python
POST /api/white-label/
{
  "custom_domain": "forms.myagency.com",
  "logo_url": "https://...",
  "primary_color": "#667eea",
  "secondary_color": "#764ba2",
  "email_from_name": "My Agency",
  "email_from_address": "noreply@myagency.com",
  "hide_branding": true
}
```

### Custom Domains

1. Add CNAME record: `forms.yourdomain.com` → `formforge.io`
2. Upload SSL certificate:
```python
PUT /api/white-label/{config_id}/
{
  "ssl_certificate": "-----BEGIN CERTIFICATE-----...",
  "ssl_key": "-----BEGIN PRIVATE KEY-----..."
}
```

### Bulk Operations

Process multiple forms at once:

```python
from forms.tasks import process_bulk_operations

process_bulk_operations.delay(
    operation_type='archive_forms',
    resource_ids=['form1_id', 'form2_id'],
    params={}
)
```

---

## 🔒 Compliance & Security

### GDPR Compliance

Track consent and manage data retention:

**Consent Recording**:
```python
from forms.models_advanced import ConsentRecord

ConsentRecord.objects.create(
    submission=submission,
    consent_type='marketing',
    granted=True,
    consent_text="I agree to receive marketing emails",
    ip_address=ip_address,
    user_agent=user_agent
)
```

**Data Export**:
```python
GET /api/submissions/export/?format=json&include_personal_data=true
```

**Data Deletion**:
```python
DELETE /api/submissions/{submission_id}/
```

### Audit Logs

All actions are logged for compliance:

```python
from forms.models_advanced import AuditLog

AuditLog.objects.create(
    user=request.user,
    action='form_update',
    resource_type='form',
    resource_id=str(form.id),
    details={'changes': ['title', 'schema']},
    ip_address=ip_address,
    user_agent=user_agent
)
```

**View Audit Trail**:
```python
GET /api/audit-logs/?date_from=2024-01-01
```

### SSO Integration

Support for enterprise authentication:

```python
# Configure in settings.py
SOCIAL_AUTH_SAML_ENABLED_IDPS = {
    'okta': {
        'entity_id': 'https://...',
        'url': 'https://...',
        'x509cert': '...'
    }
}
```

---

## 🔌 API Documentation

### REST API

**Base URL**: `https://api.formforge.io/v1/`

**Authentication**: Bearer token
```
Authorization: Bearer YOUR_TOKEN_HERE
```

### Key Endpoints

**Forms**:
```
GET    /api/forms/
POST   /api/forms/
GET    /api/forms/{id}/
PUT    /api/forms/{id}/
DELETE /api/forms/{id}/
POST   /api/forms/{id}/publish/
```

**Submissions**:
```
GET    /api/forms/{form_id}/submissions/
POST   /api/public/submit/{form_slug}/
GET    /api/forms/{form_id}/submissions/export/
```

**Advanced Features**:
```
POST   /api/partial-submissions/save_progress/
GET    /api/partial-submissions/resume/
GET    /api/forms/{form_id}/analytics/dashboard/
POST   /api/ab-tests/
GET    /api/lead-scores/
POST   /api/white-label/
GET    /api/audit-logs/
```

### Rate Limiting

- **Free plan**: 100 requests/hour
- **Pro plan**: 1000 requests/hour
- **Enterprise**: Custom limits

---

## ⚙️ Setup & Configuration

### Backend Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Run migrations**:
```bash
python manage.py migrate
```

3. **Configure Celery**:
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

4. **Start Celery worker**:
```bash
celery -A backend worker -l info
celery -A backend beat -l info
```

5. **Configure email**:
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@formforge.io'
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Configure environment**:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

3. **Run development server**:
```bash
npm run dev
```

### Celery Beat Schedule

Configure periodic tasks in `settings.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'process-abandoned-forms': {
        'task': 'forms.tasks.process_abandoned_forms',
        'schedule': crontab(minute=0),  # Every hour
    },
    'process-follow-ups': {
        'task': 'forms.tasks.process_automated_follow_ups',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'calculate-lead-scores': {
        'task': 'forms.tasks.calculate_lead_scores_batch',
        'schedule': crontab(minute=0),  # Every hour
    },
    'auto-declare-ab-winners': {
        'task': 'forms.tasks.auto_declare_ab_test_winners',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

### Storage Configuration

**AWS S3**:
```python
# settings.py
AWS_ACCESS_KEY_ID = 'your-key'
AWS_SECRET_ACCESS_KEY = 'your-secret'
AWS_STORAGE_BUCKET_NAME = 'your-bucket'
AWS_S3_REGION_NAME = 'us-east-1'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### Redis Configuration

For caching and real-time features:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up SSL certificates
- [ ] Configure production database (PostgreSQL)
- [ ] Set up Redis for caching
- [ ] Configure Celery workers
- [ ] Set up email service (SendGrid, AWS SES)
- [ ] Configure S3 for file storage
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Enable security headers
- [ ] Set up backups

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=formforge.io,www.formforge.io

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# AWS
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=formforge-uploads

# Frontend
NEXT_PUBLIC_API_URL=https://api.formforge.io
```

---

## 📚 Additional Resources

- [API Reference](https://docs.formforge.io/api)
- [Developer Guide](https://docs.formforge.io/developers)
- [Video Tutorials](https://youtube.com/formforge)
- [Support](https://support.formforge.io)

---

## 🆘 Support

For technical support or feature requests:
- Email: support@formforge.io
- Discord: https://discord.gg/formforge
- GitHub Issues: https://github.com/formforge/issues

---

**Last Updated**: November 21, 2025
**Version**: 2.0.0
