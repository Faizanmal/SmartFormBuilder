"""
Multi-step form service with save & resume functionality
"""
from django.utils import timezone
from datetime import timedelta
import secrets


class MultiStepFormService:
    """Service for handling multi-step forms"""
    
    @staticmethod
    def generate_resume_token():
        """Generate a secure resume token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def save_partial_submission(form, email, payload, current_step, ip_address=None, user_agent=''):
        """Save or update a partial submission"""
        from forms.models_advanced import PartialSubmission
        
        # Check if partial submission already exists for this email
        resume_token = MultiStepFormService.generate_resume_token()
        expires_at = timezone.now() + timedelta(days=30)  # 30-day expiry
        
        partial, created = PartialSubmission.objects.update_or_create(
            form=form,
            email=email,
            defaults={
                'payload_json': payload,
                'current_step': current_step,
                'resume_token': resume_token if created else None,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'expires_at': expires_at,
            }
        )
        
        if not created:
            # Keep the existing resume token
            resume_token = partial.resume_token
        
        return partial, resume_token
    
    @staticmethod
    def get_partial_submission(resume_token):
        """Retrieve partial submission by resume token"""
        from forms.models_advanced import PartialSubmission
        
        try:
            partial = PartialSubmission.objects.get(
                resume_token=resume_token,
                expires_at__gt=timezone.now(),
                completed_at__isnull=True
            )
            return partial
        except PartialSubmission.DoesNotExist:
            return None
    
    @staticmethod
    def mark_abandoned(form, hours_since_update=24):
        """Mark submissions as abandoned if not updated recently"""
        from forms.models_advanced import PartialSubmission
        
        cutoff_time = timezone.now() - timedelta(hours=hours_since_update)
        
        abandoned = PartialSubmission.objects.filter(
            form=form,
            updated_at__lt=cutoff_time,
            is_abandoned=False,
            completed_at__isnull=True
        )
        
        count = abandoned.update(
            is_abandoned=True,
            abandoned_at=timezone.now()
        )
        
        return count
    
    @staticmethod
    def complete_partial_submission(partial_submission, final_payload):
        """Mark a partial submission as complete and create final submission"""
        from forms.models import Submission
        
        # Create final submission
        submission = Submission.objects.create(
            form=partial_submission.form,
            payload_json=final_payload,
            ip_address=partial_submission.ip_address,
            user_agent=partial_submission.user_agent
        )
        
        # Mark partial as complete
        partial_submission.completed_at = timezone.now()
        partial_submission.save()
        
        return submission
    
    @staticmethod
    def validate_step_transition(form_schema, current_step, payload):
        """Validate if user can move to next step based on conditional logic"""
        steps = form_schema.get('steps', [])
        
        if current_step >= len(steps):
            return True, None
        
        current_step_config = steps[current_step - 1]
        conditional_logic = current_step_config.get('conditional_logic', {})
        
        if not conditional_logic:
            return True, None
        
        # Check conditions
        condition_type = conditional_logic.get('type', 'all')  # 'all' or 'any'
        rules = conditional_logic.get('rules', [])
        
        results = []
        for rule in rules:
            field_id = rule.get('field_id')
            operator = rule.get('operator')
            value = rule.get('value')
            
            field_value = payload.get(field_id)
            
            if operator == 'equals':
                results.append(field_value == value)
            elif operator == 'not_equals':
                results.append(field_value != value)
            elif operator == 'contains':
                results.append(value in str(field_value))
            elif operator == 'greater_than':
                try:
                    results.append(float(field_value) > float(value))
                except (ValueError, TypeError):
                    results.append(False)
            elif operator == 'less_than':
                try:
                    results.append(float(field_value) < float(value))
                except (ValueError, TypeError):
                    results.append(False)
        
        if condition_type == 'all':
            is_valid = all(results)
        else:  # 'any'
            is_valid = any(results)
        
        if not is_valid:
            return False, "Conditions not met to proceed to next step"
        
        return True, None
    
    @staticmethod
    def calculate_progress(total_steps, current_step):
        """Calculate form completion progress"""
        if total_steps == 0:
            return 0
        return min(100, int((current_step / total_steps) * 100))
