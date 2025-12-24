from django.db import models
from django.utils.text import slugify
import uuid


class Form(models.Model):
    """Form model storing the generated form schema"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='forms')
    team = models.ForeignKey('users.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='forms')
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    schema_json = models.JSONField(default=dict, help_text="Complete form schema with fields and logic")
    settings_json = models.JSONField(default=dict, help_text="Integrations, privacy, and other settings")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1, help_text="Version number for tracking changes")
    views_count = models.IntegerField(default=0)
    submissions_count = models.IntegerField(default=0)
    completion_count = models.IntegerField(default=0, help_text="Submissions marked as complete")
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
    
    @property
    def completion_rate(self):
        """Calculate completion rate (completed / total submissions)"""
        if self.submissions_count == 0:
            return 0
        return round((self.completion_count / self.submissions_count) * 100, 2)
    
    def create_version(self):
        """Create a new version of the form"""
        FormVersion.objects.create(
            form=self,
            version=self.version,
            schema_json=self.schema_json,
            settings_json=self.settings_json
        )
        self.version += 1
        self.save(update_fields=['version'])


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


class FormVersion(models.Model):
    """Form version history for tracking changes"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='versions')
    version = models.IntegerField()
    schema_json = models.JSONField()
    settings_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_versions'
        ordering = ['-version']
        unique_together = ['form', 'version']
        
    def __str__(self):
        return f"{self.form.title} - v{self.version}"


class NotificationConfig(models.Model):
    """Email/SMS notification configuration for forms"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
    ]
    
    TRIGGER_CHOICES = [
        ('on_submit', 'On Submission'),
        ('on_payment', 'On Payment Success'),
        ('on_failure', 'On Payment Failure'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='on_submit')
    recipient = models.CharField(max_length=500, help_text="Email address, phone number, or webhook URL")
    subject = models.CharField(max_length=500, blank=True)
    template = models.TextField(help_text="Email/SMS template with {{field_name}} placeholders")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_configs'
        
    def __str__(self):
        return f"{self.form.title} - {self.type} to {self.recipient}"


class FormDraft(models.Model):
    """Save and resume functionality - stores partial form submissions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='drafts')
    draft_token = models.CharField(max_length=64, unique=True, db_index=True)
    payload_json = models.JSONField(default=dict, help_text="Partial submission data")
    current_step = models.IntegerField(default=0, help_text="Current step in multi-step form")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    email = models.EmailField(blank=True, help_text="Email to send resume link")
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_drafts'
        indexes = [
            models.Index(fields=['draft_token']),
            models.Index(fields=['form', 'expires_at']),
        ]
        
    def __str__(self):
        return f"Draft for {self.form.title} - {self.draft_token[:8]}..."
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at < timezone.now()


class FormVariant(models.Model):
    """A/B testing variant of a form"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255)
    schema_json = models.JSONField(help_text="Variant form schema")
    traffic_percentage = models.IntegerField(default=50, help_text="Percentage of traffic to this variant")
    views_count = models.IntegerField(default=0)
    submissions_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_variants'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.form.title} - Variant: {self.name}"
    
    @property
    def conversion_rate(self):
        if self.views_count == 0:
            return 0
        return round((self.submissions_count / self.views_count) * 100, 2)


class ABTest(models.Model):
    """A/B test configuration"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='ab_tests_basic')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    winner_variant = models.ForeignKey(FormVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_tests')
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ab_tests'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"A/B Test: {self.name} for {self.form.title}"
