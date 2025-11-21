"""
Automated follow-up service
"""
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template import Template, Context


class FollowUpService:
    """Service for automated follow-up sequences"""
    
    @staticmethod
    def create_follow_up_sequence(form, submission, sequences):
        """
        Create follow-up emails for a submission
        
        sequences: List of dicts with 'hours', 'subject', 'content'
        Example:
        [
            {'hours': 1, 'subject': 'Thank you!', 'content': 'Thanks for your submission...'},
            {'hours': 24, 'subject': 'Next steps', 'content': 'Here are your next steps...'},
        ]
        """
        from forms.models_advanced import AutomatedFollowUp
        
        follow_ups = []
        for idx, seq in enumerate(sequences, start=1):
            scheduled_for = submission.created_at + timedelta(hours=seq['hours'])
            
            follow_up = AutomatedFollowUp.objects.create(
                form=form,
                submission=submission,
                sequence_step=idx,
                send_after_hours=seq['hours'],
                subject=seq['subject'],
                content=seq['content'],
                scheduled_for=scheduled_for,
                status='scheduled'
            )
            follow_ups.append(follow_up)
        
        return follow_ups
    
    @staticmethod
    def process_pending_follow_ups(batch_size=100):
        """Process scheduled follow-ups that are due"""
        from forms.models_advanced import AutomatedFollowUp
        
        now = timezone.now()
        
        # Get follow-ups that are due
        pending = AutomatedFollowUp.objects.filter(
            status='scheduled',
            scheduled_for__lte=now
        )[:batch_size]
        
        sent_count = 0
        failed_count = 0
        
        for follow_up in pending:
            success = FollowUpService.send_follow_up(follow_up)
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        return {
            'sent': sent_count,
            'failed': failed_count,
        }
    
    @staticmethod
    def send_follow_up(follow_up):
        """Send a single follow-up email"""
        from django.conf import settings
        
        submission = follow_up.submission
        form = follow_up.form
        
        # Get recipient email from submission
        recipient_email = submission.payload_json.get('email')
        if not recipient_email:
            follow_up.status = 'failed'
            follow_up.error_message = 'No email address in submission'
            follow_up.save()
            return False
        
        # Render content with submission data
        try:
            subject_template = Template(follow_up.subject)
            content_template = Template(follow_up.content)
            
            context = Context({
                'form': form,
                'submission': submission.payload_json,
                'form_title': form.title,
                **submission.payload_json
            })
            
            subject = subject_template.render(context)
            content = content_template.render(context)
            
            # Send email
            send_mail(
                subject=subject,
                message=content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            
            # Mark as sent
            follow_up.status = 'sent'
            follow_up.sent_at = timezone.now()
            follow_up.save()
            
            return True
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send follow-up: {e}")
            
            follow_up.status = 'failed'
            follow_up.error_message = str(e)
            follow_up.save()
            
            return False
    
    @staticmethod
    def cancel_follow_ups(submission):
        """Cancel all pending follow-ups for a submission"""
        from forms.models_advanced import AutomatedFollowUp
        
        AutomatedFollowUp.objects.filter(
            submission=submission,
            status='scheduled'
        ).update(status='cancelled')
    
    @staticmethod
    def get_default_sequences(form_type='general'):
        """Get default follow-up sequences by form type"""
        sequences = {
            'general': [
                {
                    'hours': 1,
                    'subject': 'Thank you for your submission!',
                    'content': 'Hi {{name}},\n\nThank you for submitting {{form_title}}. We received your information and will get back to you soon.\n\nBest regards'
                },
                {
                    'hours': 24,
                    'subject': 'Your {{form_title}} - Next Steps',
                    'content': 'Hi {{name}},\n\nWe\'re processing your {{form_title}} submission. Here are the next steps...\n\nBest regards'
                },
            ],
            'consultation': [
                {
                    'hours': 1,
                    'subject': 'Consultation Request Received',
                    'content': 'Hi {{name}},\n\nThank you for requesting a consultation. We\'ll review your information and contact you within 24 hours.\n\nBest regards'
                },
                {
                    'hours': 24,
                    'subject': 'Schedule Your Consultation',
                    'content': 'Hi {{name}},\n\nWe\'re ready to schedule your consultation! Please reply with your availability.\n\nBest regards'
                },
                {
                    'hours': 72,
                    'subject': 'Don\'t Miss Your Consultation',
                    'content': 'Hi {{name}},\n\nWe haven\'t heard back from you. Are you still interested in scheduling a consultation?\n\nBest regards'
                },
            ],
            'quote': [
                {
                    'hours': 2,
                    'subject': 'Your Quote is Ready!',
                    'content': 'Hi {{name}},\n\nYour quote for {{form_title}} is ready. Total estimate: {{budget}}\n\nBest regards'
                },
                {
                    'hours': 48,
                    'subject': 'Questions About Your Quote?',
                    'content': 'Hi {{name}},\n\nDo you have any questions about the quote we sent? We\'re here to help!\n\nBest regards'
                },
            ],
        }
        
        return sequences.get(form_type, sequences['general'])
