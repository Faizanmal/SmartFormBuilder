"""
Real-Time Form Personalization Service
Dynamically adapt forms based on user data from external sources
"""
import json
import hashlib
from typing import Dict, Any, List
from datetime import datetime
from django.core.cache import cache
from django.conf import settings
import requests
from openai import OpenAI


class PersonalizationService:
    """
    Service for real-time form personalization.
    Pulls user data from external sources and dynamically adapts forms.
    """
    
    CACHE_TTL = 3600  # 1 hour cache for external data
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
    
    def personalize_form(
        self, 
        form, 
        user_context: Dict[str, Any],
        data_sources: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a personalized version of the form schema
        
        Args:
            form: Form model instance
            user_context: User context (email, user_id, session data, etc.)
            data_sources: List of data source configurations
            
        Returns:
            Personalized form schema
        """
        schema = form.schema_json.copy()
        
        # Collect external data
        external_data = {}
        if data_sources:
            for source in data_sources:
                data = self._fetch_external_data(source, user_context)
                external_data.update(data)
        
        # Merge user context with external data
        personalization_data = {**user_context, **external_data}
        
        # Apply personalization rules
        schema = self._apply_field_personalization(schema, personalization_data)
        schema = self._apply_conditional_visibility(schema, personalization_data)
        schema = self._apply_prefill(schema, personalization_data)
        schema = self._apply_dynamic_options(schema, personalization_data)
        
        # Add personalization metadata
        schema['_personalization'] = {
            'applied': True,
            'timestamp': datetime.now().isoformat(),
            'data_sources': [s.get('name') for s in (data_sources or [])],
            'user_segments': self._identify_user_segments(personalization_data),
        }
        
        return schema
    
    def _fetch_external_data(
        self, 
        source: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fetch data from external source"""
        source_type = source.get('type')
        
        # Generate cache key
        cache_key = self._get_cache_key(source, user_context)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if source_type == 'api':
                data = self._fetch_from_api(source, user_context)
            elif source_type == 'crm':
                data = self._fetch_from_crm(source, user_context)
            elif source_type == 'database':
                data = self._fetch_from_database(source, user_context)
            elif source_type == 'csv':
                data = self._fetch_from_csv(source, user_context)
            else:
                data = {}
            
            # Cache the data
            cache.set(cache_key, data, self.CACHE_TTL)
            return data
            
        except Exception as e:
            print(f"Error fetching from {source_type}: {e}")
            return {}
    
    def _fetch_from_api(
        self, source: Dict, user_context: Dict
    ) -> Dict[str, Any]:
        """Fetch data from REST API"""
        url = source.get('url')
        method = source.get('method', 'GET')
        headers = source.get('headers', {})
        params = source.get('params', {})
        
        # Replace placeholders in URL/params
        for key in ['email', 'user_id', 'phone']:
            if key in user_context:
                url = url.replace(f'{{{key}}}', str(user_context[key]))
                params = {
                    k: v.replace(f'{{{key}}}', str(user_context[key])) if isinstance(v, str) else v
                    for k, v in params.items()
                }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            timeout=10,
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract data using path if specified
            if source.get('data_path'):
                for key in source['data_path'].split('.'):
                    data = data.get(key, {})
            return data
        
        return {}
    
    def _fetch_from_crm(
        self, source: Dict, user_context: Dict
    ) -> Dict[str, Any]:
        """Fetch data from CRM (Salesforce, HubSpot, etc.)"""
        crm_type = source.get('crm_type')
        email = user_context.get('email')
        
        if not email:
            return {}
        
        if crm_type == 'salesforce':
            return self._fetch_salesforce_contact(source, email)
        elif crm_type == 'hubspot':
            return self._fetch_hubspot_contact(source, email)
        elif crm_type == 'pipedrive':
            return self._fetch_pipedrive_contact(source, email)
        
        return {}
    
    def _fetch_salesforce_contact(self, source: Dict, email: str) -> Dict:
        """Fetch contact from Salesforce"""
        access_token = source.get('access_token')
        instance_url = source.get('instance_url')
        
        query = f"SELECT Id, Name, Title, Department, Industry, Company FROM Contact WHERE Email = '{email}'"
        url = f"{instance_url}/services/data/v57.0/query/"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(url, params={'q': query}, headers=headers)
        
        if response.status_code == 200:
            records = response.json().get('records', [])
            if records:
                return records[0]
        
        return {}
    
    def _fetch_hubspot_contact(self, source: Dict, email: str) -> Dict:
        """Fetch contact from HubSpot"""
        api_key = source.get('api_key')
        
        url = 'https://api.hubapi.com/crm/v3/objects/contacts/search'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'filterGroups': [{
                'filters': [{
                    'propertyName': 'email',
                    'operator': 'EQ',
                    'value': email,
                }]
            }],
            'properties': ['firstname', 'lastname', 'company', 'jobtitle', 'industry']
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                return results[0].get('properties', {})
        
        return {}
    
    def _fetch_pipedrive_contact(self, source: Dict, email: str) -> Dict:
        """Fetch contact from Pipedrive"""
        api_key = source.get('api_key')
        
        url = 'https://api.pipedrive.com/v1/persons/search'
        params = {
            'term': email,
            'api_token': api_key,
            'fields': 'email',
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            items = response.json().get('data', {}).get('items', [])
            if items:
                return items[0].get('item', {})
        
        return {}
    
    def _fetch_from_database(
        self, source: Dict, user_context: Dict
    ) -> Dict[str, Any]:
        """Fetch data from internal database lookup"""
        from forms.models import Submission
        
        lookup_field = source.get('lookup_field', 'email')
        lookup_value = user_context.get(lookup_field)
        
        if not lookup_value:
            return {}
        
        # Find previous submissions
        previous_submissions = Submission.objects.filter(
            form__owner=source.get('owner'),
            payload_json__contains={lookup_field: lookup_value}
        ).order_by('-created_at')[:5]
        
        if previous_submissions:
            # Merge data from previous submissions
            merged_data = {}
            for sub in reversed(previous_submissions):
                merged_data.update(sub.payload_json)
            return merged_data
        
        return {}
    
    def _fetch_from_csv(
        self, source: Dict, user_context: Dict
    ) -> Dict[str, Any]:
        """Fetch data from uploaded CSV file"""
        import csv
        import io
        
        csv_data = source.get('csv_data')
        lookup_field = source.get('lookup_field', 'email')
        lookup_value = user_context.get(lookup_field)
        
        if not csv_data or not lookup_value:
            return {}
        
        reader = csv.DictReader(io.StringIO(csv_data))
        for row in reader:
            if row.get(lookup_field) == lookup_value:
                return row
        
        return {}
    
    def _get_cache_key(self, source: Dict, user_context: Dict) -> str:
        """Generate cache key for external data"""
        key_data = json.dumps({
            'source': source.get('name'),
            'type': source.get('type'),
            'user': user_context.get('email') or user_context.get('user_id'),
        }, sort_keys=True)
        return f"personalization:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _apply_field_personalization(
        self, schema: Dict, data: Dict
    ) -> Dict[str, Any]:
        """Apply field-level personalization"""
        fields = schema.get('fields', [])
        personalization_rules = schema.get('personalization_rules', [])
        
        for field in fields:
            field_id = field.get('id')
            
            # Check for field-specific rules
            for rule in personalization_rules:
                if rule.get('field_id') == field_id:
                    rule_type = rule.get('type')
                    
                    if rule_type == 'label':
                        # Dynamic label based on data
                        template = rule.get('template', '')
                        field['label'] = self._render_template(template, data)
                    
                    elif rule_type == 'placeholder':
                        template = rule.get('template', '')
                        field['placeholder'] = self._render_template(template, data)
                    
                    elif rule_type == 'default_value':
                        source_field = rule.get('source_field')
                        if source_field and source_field in data:
                            field['default_value'] = data[source_field]
                    
                    elif rule_type == 'validation':
                        # Dynamic validation based on user segment
                        segment = data.get('_segment')
                        if segment and rule.get('segments', {}).get(segment):
                            field['validation'] = rule['segments'][segment]
        
        schema['fields'] = fields
        return schema
    
    def _apply_conditional_visibility(
        self, schema: Dict, data: Dict
    ) -> Dict[str, Any]:
        """Apply conditional field visibility based on external data"""
        fields = schema.get('fields', [])
        visibility_rules = schema.get('visibility_rules', [])
        
        hidden_fields = set()
        
        for rule in visibility_rules:
            condition = rule.get('condition', {})
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            # Get data value
            data_value = data.get(field)
            
            # Evaluate condition
            condition_met = False
            if operator == 'equals':
                condition_met = data_value == value
            elif operator == 'not_equals':
                condition_met = data_value != value
            elif operator == 'contains':
                condition_met = value in str(data_value) if data_value else False
            elif operator == 'in':
                condition_met = data_value in value if isinstance(value, list) else False
            elif operator == 'exists':
                condition_met = data_value is not None
            elif operator == 'not_exists':
                condition_met = data_value is None
            
            # Apply visibility
            if condition_met:
                hidden_fields.update(rule.get('hide', []))
            else:
                hidden_fields.update(rule.get('show_if_not_met', []))
        
        # Filter out hidden fields
        schema['fields'] = [f for f in fields if f.get('id') not in hidden_fields]
        schema['_hidden_fields'] = list(hidden_fields)
        
        return schema
    
    def _apply_prefill(self, schema: Dict, data: Dict) -> Dict[str, Any]:
        """Prefill fields with external data"""
        fields = schema.get('fields', [])
        prefill_mapping = schema.get('prefill_mapping', {})
        
        for field in fields:
            field_id = field.get('id')
            
            # Check prefill mapping
            if field_id in prefill_mapping:
                source_field = prefill_mapping[field_id]
                if source_field in data:
                    field['prefill_value'] = data[source_field]
            
            # Auto-detect common fields
            field_type = field.get('type')
            field_label = field.get('label', '').lower()
            
            if not field.get('prefill_value'):
                # Email field
                if field_type == 'email' or 'email' in field_label:
                    for key in ['email', 'Email', 'e-mail']:
                        if key in data:
                            field['prefill_value'] = data[key]
                            break
                
                # Name field
                elif 'name' in field_label:
                    for key in ['name', 'Name', 'full_name', 'firstname', 'first_name']:
                        if key in data:
                            field['prefill_value'] = data[key]
                            break
                
                # Company field
                elif 'company' in field_label or 'organization' in field_label:
                    for key in ['company', 'Company', 'organization', 'org']:
                        if key in data:
                            field['prefill_value'] = data[key]
                            break
                
                # Phone field
                elif field_type == 'phone' or 'phone' in field_label:
                    for key in ['phone', 'Phone', 'telephone', 'mobile']:
                        if key in data:
                            field['prefill_value'] = data[key]
                            break
        
        schema['fields'] = fields
        return schema
    
    def _apply_dynamic_options(
        self, schema: Dict, data: Dict
    ) -> Dict[str, Any]:
        """Apply dynamic options to select/radio fields"""
        fields = schema.get('fields', [])
        
        for field in fields:
            if field.get('type') not in ['select', 'radio', 'checkbox', 'multiselect']:
                continue
            
            dynamic_options = field.get('dynamic_options')
            if not dynamic_options:
                continue
            
            source_type = dynamic_options.get('source_type')
            
            if source_type == 'data_field':
                # Options from external data field
                source_field = dynamic_options.get('source_field')
                if source_field in data:
                    options = data[source_field]
                    if isinstance(options, list):
                        field['options'] = options
            
            elif source_type == 'filtered':
                # Filter existing options based on data
                all_options = dynamic_options.get('all_options', [])
                filter_field = dynamic_options.get('filter_field')
                filter_value = data.get(filter_field)
                
                if filter_value:
                    filtered = [
                        opt for opt in all_options
                        if opt.get('filter') == filter_value or not opt.get('filter')
                    ]
                    field['options'] = [opt.get('value') or opt for opt in filtered]
            
            elif source_type == 'dependent':
                # Options depend on another field's value
                depends_on = dynamic_options.get('depends_on')
                option_map = dynamic_options.get('option_map', {})
                
                parent_value = data.get(depends_on)
                if parent_value and parent_value in option_map:
                    field['options'] = option_map[parent_value]
        
        schema['fields'] = fields
        return schema
    
    def _identify_user_segments(self, data: Dict) -> List[str]:
        """Identify user segments based on personalization data"""
        segments = []
        
        # Industry segment
        industry = data.get('industry') or data.get('Industry')
        if industry:
            segments.append(f'industry:{industry.lower()}')
        
        # Company size segment
        company_size = data.get('company_size') or data.get('employees')
        if company_size:
            if isinstance(company_size, int):
                if company_size < 10:
                    segments.append('size:small')
                elif company_size < 100:
                    segments.append('size:medium')
                else:
                    segments.append('size:enterprise')
        
        # Location segment
        country = data.get('country') or data.get('Country')
        if country:
            segments.append(f'country:{country.lower()}')
        
        # Lead quality segment (if lead score available)
        lead_score = data.get('_lead_score')
        if lead_score:
            if lead_score >= 80:
                segments.append('lead:hot')
            elif lead_score >= 50:
                segments.append('lead:warm')
            else:
                segments.append('lead:cold')
        
        # Returning user segment
        if data.get('_previous_submissions'):
            segments.append('returning_user')
        else:
            segments.append('new_user')
        
        return segments
    
    def _render_template(self, template: str, data: Dict) -> str:
        """Render template string with data"""
        result = template
        for key, value in data.items():
            result = result.replace(f'{{{key}}}', str(value) if value else '')
            result = result.replace('{{key}}', str(value) if value else '')
        return result
    
    def create_personalization_rule(
        self,
        form,
        rule_type: str,
        field_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a personalization rule to a form"""
        schema = form.schema_json
        
        if 'personalization_rules' not in schema:
            schema['personalization_rules'] = []
        
        rule = {
            'type': rule_type,
            'field_id': field_id,
            **config,
        }
        
        schema['personalization_rules'].append(rule)
        form.schema_json = schema
        form.save()
        
        return rule
    
    def create_visibility_rule(
        self,
        form,
        condition: Dict[str, Any],
        hide_fields: List[str] = None,
        show_fields: List[str] = None,
    ) -> Dict[str, Any]:
        """Add a visibility rule to a form"""
        schema = form.schema_json
        
        if 'visibility_rules' not in schema:
            schema['visibility_rules'] = []
        
        rule = {
            'condition': condition,
            'hide': hide_fields or [],
            'show_if_not_met': show_fields or [],
        }
        
        schema['visibility_rules'].append(rule)
        form.schema_json = schema
        form.save()
        
        return rule
    
    def create_data_source(
        self,
        form,
        name: str,
        source_type: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a data source configuration to a form"""
        schema = form.schema_json
        
        if 'data_sources' not in schema:
            schema['data_sources'] = []
        
        source = {
            'name': name,
            'type': source_type,
            **config,
        }
        
        schema['data_sources'].append(source)
        form.schema_json = schema
        form.save()
        
        return source
    
    def preview_personalization(
        self,
        form,
        test_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Preview personalization with test data"""
        # Get data sources from schema
        schema = form.schema_json
        data_sources = schema.get('data_sources', [])
        
        # Personalize with test data
        personalized = self.personalize_form(form, test_data, data_sources)
        
        # Return comparison
        return {
            'original': {
                'field_count': len(schema.get('fields', [])),
                'fields': [f.get('id') for f in schema.get('fields', [])],
            },
            'personalized': {
                'field_count': len(personalized.get('fields', [])),
                'fields': [f.get('id') for f in personalized.get('fields', [])],
                'hidden_fields': personalized.get('_hidden_fields', []),
                'prefilled_fields': [
                    f.get('id') for f in personalized.get('fields', [])
                    if f.get('prefill_value')
                ],
                'segments': personalized.get('_personalization', {}).get('user_segments', []),
            },
            'test_data_used': test_data,
        }


class PersonalizationAnalytics:
    """Track and analyze personalization effectiveness"""
    
    @staticmethod
    def track_personalized_view(form, session_id: str, personalization_data: Dict):
        """Track when a personalized form is viewed"""
        from forms.models_advanced import FormAnalytics
        
        FormAnalytics.objects.create(
            form=form,
            session_id=session_id,
            event_type='view',
            event_data={
                'personalized': True,
                'segments': personalization_data.get('user_segments', []),
                'prefilled_count': len(personalization_data.get('prefilled_fields', [])),
                'hidden_count': len(personalization_data.get('hidden_fields', [])),
            }
        )
    
    @staticmethod
    def get_personalization_stats(form) -> Dict[str, Any]:
        """Get statistics on personalization effectiveness"""
        from forms.models_advanced import FormAnalytics
        
        # Compare personalized vs non-personalized conversion
        personalized_views = FormAnalytics.objects.filter(
            form=form,
            event_type='view',
            event_data__personalized=True,
        ).count()
        
        non_personalized_views = FormAnalytics.objects.filter(
            form=form,
            event_type='view',
        ).exclude(
            event_data__personalized=True,
        ).count()
        
        # Get submission counts
        # This would require tracking which submissions came from personalized forms
        
        return {
            'personalized_views': personalized_views,
            'non_personalized_views': non_personalized_views,
            'personalization_rate': (
                personalized_views / (personalized_views + non_personalized_views) * 100
                if (personalized_views + non_personalized_views) > 0 else 0
            ),
        }
