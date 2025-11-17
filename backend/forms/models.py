from django.db import models
from django.utils.text import slugify
import uuid
import json


class Form(models.Model):
    """Form model storing the generated form schema"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='forms')
    team = models.ForeignKey('users.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='forms')
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    schema_json = models.JSONField(default=dict, help_text="Complete form schema with fields and logic")
    settings_json = models.JSONField(default=dict, help_text="Integrations, privacy, and other settings")
    published_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    submissions_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forms'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['user', '-created_at']),
        ]
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:200]
            slug = base_slug
            counter = 1
            while Form.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def conversion_rate(self):
        """Calculate conversion rate (submissions / views)"""
        if self.views_count == 0:
            return 0
        return round((self.submissions_count / self.views_count) * 100, 2)


class Submission(models.Model):
    """Form submission data"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    payload_json = models.JSONField(help_text="Complete form submission data")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Payment fields
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, null=True, blank=True)
    payment_id = models.CharField(max_length=255, blank=True, help_text="Stripe Payment Intent ID")
    payment_amount = models.IntegerField(null=True, blank=True, help_text="Payment amount in cents")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', '-created_at']),
        ]
        
    def __str__(self):
        return f"Submission for {self.form.title} at {self.created_at}"


class FormTemplate(models.Model):
    """Pre-built form templates for quick start"""
    
    CATEGORY_CHOICES = [
        ('photography', 'Photography'),
        ('health', 'Health & Wellness'),
        ('fitness', 'Fitness & Gym'),
        ('real_estate', 'Real Estate'),
        ('consulting', 'Consulting'),
        ('events', 'Events & Catering'),
        ('general', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    schema_json = models.JSONField(help_text="Template form schema")
    thumbnail_url = models.URLField(blank=True)
    usage_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_templates'
        ordering = ['-is_featured', '-usage_count']
        
    def __str__(self):
        return self.name
