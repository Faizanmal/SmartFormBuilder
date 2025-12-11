# Advanced Features Quick Reference

## 🌍 1. Multi-Language Support

```python
# Translate a form
from forms.services.i18n_service import I18nService
service = I18nService()
translated = service.translate_form(form_schema, target_language='es')

# Detect user language
lang = service.detect_language_from_browser(request.META.get('HTTP_ACCEPT_LANGUAGE'))
```

**Supported:** 13 languages including RTL (Arabic, Hebrew)

---

## 🔌 2. Integration Marketplace

```python
from forms.services.integration_marketplace_service import IntegrationMarketplaceService
service = IntegrationMarketplaceService()

# Salesforce
service.sync_to_salesforce(connection_data, submission_data)

# HubSpot
service.sync_to_hubspot(connection_data, submission_data)

# Custom Webhook
service.execute_webhook(url, method, headers, payload_template, submission_data)

# IFTTT Workflow
service.execute_workflow(workflow_id, trigger_data)
```

**Connectors:** Salesforce, HubSpot, Mailchimp, Slack, Trello, Google Sheets

---

## ⏰ 3. Form Scheduling

```python
from forms.services.scheduling_service import SchedulingService
service = SchedulingService()

# Schedule activation
service.schedule_form_activation(form_id, start_date, end_date, max_submissions=100)

# Create recurring form
service.create_recurring_form(
    template_form_id, 
    frequency='weekly',
    interval=1,
    naming_pattern='{title} - Week {week}'
)
```

**Features:** Scheduled activation, expiration, recurring forms, conditional triggers

---

## 🎨 4. Custom Themes

```python
from forms.services.theme_service import ThemeService
service = ThemeService()

# Create theme
service.create_theme(user, name, colors, typography, layout)

# Apply to form
service.apply_theme_to_form(form_id, theme_id, overrides)

# Search marketplace
themes = service.search_marketplace_themes(min_rating=4.0)
```

**Features:** Visual editor, WCAG validation, brand guidelines, marketplace

---

## 🔒 5. Security & Compliance

```python
from forms.services.security_service import SecurityService
service = SecurityService()

# 2FA Setup
result = service.setup_2fa(user, method='totp')

# Encrypt data
encrypted = service.encrypt_submission(submission_data)

# GDPR Request
service.create_privacy_request(email, request_type='export')

# Security Scan
scan = service.scan_submission_for_threats(submission_data)
```

**Features:** 2FA, SSO, E2E encryption, GDPR/CCPA tools, IP controls, threat detection

---

## 👥 6. Real-Time Collaboration

```javascript
// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/form/FORM-UUID/');

// Send change
ws.send(JSON.stringify({
    type: 'form_change',
    change: {field_id: 'email', new_value: {...}}
}));

// Receive updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update UI
};
```

```python
from forms.services.realtime_service import CollaborationService
service = CollaborationService()

# Add comment
service.add_comment(form_id, user, field_id, content, mentions)

# Submit for review
service.submit_for_review(form_id, user, reviewers)
```

**Features:** Live editing, cursors, comments, @mentions, review workflows

---

## 🤖 7. Predictive Completion

```python
from forms.services.realtime_service import PredictiveService
service = PredictiveService()

# Predict field value
prediction = service.predict_field_value(form_id, field_id, context_data)

# Calculate completion
progress = service.calculate_completion_prediction(
    form_id, session_id, filled_fields, total_fields
)
```

**Features:** AI predictions, auto-fill, smart defaults, progressive disclosure

---

## 📱 8. Mobile Optimization

```python
from forms.services.realtime_service import MobileService
service = MobileService()

# Queue offline submission
service.queue_offline_submission(form_id, device_id, submission_data)

# Send push notification
service.send_push_notification(subscription_id, title, body, data)

# Track analytics
service.track_mobile_analytics(form_id, device_info, metrics)
```

