"""
Automated Lead Nurturing Workflow Service
Build automated email/SMS sequences triggered by form submissions
"""
import json
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.core.mail import send_mail
from django.template import Template, Context
from django.conf import settings
from openai import OpenAI


class WorkflowService:
    """
    No-code workflow builder for automated lead nurturing.
    Supports email sequences, SMS, webhooks, and CRM integrations.
    """
    
    TRIGGER_TYPES = [
        'on_submit',
        'on_lead_score',
        'on_status_change',
        'time_delay',
        'condition_met',
    ]
    
    ACTION_TYPES = [
        'send_email',
        'send_sms',
        'webhook',
        'update_lead_status',
        'assign_lead',
        'add_tag',
        'remove_tag',
        'crm_sync',
        'slack_notification',
    ]
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
    
    def create_workflow(
        self, 
        form, 
        name: str, 
        description: str = '',
        trigger: Dict[str, Any] = None,
        actions: List[Dict[str, Any]] = None,
        conditions: List[Dict[str, Any]] = None,
        is_active: bool = True,
    ) -> 'NurturingWorkflow':
        """
        Create a new nurturing workflow
        
        Args:
            form: Form model instance
            name: Workflow name
            description: Workflow description
            trigger: Trigger configuration
            actions: List of action configurations
            conditions: List of condition configurations
            is_active: Whether workflow is active
        """
        from forms.models_advanced import NurturingWorkflow
        
        workflow = NurturingWorkflow.objects.create(
            form=form,
            name=name,
            description=description,
            trigger_config=trigger or {'type': 'on_submit'},
            actions=actions or [],
            conditions=conditions or [],
            is_active=is_active,
        )
        
        return workflow
    
    def execute_workflow(
        self, 
        workflow: 'NurturingWorkflow', 
        submission, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow for a submission
        Returns execution result
        """
        from forms.models_advanced import WorkflowExecution, WorkflowActionLog
        
        # Check if workflow should run
        if not workflow.is_active:
            return {'status': 'skipped', 'reason': 'Workflow is inactive'}
        
        # Check conditions
        if not self._check_conditions(workflow.conditions, submission, context):
            return {'status': 'skipped', 'reason': 'Conditions not met'}
        
        # Create execution record
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            submission=submission,
            status='running',
            context=context or {},
        )
        
        results = []
        
        try:
            # Execute each action
            for i, action in enumerate(workflow.actions):
                action_result = self._execute_action(
                    action, submission, context, execution
                )
                
                # Log action
                WorkflowActionLog.objects.create(
                    execution=execution,
                    action_index=i,
                    action_type=action.get('type'),
                    action_config=action,
                    status='success' if action_result.get('success') else 'failed',
                    result=action_result,
                )
                
                results.append(action_result)
                
                # Stop on failure if configured
                if not action_result.get('success') and action.get('stop_on_failure'):
                    execution.status = 'failed'
                    execution.error_message = action_result.get('error')
                    execution.save()
                    return {
                        'status': 'failed',
                        'execution_id': str(execution.id),
                        'results': results,
                    }
            
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.save()
            
            return {
                'status': 'completed',
                'execution_id': str(execution.id),
                'results': results,
            }
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.save()
            
            return {
                'status': 'failed',
                'execution_id': str(execution.id),
                'error': str(e),
                'results': results,
            }
    
    def _check_conditions(
        self, 
        conditions: List[Dict], 
        submission, 
        context: Dict
    ) -> bool:
        """Check if all conditions are met"""
        if not conditions:
            return True
        
        payload = submission.payload_json
        
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            # Get field value from submission
            field_value = payload.get(field)
            
            # Check condition
            if operator == 'equals':
                if field_value != value:
                    return False
            elif operator == 'not_equals':
                if field_value == value:
                    return False
            elif operator == 'contains':
                if value not in str(field_value):
                    return False
            elif operator == 'greater_than':
                if not (field_value and float(field_value) > float(value)):
                    return False
            elif operator == 'less_than':
                if not (field_value and float(field_value) < float(value)):
                    return False
            elif operator == 'is_empty':
                if field_value:
                    return False
            elif operator == 'is_not_empty':
                if not field_value:
                    return False
            elif operator == 'lead_score_gte':
                if hasattr(submission, 'lead_score'):
                    if submission.lead_score.total_score < int(value):
                        return False
                else:
                    return False
        
        return True
    
    def _execute_action(
        self, 
        action: Dict, 
        submission, 
        context: Dict,
        execution: 'WorkflowExecution'
    ) -> Dict[str, Any]:
        """Execute a single workflow action"""
        action_type = action.get('type')
        config = action.get('config', {})
        
        # Handle delay
        if action.get('delay_minutes'):
            self._schedule_delayed_action(action, submission, execution)
            return {'success': True, 'delayed': True, 'delay_minutes': action['delay_minutes']}
        
        try:
            if action_type == 'send_email':
                return self._action_send_email(config, submission, context)
            elif action_type == 'send_sms':
                return self._action_send_sms(config, submission, context)
            elif action_type == 'webhook':
                return self._action_webhook(config, submission, context)
            elif action_type == 'update_lead_status':
                return self._action_update_lead_status(config, submission)
            elif action_type == 'assign_lead':
                return self._action_assign_lead(config, submission)
            elif action_type == 'add_tag':
                return self._action_add_tag(config, submission)
            elif action_type == 'crm_sync':
                return self._action_crm_sync(config, submission, context)
            elif action_type == 'slack_notification':
                return self._action_slack_notification(config, submission, context)
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_send_email(
        self, config: Dict, submission, context: Dict
    ) -> Dict[str, Any]:
        """Send email action"""
        recipient = config.get('recipient') or self._get_submission_email(submission)
        subject = self._render_template(config.get('subject', ''), submission, context)
        body = self._render_template(config.get('body', ''), submission, context)
        html_body = self._render_template(config.get('html_body', ''), submission, context)
        
        if not recipient:
            return {'success': False, 'error': 'No recipient email found'}
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_body if html_body else None,
                fail_silently=False,
            )
            return {'success': True, 'recipient': recipient}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_send_sms(
        self, config: Dict, submission, context: Dict
    ) -> Dict[str, Any]:
        """Send SMS action (Twilio integration)"""
        from forms.services.sms_service import SMSService
        
        phone = config.get('phone') or self._get_submission_phone(submission)
        message = self._render_template(config.get('message', ''), submission, context)
        
        if not phone:
            return {'success': False, 'error': 'No phone number found'}
        
        try:
            result = SMSService.send_sms(phone, message)
            return {'success': True, 'phone': phone, 'message_sid': result.get('sid')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_webhook(
        self, config: Dict, submission, context: Dict
    ) -> Dict[str, Any]:
        """Send webhook action"""
        import requests
        
        url = config.get('url')
        method = config.get('method', 'POST').upper()
        headers = config.get('headers', {})
        
        # Prepare payload
        payload = {
            'submission_id': str(submission.id),
            'form_id': str(submission.form.id),
            'data': submission.payload_json,
            'timestamp': timezone.now().isoformat(),
        }
        
        # Add custom payload fields
        if config.get('payload'):
            payload.update(config['payload'])
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=headers,
                timeout=30,
            )
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response': response.text[:500],
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_update_lead_status(
        self, config: Dict, submission
    ) -> Dict[str, Any]:
        """Update lead status action"""
        from forms.models_advanced import LeadScore
        
        new_status = config.get('status')
        notes = config.get('notes', '')
        
        try:
            lead_score, created = LeadScore.objects.get_or_create(
                submission=submission,
                defaults={'total_score': 0, 'quality': 'warm'}
            )
            lead_score.follow_up_status = new_status
            if notes:
                lead_score.notes = f"{lead_score.notes}\n{timezone.now().isoformat()}: {notes}"
            lead_score.save()
            
            return {'success': True, 'status': new_status}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_assign_lead(
        self, config: Dict, submission
    ) -> Dict[str, Any]:
        """Assign lead to user action"""
        from forms.models_advanced import LeadScore
        from users.models import User
        
        user_id = config.get('user_id')
        assignment_method = config.get('method', 'specific')  # specific, round_robin, least_loaded
        
        try:
            lead_score, created = LeadScore.objects.get_or_create(
                submission=submission,
                defaults={'total_score': 0, 'quality': 'warm'}
            )
            
            if assignment_method == 'specific' and user_id:
                user = User.objects.get(id=user_id)
            elif assignment_method == 'round_robin':
                user = self._get_round_robin_assignee(submission.form)
            elif assignment_method == 'least_loaded':
                user = self._get_least_loaded_assignee(submission.form)
            else:
                return {'success': False, 'error': 'Invalid assignment method'}
            
            lead_score.assigned_to = user
            lead_score.save()
            
            return {'success': True, 'assigned_to': user.email}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_add_tag(
        self, config: Dict, submission
    ) -> Dict[str, Any]:
        """Add tag to submission"""
        tags = config.get('tags', [])
        
        try:
            existing_tags = submission.payload_json.get('_tags', [])
            new_tags = list(set(existing_tags + tags))
            submission.payload_json['_tags'] = new_tags
            submission.save()
            
            return {'success': True, 'tags': new_tags}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_crm_sync(
        self, config: Dict, submission, context: Dict
    ) -> Dict[str, Any]:
        """Sync to CRM action"""
        crm_type = config.get('crm_type')  # salesforce, hubspot, pipedrive
        
        # Map submission data to CRM fields
        field_mapping = config.get('field_mapping', {})
        crm_data = {}
        
        for form_field, crm_field in field_mapping.items():
            crm_data[crm_field] = submission.payload_json.get(form_field)
        
        try:
            if crm_type == 'salesforce':
                result = self._sync_to_salesforce(crm_data, config)
            elif crm_type == 'hubspot':
                result = self._sync_to_hubspot(crm_data, config)
            elif crm_type == 'pipedrive':
                result = self._sync_to_pipedrive(crm_data, config)
            else:
                return {'success': False, 'error': f'Unknown CRM: {crm_type}'}
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_slack_notification(
        self, config: Dict, submission, context: Dict
    ) -> Dict[str, Any]:
        """Send Slack notification"""
        import requests
        
        webhook_url = config.get('webhook_url')
        channel = config.get('channel')
        message = self._render_template(config.get('message', ''), submission, context)
        
        payload = {
            'text': message,
            'channel': channel,
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            return {'success': response.status_code == 200}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _render_template(
        self, template_str: str, submission, context: Dict = None
    ) -> str:
        """Render template with submission data"""
        if not template_str:
            return ''
        
        # Build context
        template_context = {
            'submission_id': str(submission.id),
            'form_title': submission.form.title,
            'submitted_at': submission.created_at.isoformat(),
            **(context or {}),
        }
        
        # Add submission fields
        for key, value in submission.payload_json.items():
            template_context[key] = value
        
        # Add lead score if available
        if hasattr(submission, 'lead_score'):
            template_context['lead_score'] = submission.lead_score.total_score
            template_context['lead_quality'] = submission.lead_score.quality
        
        # Render with Django template
        try:
            template = Template(template_str)
            return template.render(Context(template_context))
        except:
            # Fallback to simple string replacement
            result = template_str
            for key, value in template_context.items():
                result = result.replace('{{' + key + '}}', str(value))
            return result
    
    def _get_submission_email(self, submission) -> Optional[str]:
        """Extract email from submission"""
        payload = submission.payload_json
        for key in ['email', 'Email', 'EMAIL', 'e-mail', 'E-mail']:
            if key in payload:
                return payload[key]
        return None
    
    def _get_submission_phone(self, submission) -> Optional[str]:
        """Extract phone from submission"""
        payload = submission.payload_json
        for key in ['phone', 'Phone', 'PHONE', 'telephone', 'mobile']:
            if key in payload:
                return payload[key]
        return None
    
    def _get_round_robin_assignee(self, form):
        """Get next assignee using round-robin"""
        from users.models import User
        from forms.models_advanced import LeadScore
        
        # Get team members
        team_members = User.objects.filter(
            team_memberships__team=form.owner.teams.first()
        ).order_by('id')
        
        if not team_members:
            return form.owner
        
        # Get last assignment
        last_assignment = LeadScore.objects.filter(
            submission__form=form,
            assigned_to__isnull=False
        ).order_by('-created_at').first()
        
        if last_assignment:
            last_idx = list(team_members).index(last_assignment.assigned_to)
            next_idx = (last_idx + 1) % len(team_members)
            return team_members[next_idx]
        
        return team_members.first()
    
    def _get_least_loaded_assignee(self, form):
        """Get assignee with least open leads"""
        from users.models import User
        from django.db.models import Count
        
        team_members = User.objects.filter(
            team_memberships__team=form.owner.teams.first()
        ).annotate(
            open_leads=Count(
                'assigned_leads',
                filter=Q(assigned_leads__follow_up_status__in=['pending', 'contacted'])
            )
        ).order_by('open_leads')
        
        return team_members.first() if team_members else form.owner
    
    def _sync_to_salesforce(self, data: Dict, config: Dict) -> Dict:
        """Sync data to Salesforce"""
        import requests
        
        access_token = config.get('access_token')
        instance_url = config.get('instance_url')
        object_type = config.get('object_type', 'Lead')
        
        url = f"{instance_url}/services/data/v57.0/sobjects/{object_type}/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            return {'success': True, 'id': response.json().get('id')}
        else:
            return {'success': False, 'error': response.text}
    
    def _sync_to_hubspot(self, data: Dict, config: Dict) -> Dict:
        """Sync data to HubSpot"""
        import requests
        
        api_key = config.get('api_key')
        url = 'https://api.hubapi.com/crm/v3/objects/contacts'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'properties': data
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return {'success': True, 'id': response.json().get('id')}
        else:
            return {'success': False, 'error': response.text}
    
    def _sync_to_pipedrive(self, data: Dict, config: Dict) -> Dict:
        """Sync data to Pipedrive"""
        import requests
        
        api_key = config.get('api_key')
        url = f'https://api.pipedrive.com/v1/persons?api_token={api_key}'
        
        response = requests.post(url, json=data)
        
        if response.status_code == 201:
            return {'success': True, 'id': response.json().get('data', {}).get('id')}
        else:
            return {'success': False, 'error': response.text}
    
    def _schedule_delayed_action(
        self, action: Dict, submission, execution
    ) -> None:
        """Schedule a delayed action using Celery"""
        from forms.tasks import execute_delayed_workflow_action
        
        delay_minutes = action.get('delay_minutes', 0)
        
        execute_delayed_workflow_action.apply_async(
            args=[str(execution.id), action],
            countdown=delay_minutes * 60,
        )
    
    def generate_workflow_from_template(
        self, template_name: str, form, customizations: Dict = None
    ) -> 'NurturingWorkflow':
        """Create workflow from predefined template"""
        templates = {
            'welcome_sequence': {
                'name': 'Welcome Email Sequence',
                'description': 'Send welcome emails to new submissions',
                'trigger_config': {'type': 'on_submit'},
                'actions': [
                    {
                        'type': 'send_email',
                        'config': {
                            'subject': 'Welcome to {{form_title}}!',
                            'body': 'Hi {{name}},\n\nThank you for your submission!',
                        },
                    },
                    {
                        'type': 'send_email',
                        'delay_minutes': 1440,  # 24 hours
                        'config': {
                            'subject': 'Here are your next steps',
                            'body': 'Hi {{name}},\n\nWe wanted to follow up...',
                        },
                    },
                ],
            },
            'high_value_lead': {
                'name': 'High-Value Lead Handler',
                'description': 'Alert team and assign leads with high scores',
                'trigger_config': {'type': 'on_submit'},
                'conditions': [
                    {'field': '_lead_score', 'operator': 'lead_score_gte', 'value': 80}
                ],
                'actions': [
                    {
                        'type': 'slack_notification',
                        'config': {
                            'message': '🔥 High-value lead from {{form_title}}!\nName: {{name}}\nEmail: {{email}}',
                        },
                    },
                    {
                        'type': 'assign_lead',
                        'config': {
                            'method': 'round_robin',
                        },
                    },
                    {
                        'type': 'update_lead_status',
                        'config': {
                            'status': 'contacted',
                            'notes': 'Auto-assigned as high-value lead',
                        },
                    },
                ],
            },
            'abandoned_cart_recovery': {
                'name': 'Abandoned Form Recovery',
                'description': 'Re-engage users who started but did not complete the form',
                'trigger_config': {'type': 'on_abandon'},
                'actions': [
                    {
                        'type': 'send_email',
                        'delay_minutes': 60,
                        'config': {
                            'subject': "Don't forget to complete your submission",
                            'body': 'Hi,\n\nYou started filling out {{form_title}} but didn\'t finish...',
                        },
                    },
                    {
                        'type': 'send_email',
                        'delay_minutes': 1440,
                        'config': {
                            'subject': 'Last chance to complete your submission',
                            'body': 'Hi,\n\nWe noticed you haven\'t finished...',
                        },
                    },
                ],
            },
        }
        
        if template_name not in templates:
            raise ValueError(f'Unknown template: {template_name}')
        
        template = templates[template_name]
        
        # Apply customizations
        if customizations:
            if 'actions' in customizations:
                for i, action_update in enumerate(customizations['actions']):
                    if i < len(template['actions']):
                        template['actions'][i]['config'].update(action_update)
        
        return self.create_workflow(
            form=form,
            name=template['name'],
            description=template['description'],
            trigger=template['trigger_config'],
            actions=template['actions'],
            conditions=template.get('conditions', []),
        )
    
    def generate_ai_workflow(
        self, form, description: str
    ) -> Dict[str, Any]:
        """Generate workflow using AI based on description"""
        schema = form.schema_json
        
        prompt = f"""Create an automated workflow for a form with these fields:
{json.dumps(schema.get('fields', []), indent=2)}

User request: {description}

Return a JSON workflow with this structure:
{{
    "name": "Workflow name",
    "description": "Description",
    "trigger_config": {{"type": "on_submit|on_lead_score|time_delay"}},
    "conditions": [{{"field": "field_id", "operator": "equals|contains|greater_than", "value": "value"}}],
    "actions": [
        {{
            "type": "send_email|send_sms|webhook|update_lead_status|assign_lead|slack_notification",
            "delay_minutes": 0,
            "config": {{
                // Action-specific config
            }}
        }}
    ]
}}

Action types available:
- send_email: subject, body, recipient (optional)
- send_sms: message, phone (optional)
- webhook: url, method, headers, payload
- update_lead_status: status (pending|contacted|negotiating|won|lost)
- assign_lead: method (specific|round_robin|least_loaded), user_id
- slack_notification: message, webhook_url, channel

Use {{field_id}} placeholders for dynamic values.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a workflow automation expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            
            result = response.choices[0].message.content
            workflow_config = json.loads(result)
            
            return workflow_config
        except Exception as e:
            return {'error': str(e)}
