"""
Integration Marketplace Service
Pre-built connectors for 50+ tools with one-click setup
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
import requests


class IntegrationMarketplaceService:
    """
    Service for managing integration marketplace.
    Provides pre-built connectors with OAuth and webhook support.
    """
    
    # Available integration categories
    CATEGORIES = [
        'crm',
        'email_marketing',
        'automation',
        'analytics',
        'payment',
        'storage',
        'communication',
        'project_management',
        'spreadsheet',
        'database',
    ]
    
    # Pre-built integrations catalog
    INTEGRATIONS = {
        # CRM
        'salesforce': {
            'name': 'Salesforce',
            'category': 'crm',
            'description': 'Sync leads and contacts with Salesforce CRM',
            'icon': 'salesforce.svg',
            'auth_type': 'oauth2',
            'oauth_config': {
                'authorize_url': 'https://login.salesforce.com/services/oauth2/authorize',
                'token_url': 'https://login.salesforce.com/services/oauth2/token',
                'scopes': ['api', 'refresh_token'],
            },
            'features': ['sync_leads', 'create_contacts', 'update_records', 'custom_objects'],
            'field_mapping': True,
            'popular': True,
        },
        'hubspot': {
            'name': 'HubSpot',
            'category': 'crm',
            'description': 'Create contacts and deals in HubSpot',
            'icon': 'hubspot.svg',
            'auth_type': 'oauth2',
            'oauth_config': {
                'authorize_url': 'https://app.hubspot.com/oauth/authorize',
                'token_url': 'https://api.hubapi.com/oauth/v1/token',
                'scopes': ['contacts', 'forms'],
            },
            'features': ['sync_contacts', 'create_deals', 'update_properties'],
            'field_mapping': True,
            'popular': True,
        },
        'pipedrive': {
            'name': 'Pipedrive',
            'category': 'crm',
            'description': 'Add people and deals to Pipedrive',
            'icon': 'pipedrive.svg',
            'auth_type': 'api_key',
            'features': ['create_person', 'create_deal', 'add_note'],
            'field_mapping': True,
        },
        'zoho_crm': {
            'name': 'Zoho CRM',
            'category': 'crm',
            'description': 'Sync leads with Zoho CRM',
            'icon': 'zoho.svg',
            'auth_type': 'oauth2',
            'features': ['create_lead', 'create_contact', 'create_deal'],
            'field_mapping': True,
        },
        
        # Email Marketing
        'mailchimp': {
            'name': 'Mailchimp',
            'category': 'email_marketing',
            'description': 'Add subscribers to Mailchimp lists',
            'icon': 'mailchimp.svg',
            'auth_type': 'oauth2',
            'oauth_config': {
                'authorize_url': 'https://login.mailchimp.com/oauth2/authorize',
                'token_url': 'https://login.mailchimp.com/oauth2/token',
            },
            'features': ['add_subscriber', 'update_subscriber', 'add_tags'],
            'field_mapping': True,
            'popular': True,
        },
        'convertkit': {
            'name': 'ConvertKit',
            'category': 'email_marketing',
            'description': 'Add subscribers to ConvertKit sequences',
            'icon': 'convertkit.svg',
            'auth_type': 'api_key',
            'features': ['add_subscriber', 'add_to_sequence', 'add_tag'],
            'field_mapping': True,
        },
        'sendinblue': {
            'name': 'Brevo (Sendinblue)',
            'category': 'email_marketing',
            'description': 'Add contacts to Brevo lists',
            'icon': 'brevo.svg',
            'auth_type': 'api_key',
            'features': ['add_contact', 'add_to_list', 'send_email'],
            'field_mapping': True,
        },
        'activecampaign': {
            'name': 'ActiveCampaign',
            'category': 'email_marketing',
            'description': 'Add contacts and trigger automations',
            'icon': 'activecampaign.svg',
            'auth_type': 'api_key',
            'features': ['add_contact', 'add_to_list', 'add_tag', 'trigger_automation'],
            'field_mapping': True,
        },
        
        # Automation
        'zapier': {
            'name': 'Zapier',
            'category': 'automation',
            'description': 'Connect to 5000+ apps via Zapier',
            'icon': 'zapier.svg',
            'auth_type': 'webhook',
            'features': ['send_webhook'],
            'popular': True,
        },
        'make': {
            'name': 'Make (Integromat)',
            'category': 'automation',
            'description': 'Trigger Make scenarios',
            'icon': 'make.svg',
            'auth_type': 'webhook',
            'features': ['send_webhook'],
        },
        'n8n': {
            'name': 'n8n',
            'category': 'automation',
            'description': 'Trigger n8n workflows',
            'icon': 'n8n.svg',
            'auth_type': 'webhook',
            'features': ['send_webhook'],
        },
        
        # Analytics
        'google_analytics': {
            'name': 'Google Analytics',
            'category': 'analytics',
            'description': 'Track form events in Google Analytics',
            'icon': 'google-analytics.svg',
            'auth_type': 'tracking_id',
            'features': ['track_view', 'track_submit', 'track_abandon'],
            'popular': True,
        },
        'mixpanel': {
            'name': 'Mixpanel',
            'category': 'analytics',
            'description': 'Track form events in Mixpanel',
            'icon': 'mixpanel.svg',
            'auth_type': 'api_key',
            'features': ['track_event', 'identify_user'],
        },
        'segment': {
            'name': 'Segment',
            'category': 'analytics',
            'description': 'Send form data to Segment',
            'icon': 'segment.svg',
            'auth_type': 'api_key',
            'features': ['track', 'identify', 'page'],
        },
        
        # Payment
        'stripe': {
            'name': 'Stripe',
            'category': 'payment',
            'description': 'Process payments with Stripe',
            'icon': 'stripe.svg',
            'auth_type': 'api_key',
            'features': ['create_payment_intent', 'create_subscription', 'create_customer'],
            'popular': True,
        },
        'paypal': {
            'name': 'PayPal',
            'category': 'payment',
            'description': 'Accept PayPal payments',
            'icon': 'paypal.svg',
            'auth_type': 'oauth2',
            'features': ['create_order', 'capture_payment'],
        },
        
        # Storage
        'google_drive': {
            'name': 'Google Drive',
            'category': 'storage',
            'description': 'Save files to Google Drive',
            'icon': 'google-drive.svg',
            'auth_type': 'oauth2',
            'features': ['upload_file', 'create_folder'],
        },
        'dropbox': {
            'name': 'Dropbox',
            'category': 'storage',
            'description': 'Save files to Dropbox',
            'icon': 'dropbox.svg',
            'auth_type': 'oauth2',
            'features': ['upload_file', 'create_folder'],
        },
        'aws_s3': {
            'name': 'Amazon S3',
            'category': 'storage',
            'description': 'Store files in AWS S3',
            'icon': 'aws-s3.svg',
            'auth_type': 'api_key',
            'features': ['upload_file', 'generate_presigned_url'],
        },
        
        # Communication
        'slack': {
            'name': 'Slack',
            'category': 'communication',
            'description': 'Send notifications to Slack channels',
            'icon': 'slack.svg',
            'auth_type': 'oauth2',
            'features': ['send_message', 'send_to_channel', 'send_dm'],
            'popular': True,
        },
        'discord': {
            'name': 'Discord',
            'category': 'communication',
            'description': 'Send notifications to Discord',
            'icon': 'discord.svg',
            'auth_type': 'webhook',
            'features': ['send_message', 'send_embed'],
        },
        'twilio': {
            'name': 'Twilio',
            'category': 'communication',
            'description': 'Send SMS notifications',
            'icon': 'twilio.svg',
            'auth_type': 'api_key',
            'features': ['send_sms', 'send_whatsapp'],
        },
        'telegram': {
            'name': 'Telegram',
            'category': 'communication',
            'description': 'Send messages to Telegram',
            'icon': 'telegram.svg',
            'auth_type': 'api_key',
            'features': ['send_message', 'send_to_channel'],
        },
        
        # Project Management
        'notion': {
            'name': 'Notion',
            'category': 'project_management',
            'description': 'Add entries to Notion databases',
            'icon': 'notion.svg',
            'auth_type': 'oauth2',
            'features': ['create_page', 'add_to_database'],
            'field_mapping': True,
            'popular': True,
        },
        'trello': {
            'name': 'Trello',
            'category': 'project_management',
            'description': 'Create cards in Trello',
            'icon': 'trello.svg',
            'auth_type': 'api_key',
            'features': ['create_card', 'add_to_list'],
            'field_mapping': True,
        },
        'asana': {
            'name': 'Asana',
            'category': 'project_management',
            'description': 'Create tasks in Asana',
            'icon': 'asana.svg',
            'auth_type': 'oauth2',
            'features': ['create_task', 'add_to_project'],
            'field_mapping': True,
        },
        'monday': {
            'name': 'Monday.com',
            'category': 'project_management',
            'description': 'Add items to Monday boards',
            'icon': 'monday.svg',
            'auth_type': 'api_key',
            'features': ['create_item', 'update_item'],
            'field_mapping': True,
        },
        'clickup': {
            'name': 'ClickUp',
            'category': 'project_management',
            'description': 'Create tasks in ClickUp',
            'icon': 'clickup.svg',
            'auth_type': 'api_key',
            'features': ['create_task', 'add_to_list'],
            'field_mapping': True,
        },
        
        # Spreadsheet
        'google_sheets': {
            'name': 'Google Sheets',
            'category': 'spreadsheet',
            'description': 'Add rows to Google Sheets',
            'icon': 'google-sheets.svg',
            'auth_type': 'oauth2',
            'features': ['append_row', 'update_row', 'create_sheet'],
            'field_mapping': True,
            'popular': True,
        },
        'airtable': {
            'name': 'Airtable',
            'category': 'spreadsheet',
            'description': 'Add records to Airtable bases',
            'icon': 'airtable.svg',
            'auth_type': 'api_key',
            'features': ['create_record', 'update_record'],
            'field_mapping': True,
            'popular': True,
        },
        'excel_online': {
            'name': 'Excel Online',
            'category': 'spreadsheet',
            'description': 'Add rows to Excel spreadsheets',
            'icon': 'excel.svg',
            'auth_type': 'oauth2',
            'features': ['append_row', 'update_row'],
            'field_mapping': True,
        },
        
        # Database
        'supabase': {
            'name': 'Supabase',
            'category': 'database',
            'description': 'Insert data into Supabase',
            'icon': 'supabase.svg',
            'auth_type': 'api_key',
            'features': ['insert_row', 'update_row', 'upsert'],
            'field_mapping': True,
        },
        'firebase': {
            'name': 'Firebase',
            'category': 'database',
            'description': 'Add documents to Firestore',
            'icon': 'firebase.svg',
            'auth_type': 'api_key',
            'features': ['add_document', 'update_document'],
            'field_mapping': True,
        },
    }
    
    def get_catalog(
        self,
        category: str = None,
        search: str = None,
    ) -> List[Dict[str, Any]]:
        """Get integration catalog with optional filtering"""
        integrations = []
        
        for key, config in self.INTEGRATIONS.items():
            if category and config['category'] != category:
                continue
            
            if search:
                search_lower = search.lower()
                if (search_lower not in config['name'].lower() and 
                    search_lower not in config['description'].lower()):
                    continue
            
            integrations.append({
                'id': key,
                **config,
            })
        
        # Sort by popularity and name
        integrations.sort(key=lambda x: (not x.get('popular', False), x['name']))
        
        return integrations
    
    def get_integration(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get integration details"""
        if integration_id in self.INTEGRATIONS:
            return {
                'id': integration_id,
                **self.INTEGRATIONS[integration_id],
            }
        return None
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories with counts"""
        category_counts = {}
        for config in self.INTEGRATIONS.values():
            cat = config['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return [
            {
                'id': cat,
                'name': cat.replace('_', ' ').title(),
                'count': category_counts.get(cat, 0),
            }
            for cat in self.CATEGORIES
        ]
    
    def install_integration(
        self,
        form,
        integration_id: str,
        credentials: Dict[str, Any],
        config: Dict[str, Any] = None,
    ) -> 'FormIntegration':
        """Install an integration for a form"""
        from forms.models_advanced import FormIntegration
        from integrations.encryption import encrypt_credentials
        
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f'Unknown integration: {integration_id}')
        
        # Encrypt credentials
        encrypted_creds = encrypt_credentials(credentials)
        
        # Create integration record
        form_integration = FormIntegration.objects.create(
            form=form,
            integration_type=integration_id,
            credentials=encrypted_creds,
            config=config or {},
            is_active=True,
        )
        
        return form_integration
    
    def uninstall_integration(self, form, integration_id: str) -> bool:
        """Uninstall an integration from a form"""
        from forms.models_advanced import FormIntegration
        
        try:
            FormIntegration.objects.filter(
                form=form,
                integration_type=integration_id,
            ).delete()
            return True
        except:
            return False
    
    def get_installed_integrations(self, form) -> List[Dict[str, Any]]:
        """Get all installed integrations for a form"""
        from forms.models_advanced import FormIntegration
        
        installed = FormIntegration.objects.filter(form=form)
        
        result = []
        for fi in installed:
            integration = self.get_integration(fi.integration_type)
            if integration:
                result.append({
                    'id': fi.id,
                    'integration_id': fi.integration_type,
                    'name': integration['name'],
                    'category': integration['category'],
                    'icon': integration['icon'],
                    'is_active': fi.is_active,
                    'config': fi.config,
                    'created_at': fi.created_at.isoformat(),
                })
        
        return result
    
    def execute_integration(
        self,
        form_integration: 'FormIntegration',
        submission,
        action: str = None,
    ) -> Dict[str, Any]:
        """Execute an integration action"""
        from integrations.encryption import decrypt_credentials
        
        integration_id = form_integration.integration_type
        credentials = decrypt_credentials(form_integration.credentials)
        config = form_integration.config
        data = submission.payload_json
        
        # Get connector
        connector = self._get_connector(integration_id)
        if not connector:
            return {'success': False, 'error': f'No connector for {integration_id}'}
        
        try:
            result = connector.execute(
                credentials=credentials,
                config=config,
                data=data,
                action=action,
            )
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_connector(self, integration_id: str) -> Optional['BaseConnector']:
        """Get connector instance for integration"""
        connectors = {
            'salesforce': SalesforceConnector(),
            'hubspot': HubspotConnector(),
            'mailchimp': MailchimpConnector(),
            'slack': SlackConnector(),
            'google_sheets': GoogleSheetsConnector(),
            'airtable': AirtableConnector(),
            'notion': NotionConnector(),
            'stripe': StripeConnector(),
            'zapier': WebhookConnector(),
            'make': WebhookConnector(),
            'discord': WebhookConnector(),
        }
        return connectors.get(integration_id)
    
    def get_oauth_url(
        self,
        integration_id: str,
        redirect_uri: str,
        state: str,
    ) -> Optional[str]:
        """Get OAuth authorization URL"""
        integration = self.get_integration(integration_id)
        if not integration or integration.get('auth_type') != 'oauth2':
            return None
        
        oauth_config = integration.get('oauth_config', {})
        authorize_url = oauth_config.get('authorize_url')
        
        if not authorize_url:
            return None
        
        client_id = getattr(settings, f'{integration_id.upper()}_CLIENT_ID', '')
        scopes = ' '.join(oauth_config.get('scopes', []))
        
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scopes,
            'state': state,
        }
        
        query = '&'.join(f'{k}={v}' for k, v in params.items())
        return f'{authorize_url}?{query}'
    
    def exchange_oauth_code(
        self,
        integration_id: str,
        code: str,
        redirect_uri: str,
    ) -> Dict[str, Any]:
        """Exchange OAuth code for tokens"""
        integration = self.get_integration(integration_id)
        if not integration:
            return {'error': 'Unknown integration'}
        
        oauth_config = integration.get('oauth_config', {})
        token_url = oauth_config.get('token_url')
        
        if not token_url:
            return {'error': 'No token URL configured'}
        
        client_id = getattr(settings, f'{integration_id.upper()}_CLIENT_ID', '')
        client_secret = getattr(settings, f'{integration_id.upper()}_CLIENT_SECRET', '')
        
        response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
        })
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': response.text}


class BaseConnector:
    """Base class for integration connectors"""
    
    def execute(
        self,
        credentials: Dict,
        config: Dict,
        data: Dict,
        action: str = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError


class SalesforceConnector(BaseConnector):
    """Salesforce integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        access_token = credentials.get('access_token')
        instance_url = credentials.get('instance_url')
        object_type = config.get('object_type', 'Lead')
        
        # Map fields
        field_mapping = config.get('field_mapping', {})
        sf_data = {}
        for form_field, sf_field in field_mapping.items():
            if form_field in data:
                sf_data[sf_field] = data[form_field]
        
        url = f"{instance_url}/services/data/v57.0/sobjects/{object_type}/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(url, json=sf_data, headers=headers)
        
        if response.status_code == 201:
            return {'success': True, 'id': response.json().get('id')}
        else:
            return {'success': False, 'error': response.text}


