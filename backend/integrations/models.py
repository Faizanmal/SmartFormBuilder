from django.db import models
import uuid
from .encryption import encrypt_dict, decrypt_dict


class Integration(models.Model):
    """External integrations for form submissions"""
    
    TYPE_CHOICES = [
        ('google_sheets', 'Google Sheets'),
        ('notion', 'Notion'),
        ('webhook', 'Webhook'),
        ('stripe', 'Stripe'),
        ('email', 'Email'),
        ('zapier', 'Zapier'),
        ('slack', 'Slack'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='integrations')
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='integrations', null=True, blank=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    name = models.CharField(max_length=255)
    config_json = models.JSONField(help_text="Encrypted configuration data")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integrations'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"
    
    def set_config(self, config_dict):
        """Encrypt and store configuration"""
        self.config_json = encrypt_dict(config_dict)
    
    def get_config(self):
        """Decrypt and return configuration"""
        return decrypt_dict(self.config_json)


class WebhookLog(models.Model):
    """Log of webhook deliveries"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='webhook_logs')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='webhook_logs')
    payload_json = models.JSONField()
    response_status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'webhook_logs'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Webhook {self.status} - {self.integration.name}"
