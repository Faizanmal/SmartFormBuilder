# Conversational Forms & Automated Reporting

## Overview
This document covers the implementation of conversational/chatbot-style forms with AI and automated reporting features added to SmartFormBuilder.

## ✅ Features Implemented

### 1. Conversational Forms with AI

#### Core Features
- **Chatbot-Style Interface**: Natural conversation flow for form completion
- **AI-Powered Question Generation**: Uses OpenAI GPT-4 to create conversational questions
- **Voice Input Support**: Speech-to-text using OpenAI Whisper
- **Text-to-Speech**: Reads questions aloud using OpenAI TTS
- **Smart Response Parsing**: AI understands natural language answers
- **Fuzzy Matching**: Matches user responses to select/radio options
- **Auto-Completion Suggestions**: AI-powered field completion
- **Voice Commands**: Navigate forms with voice (next, back, submit, etc.)
- **Progress Tracking**: Visual progress indicator
- **Conversation History**: Full Q&A history saved

#### Technical Implementation

**Backend Services:**

1. **ConversationalFormService** (`forms/services/conversational_service.py`):
   - `generate_next_question()`: AI generates natural questions
   - `parse_user_response()`: Validates and parses natural language input
   - `_match_option()`: Fuzzy matching for select fields
   - `generate_summary()`: AI creates friendly completion summary
   - `auto_complete_field()`: Smart field suggestions

2. **VoiceInputService** (`forms/services/voice_service.py`):
   - `transcribe_audio()`: OpenAI Whisper transcription
   - `text_to_speech()`: OpenAI TTS conversion
   - `enable_voice_commands()`: Voice navigation
   - `validate_voice_input()`: Validates transcribed input

**Database Models:**

```python
class ConversationalSession(models.Model):
    """Tracks conversational form sessions"""
    form = ForeignKey to Form
    session_token = CharField (unique)
    conversation_history = JSONField (Q&A pairs)
    collected_data = JSONField (form data)
    current_field_id = CharField
    is_complete = BooleanField
    completed_at = DateTimeField
    ip_address, user_agent, timestamps
```

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/advanced/conversational/start_conversation/` | POST | Start new conversation session |
| `/api/advanced/conversational/respond/` | POST | Submit response to current question |
| `/api/advanced/conversational/voice_input/` | POST | Process voice input |
| `/api/advanced/conversational/text_to_speech/` | POST | Convert text to speech |
| `/api/advanced/conversational/session_history/` | GET | Get conversation history |

**Frontend Component:**

`ConversationalForm.tsx` - React component with:
- Real-time chat interface
- Voice recording/playback
- Progress tracking
- Auto-scroll messages
- Loading states
- Error handling

#### Usage Example

**Start a Conversational Form:**

```python
# Backend
POST /api/advanced/conversational/start_conversation/
{
    "form_id": "form-uuid"
}

# Response
{
    "session_token": "session-uuid",
    "question": {
        "question": "Hey! What's your name?",
        "field_id": "name",
        "field_type": "text"
    },
    "form_title": "Contact Form"
}
```

**Submit a Response:**

```python
POST /api/advanced/conversational/respond/
{
    "session_token": "session-uuid",
    "response": "My name is John Smith"
}

# Response
{
    "complete": false,
    "question": {
        "question": "Great to meet you, John! What's your email address?",
        "field_id": "email",
        "field_type": "email"
    },
    "progress": 0.33
}
```

**Voice Input:**

```python
POST /api/advanced/conversational/voice_input/
{
    "session_token": "session-uuid",
    "audio_data": "data:audio/webm;base64,...",
    "audio_format": "webm"
}

# Response
{
    "transcription": "john at example dot com",
    "question": {...},
    "progress": 0.66
}
```

**React Usage:**

```tsx
import { ConversationalForm } from '@/components/ConversationalForm';

export function MyPage() {
  return (
    <ConversationalForm
      formId="form-uuid"
      enableVoice={true}
      onComplete={(data) => {
        console.log('Form completed:', data);
      }}
    />
  );
}
```

---

### 2. Automated Reporting & Exports

#### Core Features
- **Scheduled Reports**: Daily, weekly, monthly automatic reports
- **Email Delivery**: HTML + plain text reports via email
- **Multiple Export Formats**: CSV, JSON, Tableau, Power BI
- **Comprehensive Metrics**: All analytics in one report
- **BI Tool Integration**: Ready for Tableau/Power BI import
- **Ad-hoc Reports**: Generate reports on-demand
- **Trend Analysis**: Period-over-period comparison
- **Report Attachments**: JSON data attached to emails
- **Custom Report Options**: Configure what to include
- **Recipient Management**: Multiple email recipients

#### Technical Implementation

**Backend Service:**

**ReportingService** (`forms/services/reporting_service.py`):

```python
# Generate comprehensive report
generate_form_report(form, date_from, date_to, report_type='summary')