class HubspotConnector(BaseConnector):
    """HubSpot integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        api_key = credentials.get('api_key') or credentials.get('access_token')
        
        # Map fields
        field_mapping = config.get('field_mapping', {})
        properties = {}
        for form_field, hs_field in field_mapping.items():
            if form_field in data:
                properties[hs_field] = data[form_field]
        
        url = 'https://api.hubapi.com/crm/v3/objects/contacts'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(url, json={'properties': properties}, headers=headers)
        
        if response.status_code == 201:
            return {'success': True, 'id': response.json().get('id')}
        else:
            return {'success': False, 'error': response.text}


class MailchimpConnector(BaseConnector):
    """Mailchimp integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        api_key = credentials.get('api_key')
        server = api_key.split('-')[-1] if api_key else ''
        list_id = config.get('list_id')
        
        email = data.get('email')
        if not email:
            return {'success': False, 'error': 'No email in submission'}
        
        # Map fields to merge fields
        field_mapping = config.get('field_mapping', {})
        merge_fields = {}
        for form_field, mc_field in field_mapping.items():
            if form_field in data and form_field != 'email':
                merge_fields[mc_field] = data[form_field]
        
        url = f'https://{server}.api.mailchimp.com/3.0/lists/{list_id}/members'
        
        subscriber_data = {
            'email_address': email,
            'status': 'subscribed',
            'merge_fields': merge_fields,
        }
        
        response = requests.post(
            url,
            json=subscriber_data,
            auth=('anystring', api_key),
        )
        
        if response.status_code in [200, 201]:
            return {'success': True, 'id': response.json().get('id')}
        else:
            return {'success': False, 'error': response.text}


