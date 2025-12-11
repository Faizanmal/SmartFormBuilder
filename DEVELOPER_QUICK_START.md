# 🚀 Quick Start Guide: Using the 8 Advanced Features

## Table of Contents
1. [Setup](#setup)
2. [Feature 1: Multi-Language (i18n)](#1-multi-language-i18n)
3. [Feature 2: Integration Marketplace](#2-integration-marketplace)
4. [Feature 3: Form Scheduling](#3-form-scheduling)
5. [Feature 4: Custom Themes](#4-custom-themes)
6. [Feature 5: Advanced Security](#5-advanced-security)
7. [Feature 6: Real-Time Collaboration](#6-real-time-collaboration)
8. [Feature 7: Predictive Analytics](#7-predictive-analytics)
9. [Feature 8: Mobile Optimization](#8-mobile-optimization)

---

## Setup

### 1. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Environment Variables
Create `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost:5432/smartformbuilder
```

### 3. Run Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 4. Start Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
cd backend
celery -A backend worker -l info

# Terminal 3: Celery Beat
cd backend
celery -A backend beat -l info

# Terminal 4: Backend (with WebSocket support)
cd backend
daphne -b 0.0.0.0 -p 8000 backend.asgi:application

# Terminal 5: Frontend
cd frontend
npm run dev
```

---

## 1. Multi-Language (i18n)

### Backend Usage

**Auto-translate a form:**
```python
from forms.services.i18n_service import I18nService

service = I18nService()
result = service.translate_form(
    form_id='form-uuid',
    target_language='es'  # Spanish
)
print(result['translation_id'])
```

**Detect language:**
```python
lang = service.detect_language_from_browser(
    accept_language='es-ES,es;q=0.9,en;q=0.8'
)
# Returns: 'es'
```

### Frontend Usage

```typescript
import { i18nAPI } from '@/lib/advancedFeaturesAPI';
import { LanguageSelector } from '@/components/features';

// In your component
function MyForm() {
  const [language, setLanguage] = useState('en');
  
  // Auto-translate
  const handleTranslate = async () => {
    await i18nAPI.autoTranslateForm('form-id', 'fr');
  };
  
  return (
    <LanguageSelector 
      formId="form-id"
      currentLanguage={language}
      onLanguageChange={setLanguage}
    />
  );
}
```

### API Endpoints
```bash
# Get all languages
GET /api/v1/languages/

# Get form translations
GET /api/v1/form-translations/?form=<form-id>

# Auto-translate
POST /api/v1/form-translations/auto_translate/
{
  "form_id": "form-uuid",
  "target_language": "es"
}
```

---

## 2. Integration Marketplace

### Backend Usage

**Sync to Salesforce:**
```python
from forms.services.integration_marketplace_service import IntegrationMarketplaceService

service = IntegrationMarketplaceService()
result = service.sync_to_salesforce(
    connection_id='conn-uuid',
    submission_id='sub-uuid'
)
```

**Execute webhook:**
```python
result = service.execute_webhook(
    webhook_id='webhook-uuid',
    data={'name': 'John', 'email': 'john@example.com'}
)
```

### Frontend Usage

```typescript
import { integrationAPI } from '@/lib/advancedFeaturesAPI';
import { IntegrationMarketplace } from '@/components/features';

// Get all providers
const providers = await integrationAPI.getProviders();

// Create connection
await integrationAPI.createConnection({
  provider: 'provider-id',
  name: 'My Salesforce',
  credentials: { /* OAuth tokens */ },
  is_active: true
});

// Test connection
const result = await integrationAPI.testConnection('connection-id');

// Use component
<IntegrationMarketplace formId="form-id" />
```

### API Endpoints
```bash
# Browse integrations
GET /api/v1/integration-providers/?category=crm

# Create connection
POST /api/v1/integration-connections/
{
  "provider": "provider-id",
  "name": "My Integration",
  "credentials": {}
}

# Create workflow
POST /api/v1/integration-workflows/
{
  "form": "form-id",
  "provider": "provider-id",
  "trigger": "on_submission",
  "actions": [...]
}
```

---

## 3. Form Scheduling

### Backend Usage

**Schedule form activation:**
```python
from forms.services.scheduling_service import SchedulingService

service = SchedulingService()
result = service.schedule_form_activation(
    form_id='form-uuid',
    activation_date='2024-01-15T10:00:00Z',
    expiration_date='2024-02-15T10:00:00Z',
    timezone='America/New_York'
)
```

**Create recurring form:**
```python
result = service.create_recurring_form(
    user_id='user-uuid',
    template_form_id='form-uuid',
    recurrence_pattern='weekly',
    recurrence_config={'day_of_week': 1},  # Monday
    start_date='2024-01-01',
    timezone='UTC'
)
```

### Frontend Usage

```typescript
import { schedulingAPI } from '@/lib/advancedFeaturesAPI';

// Create schedule
await schedulingAPI.createSchedule({
  form: 'form-id',
  activation_date: '2024-01-15T10:00:00Z',
  expiration_date: '2024-02-15T10:00:00Z',
  timezone: 'America/New_York'
});

// Create recurring form
await schedulingAPI.createRecurringForm({
  template_form: 'form-id',
  name: 'Weekly Survey',
  recurrence_pattern: 'weekly',
  start_date: '2024-01-01'
});
```

### API Endpoints
```bash
# Create schedule
POST /api/v1/form-schedules/
{
  "form": "form-id",
  "activation_date": "2024-01-15T10:00:00Z",
  "timezone": "America/New_York"
}

# Manual activation
POST /api/v1/form-schedules/<id>/activate_now/
```

---

## 4. Custom Themes

### Backend Usage

**Create theme:**
```python
from forms.services.theme_service import ThemeService

service = ThemeService()
result = service.create_theme(
    user_id='user-uuid',
    theme_data={
        'name': 'Corporate Blue',
        'colors': {
            'primary': '#0066CC',
            'secondary': '#004C99',
            ...
        },
        'typography': {...}
    }
)
```

**Validate contrast:**
```python
ratio = service.calculate_contrast_ratio('#0066CC', '#FFFFFF')
# Returns: 7.5 (passes WCAG AA)
```

### Frontend Usage

```typescript
import { themeAPI } from '@/lib/advancedFeaturesAPI';
import { ThemeBuilder } from '@/components/features';

// Create theme
const theme = await themeAPI.createTheme({
  name: 'My Theme',
  colors: {
    primary: '#3B82F6',
    secondary: '#8B5CF6',
    ...
  },
  typography: {...}
});

// Apply to form
await themeAPI.setFormTheme({
  form: 'form-id',
  theme: theme.id
});

// Use component
<ThemeBuilder formId="form-id" />
```

### API Endpoints
```bash
# Get all themes
GET /api/v1/themes/

# Create theme
POST /api/v1/themes/
{
  "name": "My Theme",
  "colors": {...},
  "typography": {...}
}

# Validate theme
POST /api/v1/themes/<id>/validate/

# Clone theme
POST /api/v1/themes/<id>/clone/
```

---

## 5. Advanced Security

### Backend Usage

**Setup 2FA:**
```python
from forms.services.security_service import SecurityService

service = SecurityService()
result = service.setup_2fa(user_id='user-uuid', method='totp')
# Returns QR code and backup codes
```

**Create GDPR request:**
```python
result = service.create_privacy_request(
    email='user@example.com',
    request_type='export'
)
```

**Encrypt submission:**
```python
result = service.encrypt_submission(
    submission_id='sub-uuid',
    encryption_key='user-key'
)
```

### Frontend Usage

```typescript
import { securityAPI } from '@/lib/advancedFeaturesAPI';

// Setup 2FA
const result = await securityAPI.setup2FA('totp');
console.log(result.qr_code_url); // Display QR code

// Verify code
await securityAPI.verify2FA(result.id, '123456');

// Create GDPR request
await securityAPI.createPrivacyRequest({
  email: 'user@example.com',
  request_type: 'export',
  description: 'Export my data'
});

// Get audit logs
const logs = await securityAPI.getAuditLogs();
```

### API Endpoints
```bash
# Setup 2FA
POST /api/v1/two-factor-auth/
{
  "method": "totp"
}

# Verify 2FA
POST /api/v1/two-factor-auth/<id>/verify/
{
  "code": "123456"
}

# GDPR request
POST /api/v1/privacy-requests/
{
  "email": "user@example.com",
  "request_type": "export"
}
```

---

## 6. Real-Time Collaboration

### Backend Usage

**Start edit session:**
```python
from forms.services.realtime_service import CollaborationService

service = CollaborationService()
session = service.start_edit_session(
    form_id='form-uuid',
    user_id='user-uuid'
)
```

**Sync change:**
```python
service.sync_change(
    form_id='form-uuid',
    user_id='user-uuid',
    change_data={'type': 'field_add', ...}
)
```

### Frontend Usage

```typescript
import { collaborationAPI } from '@/lib/advancedFeaturesAPI';
import { CollaborationPanel } from '@/components/features';

// WebSocket connection
const ws = new WebSocket(`ws://localhost:8000/ws/form/${formId}/`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'user_joined':
      console.log('User joined:', data.user);
      break;
    case 'form_change':
      console.log('Form changed:', data.change);
      break;
    case 'cursor_moved':
      console.log('Cursor at:', data.position);
      break;
  }
};

// Send change
ws.send(JSON.stringify({
  type: 'form_change',
  change: {
    type: 'field_edit',
    field_id: 'field-1',
    new_value: 'Updated label'
  }
}));

// Use component
<CollaborationPanel formId="form-id" />
```

### API Endpoints
```bash
# Get collaborators
GET /api/v1/form-collaborators/?form=<form-id>

# Invite collaborator
POST /api/v1/form-collaborators/
{
  "form": "form-id",
  "user": "user-id",
  "role": "editor"
}

# Add comment
POST /api/v1/form-comments/
{
  "form": "form-id",
  "content": "Great work!",
  "field_id": "field-1"
}

# WebSocket
ws://localhost:8000/ws/form/<form-id>/
```

---

## 7. Predictive Analytics

### Backend Usage

**Predict field value:**
```python
from forms.services.realtime_service import PredictiveService

service = PredictiveService()
result = service.predict_field_value(
    form_id='form-uuid',
    field_name='city',
    user_context={'zip_code': '10001'}
)
# Returns: {'predicted_value': 'New York'}
```

**Estimate completion:**
```python
result = service.estimate_completion_time(
    submission_id='sub-uuid'
)
# Returns: {'estimated_seconds': 120}
```

### Frontend Usage

```typescript
import { predictiveAPI } from '@/lib/advancedFeaturesAPI';

// Get prediction
const result = await predictiveAPI.predictFieldValue(
  'form-id',
  'city',
  { zip_code: '10001' }
);

// Create smart default
await predictiveAPI.createSmartDefault({
  form: 'form-id',
  field_name: 'country',
  default_value: 'USA',
  conditions: { geo_region: 'north_america' }
});

// Progressive disclosure
await predictiveAPI.createProgressiveDisclosure({
  form: 'form-id',
  field_name: 'show_if_yes',
  trigger_conditions: { previous_field: 'yes' },
  revealed_fields: ['field2', 'field3']
});
```

### API Endpoints
```bash
# Predict value
POST /api/v1/field-predictions/predict/
{
  "form_id": "form-id",
  "field_name": "city",
  "user_context": {"zip_code": "10001"}
}

# Create prediction rule
POST /api/v1/field-predictions/
{
  "form": "form-id",
  "field_name": "state",
  "prediction_type": "lookup",
  "prediction_rules": {...}
}
```

---

## 8. Mobile Optimization

### Backend Usage

**Configure mobile settings:**
```python
from forms.services.realtime_service import MobileService

service = MobileService()
result = service.configure_mobile_optimization(
    form_id='form-uuid',
    settings={
        'one_field_per_screen': True,
        'large_tap_targets': True,
        'offline_mode_enabled': True
    }
)
```

**Queue offline submission:**
```python
result = service.queue_offline_submission(
    user_id='user-uuid',
    form_id='form-uuid',
    data={'name': 'John', 'email': 'john@example.com'}
)
```

**Send push notification:**
```python
result = service.send_push_notification(
    user_id='user-uuid',
    title='New Form',
    body='A new form is available',
    data={'form_id': 'form-uuid'}
)
```

### Frontend Usage

```typescript
import { mobileAPI } from '@/lib/advancedFeaturesAPI';
import { MobileOptimizationPanel } from '@/components/features';

// Configure mobile settings
await mobileAPI.setMobileOptimization({
  form: 'form-id',
  one_field_per_screen: true,
  large_tap_targets: true,
  offline_mode_enabled: true
});

// Queue offline submission
if (!navigator.onLine) {
  await mobileAPI.createOfflineSubmission({
    form: 'form-id',
    data: formData
  });
}

// Subscribe to push notifications
const subscription = await navigator.serviceWorker.ready
  .then(reg => reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: VAPID_PUBLIC_KEY
  }));

await mobileAPI.subscribeToPush({
  endpoint: subscription.endpoint,
  p256dh_key: subscription.keys.p256dh,
  auth_key: subscription.keys.auth
});

// Use component
<MobileOptimizationPanel formId="form-id" />
```

### API Endpoints
```bash
# Configure mobile
POST /api/v1/mobile-optimizations/
{
  "form": "form-id",
  "one_field_per_screen": true,
  "offline_mode_enabled": true
}

# Queue offline submission
POST /api/v1/offline-submissions/
{
  "form": "form-id",
  "data": {...}
}

# Sync offline
POST /api/v1/offline-submissions/<id>/sync/

# Subscribe to push
POST /api/v1/push-subscriptions/
{
  "endpoint": "...",
  "p256dh_key": "...",
  "auth_key": "..."
}
```

---

## Common Patterns

### Error Handling
```typescript
try {
  const result = await api.someMethod();
  console.log('Success:', result);
} catch (error) {
  console.error('Error:', error.message);
  // Show user-friendly message
}
```

### Loading States
```typescript
const [loading, setLoading] = useState(false);

const handleAction = async () => {
  setLoading(true);
  try {
    await api.someMethod();
  } finally {
    setLoading(false);
  }
};
```

### Polling for Updates
```typescript
useEffect(() => {
  const interval = setInterval(async () => {
    const sessions = await collaborationAPI.getActiveSessions(formId);
    setActiveSessions(sessions);
  }, 5000);
  
  return () => clearInterval(interval);
}, [formId]);
```

---

## Troubleshooting

### WebSocket not connecting
- Ensure Daphne is running (not Django runserver)
- Check Redis is running
- Verify CHANNEL_LAYERS in settings.py

### Celery tasks not running
- Start Celery worker: `celery -A backend worker -l info`
- Start Celery beat: `celery -A backend beat -l info`
- Check Redis connection

### Translations not working
- Add OPENAI_API_KEY to .env
- Verify API key is valid
- Check Celery worker logs

### Push notifications not sending
- Generate VAPID keys: `npx web-push generate-vapid-keys`
- Add to .env
- Ensure service worker is registered

---

## Performance Tips

1. **Use pagination** for large lists
2. **Implement caching** for frequently accessed data
3. **Debounce** real-time updates
4. **Lazy load** components
5. **Use WebSocket** for real-time features (not polling)
6. **Index database fields** for better query performance
7. **Use Celery** for long-running tasks

---

## Security Best Practices

1. **Always validate** user input
2. **Use HTTPS** in production
3. **Enable CORS** properly
4. **Rate limit** API endpoints
5. **Sanitize** user-generated content
6. **Encrypt** sensitive data
7. **Use** environment variables for secrets
8. **Implement** proper authentication/authorization

---

## Resources

- Full API Documentation: `COMPLETE_IMPLEMENTATION_GUIDE.md`
- Model Documentation: Individual model files
- Service Documentation: Individual service files
- Frontend Components: `/components/features/`

---

**Happy Coding! 🎉**
