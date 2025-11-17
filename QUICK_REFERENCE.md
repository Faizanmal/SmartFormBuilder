# 🚀 SmartFormBuilder - Developer Quick Reference

## Common Commands

### Development
```bash
# Backend
cd backend && python manage.py runserver

# Frontend  
cd frontend && npm run dev

# Celery Worker
cd backend && celery -A backend worker -l info

# Create Superuser
cd backend && python manage.py createsuperuser
```

### Database
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (CAUTION)
python manage.py flush
```

## API Quick Reference

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -d '{"email":"user@example.com","password":"pass"}'

# Returns: {"access":"TOKEN","refresh":"REFRESH"}
```

### Forms
```bash
# List forms
curl http://localhost:8000/api/v1/forms/ \
  -H "Authorization: Bearer TOKEN"

# Create form
curl -X POST http://localhost:8000/api/v1/forms/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title":"My Form","schema_json":{}}'

# Publish form
curl -X POST http://localhost:8000/api/v1/forms/{id}/publish/ \
  -H "Authorization: Bearer TOKEN"

# Get versions
curl http://localhost:8000/api/v1/forms/{id}/versions/ \
  -H "Authorization: Bearer TOKEN"

# Revert version
curl -X POST http://localhost:8000/api/v1/forms/{id}/revert/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"version_id":"VERSION_UUID"}'
```

### Submissions
```bash
# List submissions
curl http://localhost:8000/api/v1/forms/{id}/submissions/ \
  -H "Authorization: Bearer TOKEN"

# Public submit (no auth)
curl -X POST http://localhost:8000/api/public/submit/{slug}/ \
  -d '{"payload":{"name":"John","email":"john@example.com"}}'

# Export to CSV
curl -X POST http://localhost:8000/api/v1/forms/{id}/submissions/export/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"format":"csv"}' \
  -o submissions.csv

# Export to Excel
curl -X POST http://localhost:8000/api/v1/forms/{id}/submissions/export/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"format":"xlsx"}' \
  -o submissions.xlsx
```

### Notifications
```bash
# List notifications
curl http://localhost:8000/api/v1/forms/{id}/notifications/ \
  -H "Authorization: Bearer TOKEN"

# Create notification
curl -X POST http://localhost:8000/api/v1/forms/{id}/notifications/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "type":"email",
    "trigger":"on_submit",
    "recipient":"admin@example.com",
    "subject":"New submission",
    "template":"Name: {{name}}"
  }'
```

### AI Generation
```bash
# Generate form
curl -X POST http://localhost:8000/api/v1/generate/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "prompt":"Create a contact form",
    "context":"Business website"
  }'
```

## Schema Examples

### Basic Form
```json
{
  "title": "Contact Form",
  "description": "Get in touch",
  "fields": [
    {"id":"f_1","type":"text","label":"Name","required":true},
    {"id":"f_2","type":"email","label":"Email","required":true},
    {"id":"f_3","type":"textarea","label":"Message"}
  ],
  "logic": [],
  "settings": {}
}
```

### Form with Conditional Logic
```json
{
  "title": "Service Request",
  "fields": [
    {
      "id":"f_1",
      "type":"select",
      "label":"Service Type",
      "options":["Web","Mobile"],
      "required":true
    },
    {"id":"f_2","type":"text","label":"Website URL"},
    {"id":"f_3","type":"text","label":"App Platform"}
  ],
  "logic": [
    {
      "if":{"field":"f_1","operator":"equals","value":"Web"},
      "show":["f_2"],
      "hide":["f_3"]
    },
    {
      "if":{"field":"f_1","operator":"equals","value":"Mobile"},
      "show":["f_3"],
      "hide":["f_2"]
    }
  ]
}
```

### Notification Template
```json
{
  "type": "email",
  "trigger": "on_submit",
  "recipient": "admin@example.com",
  "subject": "New submission from {{name}}",
  "template": "Name: {{name}}\nEmail: {{email}}\nMessage: {{message}}\n\nSubmitted at: {{submitted_at}}"
}
```

## Embed Code

### Basic Embed
```html
<div id="form"></div>
<script src="http://localhost:3000/embed.js"></script>
<script>
  FormForge.embed({
    slug: 'contact-form',
    container: '#form'
  });
</script>
```

### Advanced Embed
```html
<div id="form"></div>
<script src="http://localhost:3000/embed.js"></script>
<script>
  FormForge.embed({
    slug: 'contact-form',
    container: '#form',
    theme: 'light',
    width: '100%',
    height: '600px',
    prefill: {
      email: 'user@example.com',
      name: 'John Doe'
    },
    hideFields: ['internal_notes'],
    onSubmit: function(data) {
      console.log('Submitted:', data);
      alert('Thank you!');
    },
    onReady: function() {
      console.log('Form ready');
    },
    onError: function(err) {
      console.error('Error:', err);
    }
  });
</script>
```