**Features:** Touch UI, camera/QR, offline mode, push notifications, geolocation

---

## 🚀 Quick Setup

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Start services
celery -A backend worker -l info &
celery -A backend beat -l info &
daphne -b 0.0.0.0 -p 8000 backend.asgi:application &
redis-server &
```

---

## 📊 Automated Tasks (Celery Beat)

| Task | Frequency | Purpose |
|------|-----------|---------|
| check_scheduled_forms | Every 5 min | Activate scheduled forms |
| check_expired_forms | Hourly | Expire/archive forms |
| process_recurring_forms | Daily | Create recurring instances |
| sync_offline_submissions | Every 10 min | Sync mobile submissions |
| retry_failed_webhooks | Every 30 min | Retry integration failures |
| refresh_oauth_tokens | Daily | Refresh expiring OAuth tokens |
| cleanup_old_edit_sessions | Hourly | Clean inactive sessions |

---

## 🗂️ Key Models

### Internationalization
- `Language`, `FormTranslation`, `SubmissionTranslation`

### Integrations
- `IntegrationProvider`, `IntegrationConnection`, `IntegrationWorkflow`, `WebhookEndpoint`

### Scheduling
- `FormSchedule`, `RecurringForm`, `FormLifecycleEvent`

### Themes
- `Theme`, `FormTheme`, `ThemeRating`, `BrandGuideline`

### Security
- `TwoFactorAuth`, `SSOProvider`, `EncryptedSubmission`, `DataPrivacyRequest`, `SecurityAuditLog`

### Collaboration
- `FormCollaborator`, `FormEditSession`, `FormChange`, `FormComment`, `FormReviewWorkflow`

### Predictive
- `FieldPrediction`, `SmartDefault`, `CompletionPrediction`, `ProgressiveDisclosure`

### Mobile
- `MobileOptimization`, `OfflineSubmission`, `PushNotificationSubscription`, `GeolocationField`

---

## 🔧 Environment Variables

```bash
OPENAI_API_KEY=sk-...                    # For AI translations
REDIS_URL=redis://localhost:6379/0      # For Channels & Celery
VAPID_PUBLIC_KEY=...                     # For push notifications
VAPID_PRIVATE_KEY=...                    # For push notifications
```

---

## 📖 Full Documentation

See [ADVANCED_FEATURES_IMPLEMENTATION.md](./ADVANCED_FEATURES_IMPLEMENTATION.md) for comprehensive documentation.

---

## 🧪 Testing

```bash
# Test all features
python manage.py test forms

# Test specific feature
python manage.py test forms.tests.test_i18n
python manage.py test forms.tests.test_collaboration
```

---

## 🎯 Use Cases

1. **Global Forms**: Multi-language forms for international audiences
2. **CRM Integration**: Auto-sync leads to Salesforce/HubSpot
3. **Event Registration**: Scheduled forms with automatic expiration
4. **Brand Compliance**: Custom themes with brand guidelines
5. **Secure Healthcare**: HIPAA-compliant with E2E encryption
6. **Team Collaboration**: Multiple designers editing forms simultaneously
7. **Smart Forms**: AI-powered field predictions to boost completion
8. **Field Surveys**: Mobile-optimized with offline support and geolocation

---

## ⚡ Performance Tips

- Cache translated forms
- Use Redis for WebSocket scalability
- Batch process offline submissions
- Pre-compute common predictions
- Index frequently queried fields
- Enable database query optimization

---

## 🛡️ Security Checklist

- ✅ Enable 2FA for admins
- ✅ Encrypt sensitive fields
- ✅ Configure IP restrictions
- ✅ Monitor audit logs
- ✅ Validate webhook signatures
- ✅ Sanitize custom CSS/JS
- ✅ Rotate OAuth tokens

---

## 📞 Support

For issues or questions:
1. Check model docstrings
2. Review service documentation
3. Examine Celery task logs
4. Test WebSocket with wscat
