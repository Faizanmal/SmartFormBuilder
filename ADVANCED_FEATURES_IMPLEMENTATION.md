# Advanced Features Implementation Guide

This document provides comprehensive documentation for the 8 new advanced features implemented in SmartFormBuilder.

## Table of Contents
1. [Multi-Language Support & Internationalization (i18n)](#1-multi-language-support--internationalization)
2. [Advanced Third-Party Integrations Marketplace](#2-advanced-third-party-integrations-marketplace)
3. [Form Scheduling & Lifecycle Management](#3-form-scheduling--lifecycle-management)
4. [Custom Themes & Branding Engine](#4-custom-themes--branding-engine)
5. [Advanced Security & Compliance Suite](#5-advanced-security--compliance-suite)
6. [Collaborative Form Design with Real-Time Editing](#6-collaborative-form-design-with-real-time-editing)
7. [Predictive Form Completion & Smart Defaults](#7-predictive-form-completion--smart-defaults)
8. [Mobile-Optimized Form Experiences](#8-mobile-optimized-form-experiences)

---

## 1. Multi-Language Support & Internationalization

### Overview
Enable forms to be displayed in multiple languages with automatic translation, RTL support, and language detection.

### Models
- `Language`: Supported languages database
- `FormTranslation`: Store translations for form content
- `SubmissionTranslation`: Translated submission exports

### Service: `I18nService`

#### Key Features
```python
from forms.services.i18n_service import I18nService

service = I18nService()

# Translate entire form
translated_schema = service.translate_form(
    form_schema={'title': 'Contact Form', 'fields': [...]},
    target_language='es',
    source_language='en'
)

# Detect language from browser
language = service.detect_language_from_browser(request.META.get('HTTP_ACCEPT_LANGUAGE'))

# Detect language from IP
language = service.detect_language_from_ip('123.45.67.89')

# Get RTL languages
rtl_langs = service.get_rtl_languages()  # ['ar', 'he']
```

#### Supported Languages
- English (en), Spanish (es), French (fr), German (de), Italian (it)
- Portuguese (pt), Arabic (ar), Hebrew (he), Chinese (zh), Japanese (ja)
- Korean (ko), Russian (ru), Hindi (hi)

#### RTL Support
Forms automatically adjust layout for right-to-left languages (Arabic, Hebrew).

---

## 2. Advanced Third-Party Integrations Marketplace

### Overview
Pre-built connectors for popular CRMs, email marketing tools, and productivity apps with custom webhook support.

### Models
- `IntegrationProvider`: Available integration providers
- `IntegrationConnection`: User's connections to services
- `IntegrationWorkflow`: IFTTT-style automation workflows
- `WebhookEndpoint`: Custom webhook configurations
- `IntegrationTemplate`: Pre-built integration templates

### Service: `IntegrationMarketplaceService`

#### CRM Integrations
```python
from forms.services.integration_marketplace_service import IntegrationMarketplaceService

service = IntegrationMarketplaceService()

# Salesforce
result = service.sync_to_salesforce(
    connection_data={'access_token': '...', 'instance_url': '...'},
    submission_data={'firstName': 'John', 'email': 'john@example.com'}
)

# HubSpot
result = service.sync_to_hubspot(
    connection_data={'api_key': '...'},
    submission_data={'email': 'john@example.com', 'firstName': 'John'}
)
```

#### Email Marketing
```python
# Mailchimp
result = service.add_to_mailchimp(
    connection_data={'api_key': '...', 'list_id': '...'},
    submission_data={'email': 'john@example.com', 'firstName': 'John'}
)
```

#### Productivity Apps
```python
# Slack
result = service.create_slack_message(
    connection_data={'webhook_url': '...'},
    submission_data={'email': 'john@example.com'}
)

# Trello
result = service.create_trello_card(
    connection_data={'api_key': '...', 'token': '...', 'list_id': '...'},
    submission_data={'email': 'john@example.com'}
)

# Google Sheets
result = service.sync_to_google_sheets(
    connection_data={'spreadsheet_id': '...', 'credentials': {...}},
    submission_data={'email': 'john@example.com'}
)
```

#### Custom Webhooks
```python
# Execute webhook with custom template
result = service.execute_webhook(
    url='https://api.example.com/webhook',
    method='POST',
    headers={'Authorization': 'Bearer token'},
    payload_template='{"email": "{{ email }}", "name": "{{ firstName }} {{ lastName }}"}',
    submission_data={'email': 'john@example.com', 'firstName': 'John'},
    timeout=30
)
```

#### IFTTT-Style Workflows
```python
# Execute workflow
result = service.execute_workflow(
    workflow_id='uuid-here',
    trigger_data={'email': 'john@example.com'}
)
```

---

## 3. Form Scheduling & Lifecycle Management

### Overview
Schedule forms to go live/expire, create recurring forms, and automate lifecycle management.

### Models
- `FormSchedule`: Scheduling configuration
- `RecurringForm`: Recurring form templates
- `FormLifecycleEvent`: Audit trail of lifecycle events

### Service: `SchedulingService`

#### Schedule Form Activation
```python
from forms.services.scheduling_service import SchedulingService
from datetime import datetime, timedelta

service = SchedulingService()

# Schedule form
result = service.schedule_form_activation(
    form_id='uuid-here',
    start_date=datetime.now() + timedelta(days=7),
    end_date=datetime.now() + timedelta(days=30),
    timezone_str='America/New_York',
    max_submissions=100
)
```

#### Recurring Forms
```python
# Create weekly survey
result = service.create_recurring_form(
    template_form_id='uuid-here',
    frequency='weekly',
    interval=1,  # Every 1 week
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=365),
    day_of_week=0,  # Monday
    auto_publish=True,
    naming_pattern='{title} - Week {week}'
)
```

#### Conditional Activation
Forms can activate based on conditions:
- Another form reaching X submissions
- Specific date/time
- Custom business logic

#### Automated Tasks
Celery tasks automatically:
- Activate scheduled forms (every 5 minutes)
- Expire forms (every hour)
- Create recurring forms (daily)
- Auto-archive inactive forms (weekly)

---

## 4. Custom Themes & Branding Engine

### Overview
Visual theme builder with color schemes, typography, custom CSS/JS, and theme marketplace.

### Models
- `Theme`: Theme definitions
- `FormTheme`: Theme application to forms
- `ThemeRating`: User ratings for marketplace themes
- `BrandGuideline`: Brand consistency rules

### Service: `ThemeService`

#### Create Theme
```python
from forms.services.theme_service import ThemeService

service = ThemeService()

result = service.create_theme(
    user=request.user,
    name='Corporate Blue',
    colors={
        'primary': '#3B82F6',
        'secondary': '#8B5CF6',
        'background': '#FFFFFF',
        'text': '#111827'
    },
    typography={
        'fontFamily': 'Inter, sans-serif',
        'fontSize': '16px'
    },
    layout={
        'borderRadius': '8px',
        'containerWidth': '800px'
    }
)
```

#### Apply Theme to Form
```python
result = service.apply_theme_to_form(
    form_id='uuid-here',
    theme_id='theme-uuid',
    overrides={
        'colors': {'primary': '#FF5733'}  # Override primary color
    }
)
```

#### Theme Validation
Automatic validation for:
- WCAG AA contrast ratios (4.5:1 minimum)
- Brand guideline compliance
- Security scanning of custom CSS/JS

#### Theme Marketplace
```python
# Search themes
themes = service.search_marketplace_themes(
    category='business',
    min_rating=4.0,
    is_premium=False
)

# Rate theme
result = service.rate_theme(
    theme_id='uuid-here',
    user=request.user,
    rating=5,
    review='Great theme!'
)
```

---

## 5. Advanced Security & Compliance Suite

### Overview
2FA, SSO, end-to-end encryption, GDPR/CCPA tools, IP controls, and security scanning.

### Models
- `TwoFactorAuth`: 2FA settings
- `SSOProvider`: SSO configurations
- `EncryptedSubmission`: Encrypted data storage
- `DataPrivacyRequest`: GDPR/CCPA requests
- `ConsentTracking`: User consent records
- `SecurityAuditLog`: Security event logging
- `IPAccessControl`: IP-based restrictions
- `SecurityScan`: Malicious submission detection

### Service: `SecurityService`

#### Two-Factor Authentication
```python
from forms.services.security_service import SecurityService

service = SecurityService()

# Setup 2FA
result = service.setup_2fa(user=request.user, method='totp')
# Returns: secret, provisioning_uri (for QR code), backup_codes

# Verify 2FA code
is_valid = service.verify_2fa_code(user=request.user, code='123456')
```

#### Data Encryption
```python
# Encrypt submission
result = service.encrypt_submission(
    submission_data={'email': 'john@example.com', 'ssn': '123-45-6789'}
)
# Returns: encrypted_data, encryption_key

# Decrypt submission
data = service.decrypt_submission(
    encrypted_data=result['encrypted_data'],
    key=result['encryption_key']
)
```

#### GDPR/CCPA Compliance
```python
# Create privacy request
result = service.create_privacy_request(
    email='user@example.com',
    request_type='export',  # or 'deletion', 'rectification'
    reason='GDPR data export request'
)

# Process data export
result = service.process_data_export(request_id='uuid-here')
# Returns download URL valid for 7 days
```

#### Security Scanning
```python
# Scan submission for threats
scan_result = service.scan_submission_for_threats({
    'comment': '<script>alert("XSS")</script>',
    'name': "admin' OR '1'='1"
})
# Returns: is_malicious, risk_score, threats_detected, should_block
```

#### IP Access Control
```python
# Check IP access
result = service.check_ip_access(
    form_id='uuid-here',
    ip_address='192.168.1.1'
)
# Returns: allowed, reason
```

---

## 6. Collaborative Form Design with Real-Time Editing

### Overview
Google Docs-style real-time collaboration with cursors, comments, review workflows, and conflict resolution.

### Models
- `FormCollaborator`: Collaboration permissions
- `FormEditSession`: Active editing sessions
- `FormChange`: Change tracking
- `FormComment`: Field comments
- `FormReviewWorkflow`: Approval workflows
- `ConflictResolution`: Merge conflict handling

### WebSocket Consumer: `FormCollaborationConsumer`

#### Real-Time Editing
Connect via WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/form/FORM-UUID/');

// Send change
ws.send(JSON.stringify({
    type: 'form_change',
    change: {
        field_id: 'email',
        change_type: 'field_updated',
        new_value: {label: 'Email Address'}
    }
}));

// Receive changes from others
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'form_change') {
        // Update UI with change from other user
    }
};
```

#### Service: `CollaborationService`
```python
from forms.services.realtime_service import CollaborationService

service = CollaborationService()

# Start edit session
result = service.start_edit_session(
    form_id='uuid-here',
    user=request.user,
    session_id='session-uuid'
)

# Add comment
result = service.add_comment(
    form_id='uuid-here',
    user=request.user,
    field_id='email',
    content='Should we make this required?',
    mentions=['user-uuid-1', 'user-uuid-2']
)

# Submit for review
result = service.submit_for_review(
    form_id='uuid-here',
    user=request.user,
    reviewers=['reviewer-uuid-1', 'reviewer-uuid-2']
)
```

#### Review Workflows
Forms go through: Draft → In Review → Changes Requested/Approved → Published

---

## 7. Predictive Form Completion & Smart Defaults

### Overview
AI-powered field predictions, auto-fill, smart defaults, and progressive disclosure.

### Models
- `UserSubmissionHistory`: Historical submission patterns
- `FieldPrediction`: Prediction rules
- `AutoFillTemplate`: Auto-fill configurations
- `SmartDefault`: Default value sources
- `CompletionPrediction`: Progress predictions
- `ProgressiveDisclosure`: Field disclosure rules

### Service: `PredictiveService`

#### Field Value Prediction
```python
from forms.services.realtime_service import PredictiveService

service = PredictiveService()

# Predict city from ZIP code
result = service.predict_field_value(
    form_id='uuid-here',
    field_id='city',
    context_data={'zip_code': '10001'}
)
# Returns: predicted_value='New York', confidence=0.95

# Calculate completion prediction
result = service.calculate_completion_prediction(
    form_id='uuid-here',
    session_id='session-uuid',
    filled_fields=5,
    total_fields=10
)
# Returns: completion_percent=50, estimated_time_remaining=150
```

#### Smart Defaults
Configure in `SmartDefault` model:
- URL parameters: `?email=john@example.com`
- User profile data
- Cookies/localStorage
- Geolocation
- Previous submissions
- Calculated values

#### Progressive Disclosure
Hide advanced fields until basic ones are completed, improving form completion rates.

---

## 8. Mobile-Optimized Form Experiences

### Overview
Touch-optimized fields, camera integration, offline support, push notifications, and geolocation.

### Models
- `MobileOptimization`: Mobile configuration
- `GeolocationField`: Location data
- `OfflineSubmission`: Offline queue
- `PushNotificationSubscription`: Push notification subscriptions
- `FormNotification`: Notification records
- `MobileAnalytics`: Mobile usage analytics
- `QRCodeScan`: QR code scan tracking

### Service: `MobileService`

#### Offline Submission Queue
```python
from forms.services.realtime_service import MobileService

service = MobileService()

# Queue offline submission
result = service.queue_offline_submission(
    form_id='uuid-here',
    device_id='device-12345',
    submission_data={'email': 'john@example.com'}
)
```

Celery task automatically syncs queued submissions every 10 minutes.

#### Push Notifications
```python
# Send push notification
result = service.send_push_notification(
    subscription_id='uuid-here',
    title='Form Updated',
    body='The survey has been updated',
    data={'form_id': 'uuid-here', 'type': 'form_updated'}
)
```

#### Mobile Analytics
```python
# Track mobile analytics
service.track_mobile_analytics(
    form_id='uuid-here',
    device_info={
        'device_type': 'mobile',
        'os': 'iOS',
        'os_version': '16.0',
        'browser': 'Safari',
        'screen_resolution': '390x844'
    },
    metrics={
        'touch_interactions': 25,
        'swipe_actions': 5,
        'load_time_ms': 1200,
        'completion_time_s': 180,
        'session_id': 'session-uuid',
        'submitted': True
    }
)
```

#### Features
- **Touch Optimization**: Large buttons, swipe gestures
- **Camera Integration**: File upload via camera, QR code scanning
- **Offline Support**: Service worker caching, background sync
- **Geolocation**: Automatic location detection with map integration
- **PWA Features**: Installable, push notifications, offline mode

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Initial Data
```python
# Create supported languages
python manage.py shell
>>> from forms.models_i18n import Language
>>> Language.objects.create(code='en', name='English', native_name='English', is_rtl=False)
>>> Language.objects.create(code='es', name='Spanish', native_name='Español', is_rtl=False)
>>> Language.objects.create(code='ar', name='Arabic', native_name='العربية', is_rtl=True)
```

### 4. Start Celery Workers
```bash
# Start Celery worker
celery -A backend worker -l info

# Start Celery Beat (for scheduled tasks)
celery -A backend beat -l info
```

### 5. Start Channels/Daphne (WebSocket Support)
```bash
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

### 6. Start Redis (for Channels and Celery)
```bash
redis-server
```

---

## API Endpoints

All features are accessible via REST API endpoints. Create corresponding views and serializers as needed.

### Example Endpoint Structure
```
/api/forms/{id}/translations/
/api/forms/{id}/schedule/
/api/forms/{id}/theme/
/api/forms/{id}/collaborators/
/api/integrations/marketplace/
/api/integrations/workflows/
/api/themes/marketplace/
/api/security/2fa/setup/
/api/privacy/requests/
```

---

## Frontend Integration

### WebSocket Connection (React Example)
```javascript
import { useEffect, useState } from 'react';

function FormCollaborationComponent({ formId }) {
  const [ws, setWs] = useState(null);
  const [activeUsers, setActiveUsers] = useState([]);

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/form/${formId}/`);
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch(data.type) {
        case 'user_joined':
          setActiveUsers(prev => [...prev, data.user]);
          break;
        case 'form_change':
          // Update form with change
          break;
        case 'cursor_moved':
          // Show other user's cursor
          break;
      }
    };
    
    setWs(websocket);
    
    return () => websocket.close();
  }, [formId]);
  
  return (
    <div>
      <h3>Active Collaborators: {activeUsers.length}</h3>
      {/* Form editor UI */}
    </div>
  );
}
```

---

## Configuration

### Environment Variables
```bash
# OpenAI for translations
OPENAI_API_KEY=your-key-here

# Redis for Channels and Celery
REDIS_URL=redis://localhost:6379/0

# WebSocket Settings
ALLOWED_HOSTS=localhost,127.0.0.1

# VAPID Keys for Push Notifications
VAPID_PUBLIC_KEY=your-public-key
VAPID_PRIVATE_KEY=your-private-key
```

---

## Performance Considerations

- **Translations**: Cache translated forms to avoid repeated API calls
- **WebSockets**: Use Redis for channel layer scalability
- **Offline Sync**: Batch process submissions in background
- **Theme Compilation**: Cache compiled themes
- **Security Scans**: Run async for large submissions
- **Predictions**: Pre-compute common predictions

---

## Security Best Practices

1. **2FA**: Enforce for admin users
2. **Encryption**: Use for sensitive fields (SSN, credit cards)
3. **IP Controls**: Restrict forms to specific networks
4. **Audit Logs**: Monitor security events
5. **Webhook Security**: Validate webhook signatures
6. **Custom CSS/JS**: Sanitize and sandbox
7. **OAuth Tokens**: Rotate and encrypt

---

## Testing

```bash
# Run all tests
python manage.py test forms.tests

# Test specific feature
python manage.py test forms.tests.test_i18n
python manage.py test forms.tests.test_scheduling
python manage.py test forms.tests.test_collaboration
```

---

## Support & Documentation

For additional help:
- Check model docstrings for field descriptions
- Review service method documentation
- Examine Celery task configurations
- Test WebSocket endpoints with tools like wscat

---

## License

All features are part of the SmartFormBuilder platform.