class SlackConnector(BaseConnector):
    """Slack integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        webhook_url = credentials.get('webhook_url')
        channel = config.get('channel')
        message_template = config.get('message_template', 'New form submission received')
        
        # Format message
        message = message_template
        for key, value in data.items():
            message = message.replace(f'{{{key}}}', str(value))
        
        payload = {
            'text': message,
        }
        if channel:
            payload['channel'] = channel
        
        response = requests.post(webhook_url, json=payload)
        
        return {'success': response.status_code == 200}


class GoogleSheetsConnector(BaseConnector):
    """Google Sheets integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        access_token = credentials.get('access_token')
        spreadsheet_id = config.get('spreadsheet_id')
        sheet_name = config.get('sheet_name', 'Sheet1')
        
        # Map fields to columns
        field_mapping = config.get('field_mapping', {})
        row_data = []
        for form_field in field_mapping.keys():
            row_data.append(str(data.get(form_field, '')))
        
        # Add timestamp
        row_data.append(datetime.now().isoformat())
        
        url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}:append'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        params = {
            'valueInputOption': 'USER_ENTERED',
            'insertDataOption': 'INSERT_ROWS',
        }
        
        response = requests.post(
            url,
            json={'values': [row_data]},
            headers=headers,
            params=params,
        )
        
        if response.status_code == 200:
            return {'success': True, 'updated_range': response.json().get('updates', {}).get('updatedRange')}
        else:
            return {'success': False, 'error': response.text}


