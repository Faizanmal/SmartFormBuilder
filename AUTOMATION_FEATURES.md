# SmartFormBuilder Automation Features

This document describes the 8 advanced automation features added to SmartFormBuilder for real-world pain points and workflow automation.

## Table of Contents

1. [AI-Powered Form Optimization Engine](#1-ai-powered-form-optimization-engine)
2. [Automated Lead Nurturing Workflows](#2-automated-lead-nurturing-workflows)
3. [Real-Time Form Personalization](#3-real-time-form-personalization)
4. [Automated Compliance Scanner](#4-automated-compliance-scanner)
5. [Voice-Activated Form Design](#5-voice-activated-form-design)
6. [Predictive Analytics Dashboard](#6-predictive-analytics-dashboard)
7. [Integration Marketplace](#7-integration-marketplace)
8. [AI Content Generator](#8-ai-content-generator)

---

## 1. AI-Powered Form Optimization Engine

### Overview
Uses machine learning to analyze form performance and automatically suggest optimizations based on real user behavior data.

### Features
- **Performance Analysis**: Tracks completion rates, field-level drop-offs, time spent per field
- **Smart Suggestions**: AI-generated recommendations for field order, labels, and structure
- **Auto-Optimize**: One-click application of all recommended optimizations
- **A/B Testing Integration**: Automatically creates test variants for suggested changes

### API Endpoints
```
GET  /api/v1/automation/forms/{id}/optimization/analyze/
GET  /api/v1/automation/forms/{id}/optimization/suggestions/
POST /api/v1/automation/forms/{id}/optimization/apply/
POST /api/v1/automation/forms/{id}/optimization/auto-optimize/
```

### Usage Example
```python
# Get optimization suggestions
suggestions = optimization_service.generate_optimization_suggestions(form)

# Apply specific suggestion
optimization_service.apply_optimization(form, suggestion_id)

# Auto-optimize entire form
optimized_form = optimization_service.auto_optimize_form(form)
```

---

## 2. Automated Lead Nurturing Workflows

### Overview
Create sophisticated email/SMS sequences that trigger based on form submissions and user actions.

### Features
- **Visual Workflow Builder**: Drag-and-drop interface for creating workflows
- **Multi-Action Support**: Email, SMS, webhook, wait, CRM sync actions
- **Conditional Logic**: Branch workflows based on form field values
- **Automatic Triggers**: Start workflows on submission, abandonment, or custom events

### Supported Actions
| Action Type | Description |
|------------|-------------|
| `send_email` | Send templated email with field merging |
| `send_sms` | Send SMS via Twilio |
| `wait` | Delay for specified duration |
| `webhook` | Call external API |
| `crm_sync` | Sync to Salesforce, HubSpot, or Pipedrive |

### API Endpoints
```
GET    /api/v1/automation/workflows/
POST   /api/v1/automation/workflows/
GET    /api/v1/automation/workflows/{id}/
PUT    /api/v1/automation/workflows/{id}/
DELETE /api/v1/automation/workflows/{id}/
POST   /api/v1/automation/workflows/{id}/trigger/
GET    /api/v1/automation/workflows/{id}/executions/
```

### Workflow JSON Structure
```json
{
  "name": "Lead Follow-up Sequence",
  "form_id": "123",
  "trigger_type": "submission",
  "actions": [
    {
      "type": "send_email",
      "config": {
        "template": "welcome",
        "subject": "Thanks for your interest!"
      },
      "delay_minutes": 0
    },
    {
      "type": "wait",
      "config": { "duration_hours": 24 }
    },
    {
      "type": "send_email",
      "config": {
        "template": "follow_up",
        "subject": "Just checking in..."
      }
    }
  ]
}
```

---

## 3. Real-Time Form Personalization

### Overview
Dynamically customize forms based on user data fetched from external sources (CRMs, databases, APIs).

### Features
- **Data Source Connectors**: Connect to APIs, CRMs, databases
- **Field Prefilling**: Auto-fill fields with known user data
- **Dynamic Visibility**: Show/hide fields based on user profile
- **Real-time Rules**: Apply personalization rules on form load

### API Endpoints
```
GET    /api/v1/automation/forms/{id}/personalization/rules/
POST   /api/v1/automation/forms/{id}/personalization/rules/
DELETE /api/v1/automation/forms/{id}/personalization/rules/{rule_id}/
POST   /api/v1/automation/forms/{id}/personalization/apply/
```

### Personalization Rule Structure
```json
{
  "name": "VIP Customer Flow",
  "condition": {
    "field": "customer_tier",
    "operator": "equals",
    "value": "premium"
  },
  "actions": [
    {
      "type": "show_fields",
      "fields": ["vip_support_option", "dedicated_manager"]
    },
    {
      "type": "prefill",
      "field": "discount_code",
      "value": "VIP20"
    }
  ]
}
```

---

## 4. Automated Compliance Scanner

### Overview
Automatically scans forms for GDPR, WCAG accessibility, HIPAA, and PCI-DSS compliance issues.

### Supported Standards
| Standard | Description |
|----------|-------------|
| GDPR | Data protection and privacy compliance |
| WCAG | Web accessibility (A, AA, AAA levels) |
| HIPAA | Healthcare data protection |
| PCI-DSS | Payment card industry standards |

### Features
- **Comprehensive Scanning**: Detects 30+ compliance issues
- **Severity Levels**: Critical, Warning, Info classifications
- **Auto-Fix**: One-click fixes for common issues
- **Compliance Reports**: Downloadable audit reports

### API Endpoints
```
POST /api/v1/automation/forms/{id}/compliance/scan/
GET  /api/v1/automation/forms/{id}/compliance/scans/
POST /api/v1/automation/forms/{id}/compliance/auto-fix/
GET  /api/v1/automation/forms/{id}/compliance/report/
```

### Scan Response Example
```json
{
  "scan_id": "abc123",
  "overall_score": 85,
  "issues": [
    {
      "id": "gdpr-1",
      "severity": "critical",
      "type": "GDPR",
      "title": "Missing privacy policy link",
      "description": "Form collects email but has no privacy policy",
      "auto_fixable": true,
      "fix_action": "add_privacy_link"
    }
  ],
  "passed_checks": 25,
  "total_checks": 30
}
```

---

## 5. Voice-Activated Form Design

### Overview
Design and edit forms using voice commands. Built with OpenAI Whisper for transcription and GPT-4 for command interpretation.

### Supported Commands
| Command | Example |
|---------|---------|
| Add field | "Add an email field called contact" |
| Remove field | "Remove the phone number field" |
| Reorder | "Move company name to the top" |
| Configure | "Make email required" |
| Create form | "Create a contact form with name, email, and message" |

### Features
- **Natural Language**: Understands conversational commands
- **Audio Feedback**: Text-to-speech responses
- **Command History**: Review and replay past commands
- **Live Preview**: See changes in real-time

### API Endpoints
```
POST /api/v1/automation/voice/sessions/
POST /api/v1/automation/voice/sessions/{id}/command/
POST /api/v1/automation/voice/sessions/{id}/audio/
GET  /api/v1/automation/voice/sessions/{id}/
```

### Audio Command Flow
```python
# 1. Start session
session = voice_service.create_session(form_id)

# 2. Send audio command
result = voice_service.process_audio_command(
    session_id=session.id,
    audio_file=audio_blob
)

# 3. Get updated form schema
updated_form = result['form_schema']

# 4. Get audio response
audio_response = result['audio_response']  # Base64 MP3
```

---

## 6. Predictive Analytics Dashboard

### Overview
ML-powered forecasting, anomaly detection, and proactive insights for form performance.

### Features
- **Submission Forecasting**: Predict next 7/30/90 days of submissions
- **Anomaly Detection**: Automatic alerts for unusual patterns
- **Trend Analysis**: Identify seasonal and weekly patterns
- **AI Insights**: Natural language explanations of data

### Metrics Tracked
- Submission volume
- Completion rate
- Average completion time
- Drop-off rate
- Field-level engagement

### API Endpoints
```
GET /api/v1/automation/forms/{id}/analytics/forecast/
GET /api/v1/automation/forms/{id}/analytics/anomalies/
GET /api/v1/automation/forms/{id}/analytics/trends/
GET /api/v1/automation/forms/{id}/analytics/insights/
```

### Alert Configuration
```json
{
  "name": "Low Completion Alert",
  "metric": "completion_rate",
  "condition": "less_than",
  "threshold": 0.5,
  "notification_channels": ["email", "slack"],
  "cooldown_hours": 24
}
```

---

## 7. Integration Marketplace

### Overview
50+ pre-built integration connectors with guided setup wizards for one-click connections.

### Available Integrations

#### CRM
- Salesforce, HubSpot, Pipedrive, Zoho CRM, Freshsales

#### Email Marketing
- Mailchimp, SendGrid, ConvertKit, ActiveCampaign, Klaviyo

#### Project Management
- Slack, Asana, Monday.com, Trello, Notion, Jira

#### Storage & Databases
- Google Sheets, Airtable, Firebase, MongoDB, PostgreSQL

#### Automation
- Zapier, Make (Integromat), n8n, Pabbly Connect

#### Payments
- Stripe, PayPal, Square

#### Communication
- Twilio, Discord, Microsoft Teams

### API Endpoints
```
GET  /api/v1/automation/integrations/catalog/
POST /api/v1/automation/integrations/setup/
GET  /api/v1/automation/integrations/
POST /api/v1/automation/integrations/{id}/test/
POST /api/v1/automation/integrations/{id}/sync/
DELETE /api/v1/automation/integrations/{id}/
```

### Integration Setup Flow
```json
// 1. Get connector info
GET /catalog/?connector=mailchimp

// 2. Setup integration
POST /setup/
{
  "form_id": "123",
  "connector_id": "mailchimp",
  "credentials": {
    "api_key": "xxx"
  },
  "field_mapping": {
    "email": "EMAIL",
    "name": "FNAME"
  }
}

// 3. Test connection
POST /{integration_id}/test/

// 4. Enable auto-sync
PUT /{integration_id}/
{ "auto_sync": true }
```

---

## 8. AI Content Generator

### Overview
Generate form content, email templates, consent text, and more using GPT-4.

### Content Types
| Type | Description |
|------|-------------|
| Description | Form introduction text |
| Placeholders | Field placeholder text |
| Email Templates | Confirmation, follow-up, reminder emails |
| Thank You | Submission success messages |
| Consent | GDPR-compliant consent text |
| Translations | Multi-language form content |
| Questions | Survey/quiz question suggestions |

### API Endpoints
```
POST /api/v1/automation/forms/{id}/content/description/
POST /api/v1/automation/forms/{id}/content/placeholders/
POST /api/v1/automation/forms/{id}/content/email/
POST /api/v1/automation/forms/{id}/content/thank-you/
POST /api/v1/automation/forms/{id}/content/consent/
POST /api/v1/automation/forms/{id}/content/translate/
POST /api/v1/automation/forms/{id}/content/questions/
POST /api/v1/automation/forms/{id}/content/suggestions/
```

### Usage Examples

#### Generate Form Description
```json
POST /content/description/
{
  "tone": "professional",
  "context": "B2B software company"
}

// Response
{
  "description": "Share your requirements and our team will create a customized solution..."
}
```

#### Generate Email Template
```json
POST /content/email/
{
  "template_type": "confirmation",
  "brand_name": "Acme Corp"
}

// Response
{
  "subject": "Thank you for your submission!",
  "body": "Dear {{name}},\n\nThank you for reaching out to Acme Corp..."
}
```

#### Translate Form
```json
POST /content/translate/
{
  "language": "Spanish"
}

// Response
{
  "translations": {
    "Submit": "Enviar",
    "Email Address": "Correo Electrónico",
    ...
  }
}
```

---

## Backend Services Architecture

All automation features are implemented as services in `backend/forms/services/`:

```
services/
├── optimization_service.py      # Form optimization
├── workflow_service.py          # Lead nurturing
├── personalization_service.py   # Form personalization
├── compliance_service.py        # Compliance scanning
├── voice_design_service.py      # Voice commands
├── predictive_analytics_service.py  # Analytics
├── marketplace_service.py       # Integrations
└── ai_content_service.py        # Content generation
```

## Frontend Components

React components in `frontend/src/components/`:

```
components/
├── FormOptimizationDashboard.tsx
├── WorkflowBuilder.tsx
├── ComplianceScanner.tsx
├── VoiceDesignStudio.tsx
├── IntegrationMarketplace.tsx
├── PredictiveAnalyticsDashboard.tsx
├── AIContentGenerator.tsx
└── automation/
    └── index.ts  # Re-exports all components
```

## Celery Tasks

Background tasks in `backend/forms/tasks.py`:

| Task | Schedule | Description |
|------|----------|-------------|
| `process_workflow_executions` | Every 5 min | Execute pending workflow actions |
| `trigger_workflows_on_submission` | On submit | Start workflows for new submissions |
| `check_alert_conditions` | Hourly | Check predictive analytics alerts |
| `aggregate_daily_stats` | Daily | Aggregate form statistics |
| `generate_optimization_suggestions_batch` | Daily | Generate optimization suggestions |
| `sync_integration` | Varies | Sync data to integrations |
| `cleanup_old_voice_sessions` | Daily | Clean up stale voice sessions |
| `run_compliance_scans_batch` | Weekly | Run compliance scans |

## Database Models

New models in `backend/forms/models_advanced.py`:

- `NurturingWorkflow` - Workflow definitions
- `WorkflowExecution` - Workflow instances
- `WorkflowActionLog` - Action execution logs
- `FormIntegration` - Integration configurations
- `AlertConfig` - Alert rules
- `AlertHistory` - Triggered alerts
- `VoiceDesignSession` - Voice design sessions
- `ComplianceScan` - Scan results
- `OptimizationSuggestion` - Optimization suggestions
- `DailyFormStats` - Aggregated statistics
- `GeneratedContent` - AI-generated content cache
- `PersonalizationRule` - Personalization rules

## Environment Variables

Add these to your `.env` file:

```env
# OpenAI (for AI features)
OPENAI_API_KEY=sk-xxx

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1xxx

# Email
SENDGRID_API_KEY=xxx
# or
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=xxx
EMAIL_HOST_PASSWORD=xxx

# Integrations (optional)
SALESFORCE_CLIENT_ID=xxx
SALESFORCE_CLIENT_SECRET=xxx
HUBSPOT_API_KEY=xxx
MAILCHIMP_API_KEY=xxx
SLACK_BOT_TOKEN=xxx
STRIPE_SECRET_KEY=xxx
```

## Running Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## Starting Celery Workers

```bash
# Start Celery worker
celery -A backend worker -l info

# Start Celery beat (for scheduled tasks)
celery -A backend beat -l info
```

---

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install  # in frontend/
   ```

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Set environment variables**
   ```bash
   export OPENAI_API_KEY=sk-xxx
   ```

4. **Start services**
   ```bash
   # Backend
   python manage.py runserver

   # Frontend
   npm run dev

   # Celery (separate terminals)
   celery -A backend worker -l info
   celery -A backend beat -l info
   ```

5. **Access features**
   - Optimization: `Form Editor > Optimization tab`
   - Workflows: `Form Settings > Automations`
   - Compliance: `Form Settings > Compliance`
   - Integrations: `Settings > Integrations`
   - Analytics: `Dashboard > Predictive Analytics`
   - Voice Design: `Create Form > Voice Mode`
   - AI Content: `Form Editor > AI Assistant`
