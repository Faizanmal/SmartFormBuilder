"""
SMS notification service using Twilio
"""
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS notifications"""
    
    def __init__(self):
        self.client = None
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and hasattr(settings, 'TWILIO_AUTH_TOKEN'):
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def send_sms(self, to_number, message, media_url=None):
        """
        Send an SMS message
        
        Args:
            to_number: Recipient phone number (E.164 format: +1234567890)
            message: Message text (max 1600 chars)
            media_url: Optional URL for MMS media
            
        Returns:
            Message SID if successful, None otherwise
        """
        if not self.client:
            logger.error("Twilio client not configured")
            return None
        
        try:
            # Ensure phone number is in E.164 format
            if not to_number.startswith('+'):
                to_number = f'+1{to_number}'  # Assume US number
            
            message_params = {
                'body': message,
                'from_': self.from_number,
                'to': to_number
            }
            
            if media_url:
                message_params['media_url'] = [media_url]
            
            message_obj = self.client.messages.create(**message_params)
            
            logger.info(f"SMS sent successfully: {message_obj.sid}")
            return message_obj.sid
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return None
    
    def send_form_notification(self, to_number, form_title, submission_id):
        """Send notification about new form submission"""
        message = f"New submission received for '{form_title}'. Submission ID: {submission_id}"
        return self.send_sms(to_number, message)
    
    def send_form_reminder(self, to_number, form_title, form_url):
        """Send reminder to complete a form"""
        message = f"Reminder: Please complete '{form_title}'\n{form_url}"
        return self.send_sms(to_number, message)
    
    def send_verification_code(self, to_number, code):
        """Send verification code for phone verification"""
        message = f"Your verification code is: {code}\nDo not share this code with anyone."
        return self.send_sms(to_number, message)
    
    def send_form_response(self, to_number, form_title, response_message):
        """Send automated response after form submission"""
        message = f"Thank you for submitting '{form_title}'.\n\n{response_message}"
        return self.send_sms(to_number, message)
    
    def send_bulk_sms(self, recipients, message):
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of phone numbers
            message: Message text
            
        Returns:
            Dict with success/failure counts
        """
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        for phone_number in recipients:
            message_sid = self.send_sms(phone_number, message)
            if message_sid:
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(phone_number)
        
        return results
    
    def validate_phone_number(self, phone_number):
        """
        Validate phone number using Twilio Lookup API
        
        Returns:
            Dict with validation result and formatted number
        """
        if not self.client:
            return {'valid': False, 'error': 'Twilio not configured'}
        
        try:
            # Use Lookup API
            phone = self.client.lookups.v2.phone_numbers(phone_number).fetch()
            
            return {
                'valid': True,
                'formatted': phone.phone_number,
                'country_code': phone.country_code,
                'national_format': phone.national_format,
            }
        except Exception as e:
            logger.error(f"Phone validation failed: {e}")
            return {'valid': False, 'error': str(e)}
    
    def get_message_status(self, message_sid):
        """
        Get status of a sent message
        
        Returns:
            Status string (queued, sent, delivered, failed, etc.)
        """
        if not self.client:
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'price': message.price,
                'date_sent': message.date_sent,
            }
        except Exception as e:
            logger.error(f"Failed to fetch message status: {e}")
            return None
    
    def setup_webhook(self, webhook_url):
        """
        Configure webhook for SMS replies
        
        Args:
            webhook_url: URL to receive incoming SMS
        """
        # Webhooks are typically configured in Twilio console
        # This is a placeholder for programmatic configuration
        logger.info(f"Configure webhook at: {webhook_url}")
        pass


class SMSNotificationPreferences:
    """Manage SMS notification preferences for users"""
    
    @staticmethod
    def get_preferences(user):
        """Get user's SMS notification preferences"""
        from forms.models import User
        
        # This would typically be stored in a UserProfile model
        return {
            'enabled': getattr(user, 'sms_notifications_enabled', False),
            'phone_number': getattr(user, 'phone_number', None),
            'notify_on_submission': True,
            'notify_on_comment': True,
            'notify_on_share': False,
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '08:00',
                'timezone': 'UTC'
            }
        }
    
    @staticmethod
    def update_preferences(user, preferences):
        """Update user's SMS notification preferences"""
        # Update user model with preferences
        # This would typically update a UserProfile model
        pass
    
    @staticmethod
    def should_send_notification(user, notification_type):
        """Check if notification should be sent based on preferences"""
        prefs = SMSNotificationPreferences.get_preferences(user)
        
        if not prefs['enabled'] or not prefs['phone_number']:
            return False
        
        # Check notification type preference
        pref_key = f'notify_on_{notification_type}'
        if pref_key in prefs and not prefs[pref_key]:
            return False
        
        # Check quiet hours
        if prefs['quiet_hours']['enabled']:
            from datetime import datetime
            import pytz
            
            tz = pytz.timezone(prefs['quiet_hours']['timezone'])
            now = datetime.now(tz)
            current_time = now.strftime('%H:%M')
            
            start = prefs['quiet_hours']['start']
            end = prefs['quiet_hours']['end']
            
            if start > end:  # Crosses midnight
                if current_time >= start or current_time < end:
                    return False
            else:
                if start <= current_time < end:
                    return False
        
        return True