class AirtableConnector(BaseConnector):
    """Airtable integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        api_key = credentials.get('api_key')
        base_id = config.get('base_id')
        table_name = config.get('table_name')
        
        # Map fields
        field_mapping = config.get('field_mapping', {})
        fields = {}
        for form_field, at_field in field_mapping.items():
            if form_field in data:
                fields[at_field] = data[form_field]
        
        url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(url, json={'fields': fields}, headers=headers)
        
        if response.status_code == 200:
            return {'success': True, 'id': response.json().get('id')}
        else:
            return {'success': False, 'error': response.text}


class NotionConnector(BaseConnector):
    """Notion integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        api_key = credentials.get('api_key')
        database_id = config.get('database_id')
        
        # Map fields to properties
        field_mapping = config.get('field_mapping', {})
        properties = {}
        for form_field, notion_config in field_mapping.items():
            if form_field in data:
                prop_name = notion_config.get('name', form_field)
                prop_type = notion_config.get('type', 'rich_text')
                value = data[form_field]
                
                if prop_type == 'title':
                    properties[prop_name] = {'title': [{'text': {'content': str(value)}}]}
                elif prop_type == 'rich_text':
                    properties[prop_name] = {'rich_text': [{'text': {'content': str(value)}}]}
                elif prop_type == 'email':
                    properties[prop_name] = {'email': str(value)}
                elif prop_type == 'phone_number':
                    properties[prop_name] = {'phone_number': str(value)}
                elif prop_type == 'number':
                    properties[prop_name] = {'number': float(value) if value else 0}
        
        url = 'https://api.notion.com/v1/pages'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28',
        }
        
        response = requests.post(
            url,
            json={
                'parent': {'database_id': database_id},
                'properties': properties,
            },
            headers=headers,
        )
        
        if response.status_code == 200:
            return {'success': True, 'id': response.json().get('id')}
        else:
            return {'success': False, 'error': response.text}


