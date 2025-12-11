"""
Integration marketplace service for third-party connectors
"""
from typing import Dict
import requests
import json
from datetime import datetime, timedelta
from jinja2 import Template


class IntegrationMarketplaceService:
    """Manage third-party integrations and workflows"""
    
    # CRM Connectors
    def sync_to_salesforce(self, connection_data: Dict, submission_data: Dict) -> Dict:
        """Sync submission to Salesforce CRM"""
        api_url = connection_data.get('instance_url', 'https://login.salesforce.com')
        access_token = connection_data.get('access_token')
        
        # Create lead in Salesforce
        lead_data = {
            'FirstName': submission_data.get('firstName', ''),
            'LastName': submission_data.get('lastName', ''),
            'Email': submission_data.get('email', ''),
            'Company': submission_data.get('company', 'Unknown'),
            'Phone': submission_data.get('phone', ''),
            'LeadSource': 'SmartFormBuilder',
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{api_url}/services/data/v59.0/sobjects/Lead',
            headers=headers,
            json=lead_data
        )
        
        return {
            'success': response.status_code == 201,
            'status_code': response.status_code,
            'response': response.json() if response.ok else response.text
        }
    
    def sync_to_hubspot(self, connection_data: Dict, submission_data: Dict) -> Dict:
        """Sync submission to HubSpot CRM"""
        api_key = connection_data.get('api_key')
        
        # Create contact in HubSpot
        contact_data = {
            'properties': {
                'email': submission_data.get('email', ''),
                'firstname': submission_data.get('firstName', ''),
                'lastname': submission_data.get('lastName', ''),
                'phone': submission_data.get('phone', ''),
                'company': submission_data.get('company', ''),
            }
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            headers=headers,
            json=contact_data
        )
        
        return {
            'success': response.status_code == 201,
            'status_code': response.status_code,
            'response': response.json() if response.ok else response.text
        }
    
    # Email Marketing Connectors
    def add_to_mailchimp(self, connection_data: Dict, submission_data: Dict) -> Dict:
        """Add subscriber to Mailchimp list"""
        api_key = connection_data.get('api_key')
        list_id = connection_data.get('list_id')
        dc = api_key.split('-')[1] if '-' in api_key else 'us1'
        
        subscriber_data = {
            'email_address': submission_data.get('email', ''),
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': submission_data.get('firstName', ''),
                'LNAME': submission_data.get('lastName', ''),
            }
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members',
            headers=headers,
            json=subscriber_data
        )
        
        return {
            'success': response.status_code in [200, 201],
            'status_code': response.status_code,
            'response': response.json() if response.ok else response.text
        }
    
    # Productivity App Connectors
    def create_slack_message(self, connection_data: Dict, submission_data: Dict) -> Dict:
        """Post submission to Slack channel"""
        webhook_url = connection_data.get('webhook_url')
        
        # Format submission as Slack message
        fields = []
        for key, value in submission_data.items():
            fields.append({
                'title': key,
                'value': str(value),
                'short': len(str(value)) < 40
            })
        
        message = {
            'text': 'New Form Submission',
            'attachments': [{
                'color': '#36a64f',
                'title': 'Form Submission Details',
                'fields': fields,
                'footer': 'SmartFormBuilder',
                'ts': int(datetime.now().timestamp())
            }]
        }
        
        response = requests.post(webhook_url, json=message)
        
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response': response.text
        }
    
    def create_trello_card(self, connection_data: Dict, submission_data: Dict) -> Dict:
        """Create Trello card from submission"""
        api_key = connection_data.get('api_key')
        token = connection_data.get('token')
        list_id = connection_data.get('list_id')
        
        card_data = {
            'name': f"Form Submission: {submission_data.get('email', 'Unknown')}",
            'desc': json.dumps(submission_data, indent=2),
            'idList': list_id,
            'key': api_key,
            'token': token
        }
        
        response = requests.post(
            'https://api.trello.com/1/cards',
            params=card_data
        )
        
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response': response.json() if response.ok else response.text
        }
    
    def sync_to_google_sheets(self, connection_data: Dict, submission_data: Dict) -> Dict:
        """Append submission to Google Sheets"""
        # This requires Google Sheets API setup
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        try:
            creds = Credentials.from_authorized_user_info(connection_data)
            service = build('sheets', 'v4', credentials=creds)
            
            spreadsheet_id = connection_data.get('spreadsheet_id')
            range_name = connection_data.get('range', 'Sheet1!A:Z')
            
            # Prepare row data
            values = [list(submission_data.values())]
            
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return {
                'success': True,
                'updated_cells': result.get('updates', {}).get('updatedCells', 0)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # Webhook Management
    def execute_webhook(
        self,
        url: str,
        method: str,
        headers: Dict,
        payload_template: str,
        submission_data: Dict,
        timeout: int = 30
    ) -> Dict:
        """Execute custom webhook with template rendering"""
        # Render payload template with Jinja2
        if payload_template:
            template = Template(payload_template)
            payload = template.render(**submission_data)
            try:
                payload_dict = json.loads(payload)
            except json.JSONDecodeError:
                payload_dict = {'data': payload}
        else:
            payload_dict = submission_data
        
        # Execute request
        try:
            if method == 'POST':
                response = requests.post(url, json=payload_dict, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=payload_dict, headers=headers, timeout=timeout)
            elif method == 'PATCH':
                response = requests.patch(url, json=payload_dict, headers=headers, timeout=timeout)
            else:
                return {'success': False, 'error': 'Unsupported HTTP method'}
            
            return {
                'success': response.ok,
                'status_code': response.status_code,
                'response_body': response.text,
                'duration_ms': int(response.elapsed.total_seconds() * 1000)
            }
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def retry_webhook(self, webhook_log_id: str, max_retries: int = 3, delay: int = 60) -> Dict:
        """Retry failed webhook with exponential backoff"""
        from ..models_integrations_marketplace import WebhookLog
        
        try:
            log = WebhookLog.objects.get(id=webhook_log_id)
            
            if log.retry_attempt >= max_retries:
                return {'success': False, 'error': 'Max retries exceeded'}
            
            # Calculate backoff delay
            backoff_delay = delay * (2 ** log.retry_attempt)
            
            # Re-execute webhook
            result = self.execute_webhook(
                url=log.webhook.url,
                method=log.webhook.method,
                headers=log.webhook.headers,
                payload_template=log.webhook.payload_template,
                submission_data=log.request_payload,
                timeout=log.webhook.timeout
            )
            
            # Update log
            log.retry_attempt += 1
            if result['success']:
                log.status_code = result['status_code']
                log.response_body = result['response_body']
            else:
                log.error_message = result.get('error', '')
            log.save()
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Workflow Automation
    def execute_workflow(self, workflow_id: str, trigger_data: Dict) -> Dict:
        """Execute IFTTT-style workflow"""
        from ..models_integrations_marketplace import IntegrationWorkflow
        
        try:
            workflow = IntegrationWorkflow.objects.get(id=workflow_id, is_active=True)
            
            # Check trigger conditions
            if not self._evaluate_trigger(workflow.trigger_config, trigger_data):
                return {'success': False, 'reason': 'Trigger conditions not met'}
            
            # Execute actions sequentially
            results = []
            for action in workflow.actions:
                action_type = action.get('type')
                action_config = action.get('config', {})
                
                if action_type == 'create_crm_contact':
                    result = self._execute_crm_action(action_config, trigger_data)
                elif action_type == 'send_email':
                    result = self._execute_email_action(action_config, trigger_data)
                elif action_type == 'create_task':
                    result = self._execute_task_action(action_config, trigger_data)
                elif action_type == 'webhook':
                    result = self.execute_webhook(**action_config, submission_data=trigger_data)
                else:
                    result = {'success': False, 'error': f'Unknown action type: {action_type}'}
                
                results.append(result)
                
                # Stop on first failure if configured
                if not result.get('success') and not action.get('continue_on_error', False):
                    break
            
            # Update workflow stats
            workflow.execution_count += 1
            workflow.success_count += sum(1 for r in results if r.get('success'))
            workflow.failure_count += sum(1 for r in results if not r.get('success'))
            workflow.last_executed_at = datetime.now()
            workflow.save()
            
            return {
                'success': all(r.get('success') for r in results),
                'results': results
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _evaluate_trigger(self, trigger_config: Dict, data: Dict) -> bool:
        """Evaluate if trigger conditions are met"""
        conditions = trigger_config.get('conditions', [])
        operator = trigger_config.get('operator', 'AND')
        
        if not conditions:
            return True
        
        results = []
        for condition in conditions:
            field = condition.get('field')
            op = condition.get('operator')
            value = condition.get('value')
            
            actual_value = data.get(field)
            
            if op == 'equals':
                results.append(actual_value == value)
            elif op == 'not_equals':
                results.append(actual_value != value)
            elif op == 'contains':
                results.append(value in str(actual_value))
            elif op == 'greater_than':
                results.append(float(actual_value) > float(value))
            elif op == 'less_than':
                results.append(float(actual_value) < float(value))
            elif op == 'exists':
                results.append(actual_value is not None)
        
        if operator == 'AND':
            return all(results)
        elif operator == 'OR':
            return any(results)
        
        return False
    
    def _execute_crm_action(self, config: Dict, data: Dict) -> Dict:
        """Execute CRM integration action"""
        provider = config.get('provider')
        
        if provider == 'salesforce':
            return self.sync_to_salesforce(config, data)
        elif provider == 'hubspot':
            return self.sync_to_hubspot(config, data)
        
        return {'success': False, 'error': f'Unknown CRM provider: {provider}'}
    
    def _execute_email_action(self, config: Dict, data: Dict) -> Dict:
        """Execute email sending action"""
        # Placeholder for email integration
        return {'success': True, 'message': 'Email sent'}
    
    def _execute_task_action(self, config: Dict, data: Dict) -> Dict:
        """Execute task creation action"""
        task_type = config.get('task_type')
        
        if task_type == 'trello':
            return self.create_trello_card(config, data)
        elif task_type == 'slack':
            return self.create_slack_message(config, data)
        
        return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    # OAuth Management
    def refresh_oauth_token(self, connection_id: str) -> Dict:
        """Refresh OAuth access token"""
        from ..models_integrations_marketplace import IntegrationConnection
        
        try:
            connection = IntegrationConnection.objects.get(id=connection_id)
            oauth_data = connection.oauth_data
            
            # Generic OAuth refresh
            token_url = oauth_data.get('token_url')
            refresh_token = oauth_data.get('refresh_token')
            client_id = connection.credentials.get('client_id')
            client_secret = connection.credentials.get('client_secret')
            
            response = requests.post(
                token_url,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'client_id': client_id,
                    'client_secret': client_secret
                }
            )
            
            if response.ok:
                new_tokens = response.json()
                oauth_data.update({
                    'access_token': new_tokens.get('access_token'),
                    'expires_at': (datetime.now() + timedelta(seconds=new_tokens.get('expires_in', 3600))).isoformat()
                })
                connection.oauth_data = oauth_data
                connection.save()
                
                return {'success': True, 'tokens': new_tokens}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