# Send via email
send_report_email(report, recipients, include_charts=True)

# Schedule recurring report
schedule_report(form, 'weekly', ['admin@example.com'], options)

# Export for BI tools
export_to_bi_format(report, format_type='tableau')
```

**Database Model:**

```python
class ScheduledReport(models.Model):
    """Scheduled report configuration"""
    form = ForeignKey to Form
    schedule_type = CharField (daily/weekly/monthly)
    recipients = ArrayField of EmailField
    report_options = JSONField
    is_active = BooleanField
    next_run = DateTimeField
    last_run = DateTimeField
    timestamps
```

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/advanced/reports/` | GET | List scheduled reports |
| `/api/advanced/reports/` | POST | Create scheduled report |
| `/api/advanced/reports/{id}/` | PUT/PATCH | Update scheduled report |
| `/api/advanced/reports/{id}/` | DELETE | Delete scheduled report |
| `/api/advanced/reports/generate_report/` | POST | Generate ad-hoc report |
| `/api/advanced/reports/export_report/` | POST | Export report (CSV/JSON/BI) |
| `/api/advanced/reports/send_report_email/` | POST | Send report via email |
| `/api/advanced/reports/{id}/toggle_active/` | POST | Enable/disable report |
| `/api/advanced/reports/{id}/run_now/` | POST | Manually trigger report |

#### Report Structure

```json
{
  "form": {
    "id": "form-uuid",
    "title": "Contact Form",
    "slug": "contact-form"
  },
  "period": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-31T23:59:59Z"
  },
  "summary": {
    "total_views": 5000,
    "total_starts": 3500,
    "total_submissions": 2000,
    "conversion_rate": 40.0,
    "trend": 15.5
  },
  "funnel": {
    "views": 5000,
    "starts": 3500,
    "submits": 2000,
    "view_to_start_rate": 70.0,
    "start_to_submit_rate": 57.1,
    "overall_conversion": 40.0,
    "drop_off_at_start": 1500,
    "drop_off_after_start": 1500
  },
  "field_analytics": [
    {
      "field_id": "email",
      "field_label": "Email",
      "interactions": 3400,
      "completion_rate": 97.1,
      "avg_time_spent": 8.5,
      "drop_off_rate": 2.9
    }
  ],
  "devices": [
    {"device_type": "desktop", "count": 3000, "percentage": 60.0},
    {"device_type": "mobile", "count": 1500, "percentage": 30.0},
    {"device_type": "tablet", "count": 500, "percentage": 10.0}
  ],
  "geography": [
    {"country": "US", "count": 2500},
    {"country": "UK", "count": 1000}
  ],
  "time_series": {
    "views": [
      {"period": "2024-01-01", "count": 150},
      {"period": "2024-01-02", "count": 165}
    ],
    "submissions": [
      {"period": "2024-01-01", "count": 60},
      {"period": "2024-01-02", "count": 70}
    ]
  },
  "generated_at": "2024-01-31T12:00:00Z"
}
```

#### Usage Examples

**Create Scheduled Report:**

```python
POST /api/advanced/reports/
{
    "form": "form-uuid",
    "schedule_type": "weekly",
    "recipients": ["admin@example.com", "manager@example.com"],
    "report_options": {
        "include_charts": true,
        "include_field_analytics": true
    }
}
```

**Generate Ad-hoc Report:**

```python
POST /api/advanced/reports/generate_report/
{
    "form_id": "form-uuid",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "report_type": "detailed"
}
```

**Export for BI Tools:**

```python
POST /api/advanced/reports/export_report/
{
    "form_id": "form-uuid",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "format": "tableau"  # or "csv", "powerbi", "json"
}

# Returns file download
Content-Type: application/json
Content-Disposition: attachment; filename="report_contact-form_tableau.json"
```

**Send Report via Email:**

```python
POST /api/advanced/reports/send_report_email/
{
    "form_id": "form-uuid",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "recipients": ["admin@example.com"],
    "include_charts": true
}
```

---

## Background Tasks

**New Celery Task Added:**

```python
@shared_task
def send_scheduled_reports():
    """
    Process and send all scheduled reports that are due
    Runs every hour
    """
    # Finds reports where next_run <= now
    # Generates report for appropriate time period
    # Sends emails to all recipients
    # Updates next_run and last_run timestamps
```