class StripeConnector(BaseConnector):
    """Stripe payment integration connector"""
    
    def execute(self, credentials, config, data, action=None):
        import stripe
        
        stripe.api_key = credentials.get('secret_key')
        
        amount = config.get('amount') or data.get('amount', 0)
        currency = config.get('currency', 'usd')
        
        try:
            # Create customer
            customer = stripe.Customer.create(
                email=data.get('email'),
                name=data.get('name'),
            )
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),
                currency=currency,
                customer=customer.id,
                metadata={'form_submission': 'true'},
            )
            
            return {
                'success': True,
                'customer_id': customer.id,
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class WebhookConnector(BaseConnector):
    """Generic webhook connector for Zapier, Make, etc."""
    
    def execute(self, credentials, config, data, action=None):
        webhook_url = credentials.get('webhook_url') or config.get('webhook_url')
        
        if not webhook_url:
            return {'success': False, 'error': 'No webhook URL configured'}
        
        # Add metadata
        payload = {
            'timestamp': datetime.now().isoformat(),
            'data': data,
        }
        
        # Add custom headers if configured
        headers = config.get('headers', {})
        headers['Content-Type'] = 'application/json'
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=30,
        )
        
        return {
            'success': response.status_code < 400,
            'status_code': response.status_code,
        }


class IntegrationFieldMapper:
    """Helper for mapping form fields to integration fields"""
    
    @staticmethod
    def suggest_mappings(
        form_fields: List[Dict],
        integration_fields: List[Dict],
    ) -> Dict[str, str]:
        """Suggest field mappings based on names"""
        mappings = {}
        
        # Common field name variations
        variations = {
            'email': ['email', 'email_address', 'e-mail', 'emailaddress'],
            'name': ['name', 'full_name', 'fullname', 'firstname', 'first_name'],
            'phone': ['phone', 'phone_number', 'telephone', 'mobile'],
            'company': ['company', 'company_name', 'organization', 'org'],
        }
        
        for form_field in form_fields:
            form_name = form_field.get('label', '').lower().replace(' ', '_')
            
            for int_field in integration_fields:
                int_name = int_field.get('name', '').lower()
                
                # Direct match
                if form_name == int_name:
                    mappings[form_field['id']] = int_field['id']
                    break
                
                # Variation match
                for key, vars in variations.items():
                    if any(v in form_name for v in vars) and any(v in int_name for v in vars):
                        mappings[form_field['id']] = int_field['id']
                        break
        
        return mappings
