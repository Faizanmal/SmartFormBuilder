#!/bin/bash

# SmartFormBuilder Advanced Features Setup Script
# This script sets up all the new advanced features

set -e

echo "========================================="
echo "SmartFormBuilder Advanced Features Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}Error: Please activate your Python virtual environment first${NC}"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo -e "${BLUE}Step 1: Installing new dependencies...${NC}"
pip install -r backend/requirements.txt

echo ""
echo -e "${BLUE}Step 2: Running migrations...${NC}"
cd backend
python manage.py makemigrations
python manage.py migrate

echo ""
echo -e "${BLUE}Step 3: Creating initial language data...${NC}"
python manage.py shell << EOF
from forms.models_i18n import Language

languages = [
    ('en', 'English', 'English', False, '🇺🇸'),
    ('es', 'Spanish', 'Español', False, '🇪🇸'),
    ('fr', 'French', 'Français', False, '🇫🇷'),
    ('de', 'German', 'Deutsch', False, '🇩🇪'),
    ('it', 'Italian', 'Italiano', False, '🇮🇹'),
    ('pt', 'Portuguese', 'Português', False, '🇵🇹'),
    ('ar', 'Arabic', 'العربية', True, '🇸🇦'),
    ('he', 'Hebrew', 'עברית', True, '🇮🇱'),
    ('zh', 'Chinese', '中文', False, '🇨🇳'),
    ('ja', 'Japanese', '日本語', False, '🇯🇵'),
    ('ko', 'Korean', '한국어', False, '🇰🇷'),
    ('ru', 'Russian', 'Русский', False, '🇷🇺'),
    ('hi', 'Hindi', 'हिन्दी', False, '🇮🇳'),
]

for code, name, native, rtl, flag in languages:
    Language.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'native_name': native,
            'is_rtl': rtl,
            'flag_emoji': flag,
            'is_active': True
        }
    )
    print(f"✓ Created language: {name}")

print("\nTotal languages created: {Language.objects.count()}")
EOF

echo ""
echo -e "${BLUE}Step 4: Creating sample integration providers...${NC}"
python manage.py shell << EOF
from forms.models_integrations_marketplace import IntegrationProvider
from django.utils.text import slugify

providers = [
    {
        'name': 'Salesforce',
        'category': 'crm',
        'description': 'Sync form submissions to Salesforce CRM',
        'api_base_url': 'https://login.salesforce.com',
        'auth_type': 'oauth',
        'is_premium': True
    },
    {
        'name': 'HubSpot',
        'category': 'crm',
        'description': 'Add contacts to HubSpot CRM',
        'api_base_url': 'https://api.hubapi.com',
        'auth_type': 'api_key',
        'is_premium': False
    },
    {
        'name': 'Mailchimp',
        'category': 'email',
        'description': 'Add subscribers to Mailchimp lists',
        'api_base_url': 'https://api.mailchimp.com',
        'auth_type': 'api_key',
        'is_premium': False
    },
    {
        'name': 'Slack',
        'category': 'communication',
        'description': 'Send form submissions to Slack channels',
        'api_base_url': 'https://slack.com/api',
        'auth_type': 'oauth',
        'is_premium': False
    },
    {
        'name': 'Trello',
        'category': 'productivity',
        'description': 'Create Trello cards from submissions',
        'api_base_url': 'https://api.trello.com',
        'auth_type': 'api_key',
        'is_premium': False
    },
    {
        'name': 'Google Sheets',
        'category': 'storage',
        'description': 'Sync submissions to Google Sheets',
        'api_base_url': 'https://sheets.googleapis.com',
        'auth_type': 'oauth',
        'is_premium': False
    },
]

for provider_data in providers:
    provider_data['slug'] = slugify(provider_data['name'])
    IntegrationProvider.objects.get_or_create(
        slug=provider_data['slug'],
        defaults=provider_data
    )
    print(f"✓ Created integration: {provider_data['name']}")

print(f"\nTotal integrations: {IntegrationProvider.objects.count()}")
EOF

echo ""
echo -e "${BLUE}Step 5: Creating sample theme...${NC}"
python manage.py shell << EOF
from forms.models_themes import Theme
from users.models import User

# Get or create admin user
admin_user = User.objects.filter(is_superuser=True).first()

if admin_user:
    Theme.objects.get_or_create(
        name='Default Professional',
        user=admin_user,
        defaults={
            'description': 'Clean, professional theme for business forms',
            'is_public': True,
            'colors': {
                'primary': '#3B82F6',
                'secondary': '#8B5CF6',
                'accent': '#10B981',
                'background': '#FFFFFF',
                'surface': '#F3F4F6',
                'text': '#111827',
                'textSecondary': '#6B7280',
                'error': '#EF4444',
                'success': '#10B981',
                'warning': '#F59E0B'
            },
            'typography': {
                'fontFamily': 'Inter, sans-serif',
                'headingFont': 'Poppins, sans-serif',
                'fontSize': '16px',
                'headingSizes': {'h1': '2rem', 'h2': '1.5rem', 'h3': '1.25rem'}
            },
            'layout': {
                'borderRadius': '8px',
                'spacing': 'medium',
                'containerWidth': '800px',
                'fieldSpacing': '20px'
            },
            'components': {
                'button': {'style': 'solid', 'size': 'medium'},
                'input': {'variant': 'outlined', 'size': 'medium'},
                'card': {'shadow': 'medium', 'border': True}
            }
        }
    )
    print("✓ Created default theme")
else:
    print("⚠ No admin user found. Skipping theme creation.")
EOF

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Start Redis server:"
echo "   redis-server"
echo ""
echo "2. Start Celery worker (in a new terminal):"
echo "   celery -A backend worker -l info"
echo ""
echo "3. Start Celery Beat for scheduled tasks (in a new terminal):"
echo "   celery -A backend beat -l info"
echo ""
echo "4. Start the ASGI server with WebSocket support:"
echo "   daphne -b 0.0.0.0 -p 8000 backend.asgi:application"
echo ""
echo "   OR for development:"
echo "   python manage.py runserver"
echo ""
echo -e "${BLUE}Environment Variables to Set:${NC}"
echo "OPENAI_API_KEY=your-openai-key-here          # For AI translations"
echo "REDIS_URL=redis://localhost:6379/0           # For Channels & Celery"
echo "VAPID_PUBLIC_KEY=your-vapid-public-key       # For push notifications"
echo "VAPID_PRIVATE_KEY=your-vapid-private-key     # For push notifications"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "- Full Guide: ADVANCED_FEATURES_IMPLEMENTATION.md"
echo "- Quick Ref:  ADVANCED_FEATURES_QUICK_REFERENCE.md"
echo "- Status:     IMPLEMENTATION_STATUS.md"
echo ""
echo -e "${GREEN}All advanced features are now ready to use!${NC}"