**Celery Beat Schedule Updated:**

```python
'send-scheduled-reports': {
    'task': 'forms.tasks.send_scheduled_reports',
    'schedule': crontab(minute=0),  # Every hour
}
```

---

## Environment Variables

Add to `.env`:

```bash
# OpenAI API (required for conversational forms)
OPENAI_API_KEY=sk-...

# Email settings (for reports)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@yourapp.com
```

---

## Database Migrations

```bash
# Apply new migrations
python manage.py migrate

# This creates 2 new tables:
# - conversational_sessions
# - scheduled_reports
```

---

## Testing

### Test Conversational Forms:

```python
# 1. Start conversation
curl -X POST http://localhost:8000/api/advanced/conversational/start_conversation/ \
  -H "Content-Type: application/json" \
  -d '{"form_id": "your-form-id"}'

# 2. Respond to questions
curl -X POST http://localhost:8000/api/advanced/conversational/respond/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_token": "session-token-from-step-1",
    "response": "John Smith"
  }'
```

### Test Reporting:

```python
# 1. Generate report
curl -X POST http://localhost:8000/api/advanced/reports/generate_report/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "form_id": "your-form-id",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z"
  }'

# 2. Schedule report
curl -X POST http://localhost:8000/api/advanced/reports/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "form": "your-form-id",
    "schedule_type": "weekly",
    "recipients": ["admin@example.com"]
  }'
```

---

## Export Formats

### CSV Export
- Time series data (date, views, submissions)
- Summary metrics as key-value pairs
- Easily importable into Excel/Google Sheets

### JSON Export
- Full report structure
- Nested data preserved
- Ready for custom processing

### Tableau Export
- Flattened data structure
- Metrics as rows (metric, date, value)
- Optimized for Tableau data source

### Power BI Export
- Similar to Tableau format
- Compatible with Power BI's expected structure
- Supports all report metrics

---

## AI Capabilities

### Natural Language Understanding
- Understands variations: "john@example.com", "john at example dot com"
- Parses numbers from text: "I want 5" → 5
- Extracts phone numbers: "(555) 123-4567" → "5551234567"
- Boolean responses: "yes", "yeah", "sure" → true

### Smart Question Generation
- Context-aware questions
- Conversational tone
- Refers to previous answers
- Adapts to user's language style

### Voice Processing
- Real-time transcription
- Multiple language support (configurable)
- Voice command recognition
- Natural-sounding TTS output

---

## Performance Considerations

1. **OpenAI API Calls**: Each question generation uses API credits
2. **Voice Transcription**: Whisper API calls for audio processing
3. **TTS Generation**: Text-to-speech API usage
4. **Report Generation**: Compute-intensive for large datasets
5. **Email Sending**: Rate limits on email service

**Optimization Tips:**
- Cache common question templates
- Use streaming for long conversations
- Batch report generation
- Queue email sending
- Implement rate limiting

---

## Security

1. **Session Tokens**: Unique UUIDs for each conversation
2. **IP Tracking**: Log IP addresses for audit
3. **Audio Data**: Temporary files deleted after processing
4. **Report Access**: Authenticated users only
5. **Email Sanitization**: Validate recipient addresses
6. **Data Encryption**: Sensitive data encrypted at rest

---

## Next Steps

This implementation provides the foundation for:
1. Multi-language conversational forms
2. Custom voice models
3. Advanced NLP for form completion
4. Predictive analytics in reports
5. Real-time report dashboards
6. Report templates and customization

---

## Files Created/Modified

**New Files:**
- `backend/forms/services/conversational_service.py` (300+ lines)
- `backend/forms/services/voice_service.py` (150+ lines)
- `backend/forms/services/reporting_service.py` (300+ lines)
- `backend/forms/views_conversational.py` (350+ lines)
- `backend/forms/migrations/0004_conversational_reporting.py`
- `backend/templates/emails/analytics_report.html`
- `frontend/src/components/ConversationalForm.tsx` (400+ lines)

**Modified Files:**
- `backend/forms/models_advanced.py` - Added 2 models
- `backend/forms/serializers_advanced.py` - Added 2 serializers
- `backend/forms/urls_advanced.py` - Added routes
- `backend/forms/tasks.py` - Added scheduled reports task
- `backend/backend/celery.py` - Added beat schedule entry

**Total New Code:** ~1,800 lines

---

## Support

For issues or questions:
- Check OpenAI API key configuration
- Verify Celery is running for scheduled reports
- Test voice permissions in browser
- Check email settings for report delivery