## React Component Usage

### Form Builder
```tsx
import { FormBuilder } from '@/components/FormBuilder';

export default function BuilderPage() {
  const handleSave = async (schema: any) => {
    const response = await fetch('/api/v1/forms/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: schema.title,
        description: schema.description,
        schema_json: schema
      })
    });
    const data = await response.json();
    console.log('Form created:', data);
  };

  return (
    <FormBuilder
      initialSchema={existingSchema}
      onSave={handleSave}
    />
  );
}
```

## Python Service Usage

### Conditional Logic
```python
from forms.services.conditional_logic import ConditionalLogicEngine

# Check visible fields
visible_fields = ConditionalLogicEngine.get_visible_fields(
    schema=form.schema_json,
    submission_data={'service_type': 'Web'}
)

# Validate submission
is_valid, errors = ConditionalLogicEngine.validate_submission(
    schema=form.schema_json,
    submission_data=request.data
)
```

### Export Service
```python
from forms.services.export_service import SubmissionExporter

# Get submissions
submissions = Submission.objects.filter(form=form)
submissions_data = [SubmissionExporter.flatten_submission(s) for s in submissions]

# Export to CSV
csv_data = SubmissionExporter.to_csv(submissions_data, ['email', 'name'])

# Export to XLSX
xlsx_bytes = SubmissionExporter.to_xlsx(submissions_data)
```

### Notifications
```python
from forms.services.notification_service import NotificationService

# Send email
NotificationService.send_email(
    recipient='admin@example.com',
    subject='Test Email',
    body='This is a test'
)

# Process submission notifications
NotificationService.process_submission_notifications(submission, form)
```

## Environment Variables

### Backend (.env)
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost/db
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_test_...
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_EMBED_BASE_URL=http://localhost:3000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret
```

## Field Types

| Type | Description | Options |
|------|-------------|---------|
| text | Single-line text | - |
| email | Email validation | - |
| phone | Phone number | - |
| number | Numeric input | min, max, step |
| textarea | Multi-line text | rows |
| date | Date picker | - |
| time | Time picker | - |
| select | Dropdown | options[] |
| multiselect | Multiple choice dropdown | options[] |
| radio | Radio buttons | options[] |
| checkbox | Single checkbox | - |
| file | File upload | accept, maxSize |
| payment | Payment field | amount, currency |
| url | URL validation | - |

## Conditional Operators

| Operator | Description | Example |
|----------|-------------|---------|
| equals | Exact match | `{"field":"f_1","operator":"equals","value":"Yes"}` |
| not_equals | Not equal to | `{"field":"f_1","operator":"not_equals","value":"No"}` |
| in | Value in list | `{"field":"f_1","operator":"in","value":["A","B"]}` |
| contains | Contains substring/item | `{"field":"f_1","operator":"contains","value":"test"}` |
| gte | Greater than or equal | `{"field":"age","operator":"gte","value":18}` |
| lte | Less than or equal | `{"field":"age","operator":"lte","value":65}` |
| gt | Greater than | `{"field":"score","operator":"gt","value":50}` |
| lt | Less than | `{"field":"score","operator":"lt","value":100}` |
| is_empty | Field is empty | `{"field":"f_1","operator":"is_empty"}` |
| is_not_empty | Field has value | `{"field":"f_1","operator":"is_not_empty"}` |

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
sudo service postgresql start
```

### Migration Issues
```bash
# Show current migrations
python manage.py showmigrations

# Fake migration (if already applied manually)
python manage.py migrate --fake forms

# Squash migrations
python manage.py squashmigrations forms 0001 0002
```

### CORS Errors
Add to `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Redis Connection Error
```bash
# Start Redis
redis-server

# Test connection
redis-cli ping
```

## Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test forms

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing Checklist
- [ ] Create form with builder
- [ ] Add conditional logic
- [ ] Submit form publicly
- [ ] Export submissions (CSV/Excel)
- [ ] Set up email notification
- [ ] Embed form on test page
- [ ] Test version history
- [ ] Test revert functionality

## Useful Snippets

### Create Test Data
```python
from forms.models import Form, Submission
from users.models import User

user = User.objects.first()

form = Form.objects.create(
    user=user,
    title="Test Form",
    schema_json={
        "fields": [
            {"id":"f_1","type":"text","label":"Name","required":True},
            {"id":"f_2","type":"email","label":"Email","required":True}
        ]
    }
)

submission = Submission.objects.create(
    form=form,
    payload_json={"f_1":"John Doe","f_2":"john@example.com"}
)
```

### Debug Query
```python
# Show SQL queries
from django.db import connection
print(connection.queries)

# Enable query logging
import logging
logging.basicConfig()
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)
```

---

**Quick Links:**
- Full Documentation: `FEATURES.md`
- Implementation Details: `IMPLEMENTATION_SUMMARY.md`
- Setup Script: `./setup.sh`
