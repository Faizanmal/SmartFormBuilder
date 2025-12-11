"""
Form scheduling and lifecycle management service
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import pytz
from django.utils import timezone


class SchedulingService:
    """Handle form scheduling, recurring forms, and lifecycle automation"""
    
    def schedule_form_activation(
        self,
        form_id: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        timezone_str: str = 'UTC',
        max_submissions: Optional[int] = None
    ) -> Dict:
        """Schedule form to go live at specific time"""
        from ..models_scheduling import FormSchedule
        from ..models import Form
        
        try:
            form = Form.objects.get(id=form_id)
            tz = pytz.timezone(timezone_str)
            
            schedule, created = FormSchedule.objects.get_or_create(
                form=form,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                    'timezone': timezone_str,
                    'max_submissions': max_submissions,
                    'status': 'pending'
                }
            )
            
            if not created:
                schedule.start_date = start_date
                schedule.end_date = end_date
                schedule.timezone = timezone_str
                schedule.max_submissions = max_submissions
                schedule.save()
            
            return {
                'success': True,
                'schedule_id': str(schedule.id),
                'status': schedule.status
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_and_activate_scheduled_forms(self) -> Dict:
        """Check for forms that should be activated (run as Celery task)"""
        from ..models_scheduling import FormSchedule
        
        now = timezone.now()
        activated_count = 0
        
        # Find pending schedules that should start
        pending_schedules = FormSchedule.objects.filter(
            status='pending',
            start_date__lte=now
        )
        
        for schedule in pending_schedules:
            # Activate form
            schedule.form.status = 'published'
            schedule.form.is_active = True
            schedule.form.published_at = now
            schedule.form.save()
            
            schedule.status = 'active'
            schedule.activated_at = now
            schedule.save()
            
            # Log lifecycle event
            self._log_lifecycle_event(
                schedule.form,
                'activated',
                automated=True,
                metadata={'scheduled_for': schedule.start_date.isoformat()}
            )
            
            activated_count += 1
        
        return {
            'success': True,
            'activated_count': activated_count
        }
    
    def check_and_expire_forms(self) -> Dict:
        """Check for forms that should expire"""
        from ..models_scheduling import FormSchedule
        
        now = timezone.now()
        expired_count = 0
        
        # Find active schedules that should end
        expiring_schedules = FormSchedule.objects.filter(
            status='active',
            end_date__lte=now
        )
        
        for schedule in expiring_schedules:
            # Deactivate form
            schedule.form.is_active = False
            if schedule.auto_archive:
                schedule.form.status = 'archived'
            schedule.form.save()
            
            schedule.status = 'expired'
            schedule.expired_at = now
            schedule.save()
            
            # Log lifecycle event
            self._log_lifecycle_event(
                schedule.form,
                'expired',
                automated=True,
                metadata={'scheduled_end': schedule.end_date.isoformat()}
            )
            
            expired_count += 1
        
        # Check submission limits
        limit_reached = FormSchedule.objects.filter(
            status='active',
            max_submissions__isnull=False
        )
        
        for schedule in limit_reached:
            if schedule.form.submissions_count >= schedule.max_submissions:
                schedule.form.is_active = False
                schedule.form.save()
                
                schedule.status = 'expired'
                schedule.expired_at = now
                schedule.save()
                
                self._log_lifecycle_event(
                    schedule.form,
                    'submission_limit_reached',
                    automated=True,
                    metadata={'max_submissions': schedule.max_submissions}
                )
                
                expired_count += 1
        
        return {
            'success': True,
            'expired_count': expired_count
        }
    
    def create_recurring_form(
        self,
        template_form_id: str,
        frequency: str,
        interval: int,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        **kwargs
    ) -> Dict:
        """Create recurring form configuration"""
        from ..models_scheduling import RecurringForm
        from ..models import Form
        
        try:
            template_form = Form.objects.get(id=template_form_id)
            
            recurring = RecurringForm.objects.create(
                template_form=template_form,
                user=template_form.user,
                frequency=frequency,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
                next_creation_at=start_date,
                **kwargs
            )
            
            return {
                'success': True,
                'recurring_id': str(recurring.id),
                'next_creation': recurring.next_creation_at.isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_recurring_forms(self) -> Dict:
        """Process recurring forms and create new instances (Celery task)"""
        from ..models_scheduling import RecurringForm
        
        now = timezone.now()
        created_count = 0
        
        recurring_forms = RecurringForm.objects.filter(
            is_active=True,
            next_creation_at__lte=now
        )
        
        for recurring in recurring_forms:
            # Check if we should stop
            if recurring.end_date and now > recurring.end_date:
                recurring.is_active = False
                recurring.save()
                continue
            
            # Clone the template form
            new_form = self._clone_form(recurring.template_form, recurring.naming_pattern, now)
            
            if recurring.auto_publish:
                new_form.status = 'published'
                new_form.published_at = now
            
            new_form.save()
            
            # Update recurring config
            recurring.last_created_at = now
            recurring.next_creation_at = self._calculate_next_creation(recurring, now)
            recurring.forms_created_count += 1
            recurring.save()
            
            created_count += 1
        
        return {
            'success': True,
            'forms_created': created_count
        }
    
    def _clone_form(self, template_form, naming_pattern: str, date: datetime):
        """Clone a form for recurring usage"""
        from ..models import Form
        import copy
        
        # Generate new form name
        form_name = naming_pattern.format(
            title=template_form.title,
            date=date.strftime('%Y-%m-%d'),
            week=date.strftime('%W'),
            month=date.strftime('%B'),
            year=date.strftime('%Y')
        )
        
        # Create new form
        new_form = Form(
            user=template_form.user,
            team=template_form.team,
            title=form_name,
            description=template_form.description,
            schema_json=copy.deepcopy(template_form.schema_json),
            settings_json=copy.deepcopy(template_form.settings_json),
            status='draft'
        )
        
        return new_form
    
    def _calculate_next_creation(self, recurring, current_date: datetime) -> datetime:
        """Calculate next form creation date"""
        if recurring.frequency == 'daily':
            return current_date + timedelta(days=recurring.interval)
        elif recurring.frequency == 'weekly':
            return current_date + timedelta(weeks=recurring.interval)
        elif recurring.frequency == 'monthly':
            # Add months (approximate)
            return current_date + timedelta(days=30 * recurring.interval)
        elif recurring.frequency == 'quarterly':
            return current_date + timedelta(days=90 * recurring.interval)
        elif recurring.frequency == 'yearly':
            return current_date + timedelta(days=365 * recurring.interval)
        
        return current_date + timedelta(days=recurring.interval)
    
    def check_conditional_activation(self) -> Dict:
        """Check and activate forms with conditional triggers"""
        from ..models_scheduling import FormSchedule
        
        activated_count = 0
        
        schedules = FormSchedule.objects.filter(
            status='pending',
            activation_type='conditional'
        )
        
        for schedule in schedules:
            conditions = schedule.conditional_activation
            
            if self._evaluate_conditions(conditions):
                schedule.form.status = 'published'
                schedule.form.is_active = True
                schedule.form.save()
                
                schedule.status = 'active'
                schedule.activated_at = timezone.now()
                schedule.save()
                
                self._log_lifecycle_event(
                    schedule.form,
                    'activated',
                    automated=True,
                    metadata={'trigger': 'conditional', 'conditions': conditions}
                )
                
                activated_count += 1
        
        return {
            'success': True,
            'activated_count': activated_count
        }
    
    def _evaluate_conditions(self, conditions: Dict) -> bool:
        """Evaluate conditional activation rules"""
        from ..models import Form
        
        condition_type = conditions.get('type')
        
        if condition_type == 'form_submissions':
            # Activate when another form reaches X submissions
            target_form_id = conditions.get('form_id')
            target_count = conditions.get('submission_count')
            
            try:
                target_form = Form.objects.get(id=target_form_id)
                return target_form.submissions_count >= target_count
            except Form.DoesNotExist:
                return False
        
        elif condition_type == 'date_after':
            # Activate after specific date
            target_date = datetime.fromisoformat(conditions.get('date'))
            return timezone.now() >= target_date
        
        return False
    
    def _log_lifecycle_event(
        self,
        form,
        event_type: str,
        triggered_by=None,
        automated: bool = False,
        metadata: Dict = None
    ):
        """Log form lifecycle event"""
        from ..models_scheduling import FormLifecycleEvent
        
        FormLifecycleEvent.objects.create(
            form=form,
            event_type=event_type,
            triggered_by=triggered_by,
            automated=automated,
            metadata=metadata or {}
        )
    
    def auto_archive_old_forms(self, days_inactive: int = 90) -> Dict:
        """Auto-archive forms inactive for X days"""
        from ..models import Form
        
        cutoff_date = timezone.now() - timedelta(days=days_inactive)
        
        old_forms = Form.objects.filter(
            status='published',
            updated_at__lt=cutoff_date,
            is_active=True
        )
        
        archived_count = 0
        for form in old_forms:
            form.status = 'archived'
            form.is_active = False
            form.save()
            
            self._log_lifecycle_event(
                form,
                'archived',
                automated=True,
                metadata={'reason': 'auto_archive', 'days_inactive': days_inactive}
            )
            
            archived_count += 1
        
        return {
            'success': True,
            'archived_count': archived_count
        }
