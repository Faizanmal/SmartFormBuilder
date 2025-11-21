"""
Form abandonment recovery service
"""
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count


class AbandonmentRecoveryService:
    """Service for recovering abandoned forms"""
    
    @staticmethod
    def identify_abandoned_forms(hours_threshold=24):
        """Identify forms abandoned within threshold"""
        from forms.models_advanced import PartialSubmission
        
        cutoff_time = timezone.now() - timedelta(hours=hours_threshold)
        
        abandoned = PartialSubmission.objects.filter(
            updated_at__lt=cutoff_time,
            updated_at__gte=cutoff_time - timedelta(hours=1),  # Within 1 hour window
            is_abandoned=False,
            recovery_email_sent=False,
            completed_at__isnull=True,
            expires_at__gt=timezone.now()
        )
        
        # Mark as abandoned
        abandoned.update(is_abandoned=True, abandoned_at=timezone.now())
        
        return abandoned
    
    @staticmethod
    def send_recovery_email(partial_submission):
        """Send recovery email to user"""
        form = partial_submission.form
        email = partial_submission.email
        resume_token = partial_submission.resume_token
        
        # Build resume URL
        resume_url = f"{settings.FRONTEND_URL}/form/{form.slug}/resume?token={resume_token}"
        
        # Get white-label config if available
        white_label = None
        if hasattr(form.user, 'white_label_config'):
            white_label = form.user.white_label_config
        
        # Email content
        from_email = white_label.email_from_address if white_label else settings.DEFAULT_FROM_EMAIL
        from_name = white_label.email_from_name if white_label else "FormForge"
        
        subject = f"Complete your {form.title} submission"
        
        # Calculate progress
        schema = form.schema_json
        total_steps = len(schema.get('steps', [schema]))
        current_step = partial_submission.current_step
        progress = min(100, int((current_step / total_steps) * 100))
        
        context = {
            'form_title': form.title,
            'form_description': form.description,
            'resume_url': resume_url,
            'current_step': current_step,
            'total_steps': total_steps,
            'progress': progress,
            'expiry_hours': 72,  # Default 3 days
        }
        
        # Render email template
        html_message = render_to_string('emails/form_recovery.html', context)
        text_message = render_to_string('emails/form_recovery.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=text_message,
                from_email=f"{from_name} <{from_email}>",
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Mark recovery email as sent
            partial_submission.recovery_email_sent = True
            partial_submission.save()
            
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send recovery email: {e}")
            return False
    
    @staticmethod
    def batch_send_recovery_emails(max_emails=100):
        """Batch process recovery emails"""
        abandoned = AbandonmentRecoveryService.identify_abandoned_forms(hours_threshold=24)
        
        sent_count = 0
        failed_count = 0
        
        for partial in abandoned[:max_emails]:
            success = AbandonmentRecoveryService.send_recovery_email(partial)
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        return {
            'total_abandoned': abandoned.count(),
            'sent': sent_count,
            'failed': failed_count,
        }
    
    @staticmethod
    def get_abandonment_stats(form, date_from=None, date_to=None):
        """Get abandonment statistics for a form"""
        from forms.models_advanced import PartialSubmission
        
        partials = PartialSubmission.objects.filter(form=form)
        
        if date_from:
            partials = partials.filter(created_at__gte=date_from)
        if date_to:
            partials = partials.filter(created_at__lte=date_to)
        
        total_started = partials.count()
        abandoned = partials.filter(is_abandoned=True).count()
        recovered = partials.filter(
            is_abandoned=True,
            recovery_email_sent=True,
            completed_at__isnull=False
        ).count()
        
        abandonment_rate = (abandoned / total_started * 100) if total_started > 0 else 0
        recovery_rate = (recovered / abandoned * 100) if abandoned > 0 else 0
        
        # Abandonment by step
        step_abandonment = partials.filter(is_abandoned=True).values('current_step').annotate(
            count=Count('id')
        ).order_by('current_step')
        
        return {
            'total_started': total_started,
            'abandoned': abandoned,
            'recovered': recovered,
            'abandonment_rate': round(abandonment_rate, 2),
            'recovery_rate': round(recovery_rate, 2),
            'step_abandonment': list(step_abandonment),
        }
