"""
Custom themes and branding engine models
"""
from django.db import models
import uuid


class Theme(models.Model):
    """Custom themes for form styling"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='themes')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False, help_text="Share in theme marketplace")
    is_premium = models.BooleanField(default=False)
    
    # Color scheme
    colors = models.JSONField(default=dict, help_text="""
    {
        "primary": "#3B82F6",
        "secondary": "#8B5CF6",
        "accent": "#10B981",
        "background": "#FFFFFF",
        "surface": "#F3F4F6",
        "text": "#111827",
        "textSecondary": "#6B7280",
        "error": "#EF4444",
        "success": "#10B981",
        "warning": "#F59E0B"
    }
    """)
    
    # Typography
    typography = models.JSONField(default=dict, help_text="""
    {
        "fontFamily": "Inter, sans-serif",
        "headingFont": "Poppins, sans-serif",
        "fontSize": "16px",
        "headingSizes": {"h1": "2rem", "h2": "1.5rem", "h3": "1.25rem"}
    }
    """)
    
    # Layout & spacing
    layout = models.JSONField(default=dict, help_text="""
    {
        "borderRadius": "8px",
        "spacing": "medium",
        "containerWidth": "800px",
        "fieldSpacing": "20px"
    }
    """)
    
    # Component styles
    components = models.JSONField(default=dict, help_text="""
    {
        "button": {"style": "solid", "size": "medium"},
        "input": {"variant": "outlined", "size": "medium"},
        "card": {"shadow": "medium", "border": true}
    }
    """)
    
    # Custom CSS
    custom_css = models.TextField(
        blank=True,
        help_text="Custom CSS (sandboxed for security)"
    )
    
    # Custom JavaScript (with restrictions)
    custom_js = models.TextField(
        blank=True,
        help_text="Custom JS (sandboxed, limited to theme behaviors)"
    )
    
    # Preview image
    preview_image_url = models.URLField(blank=True)
    
    # Marketplace stats
    downloads_count = models.IntegerField(default=0)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.IntegerField(default=0)
    
    # Brand consistency
    brand_guidelines = models.JSONField(
        default=dict,
        blank=True,
        help_text="Brand rules (e.g., required colors, fonts)"
    )
    enforce_guidelines = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'themes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_public', '-downloads_count']),
        ]
    
    def __str__(self):
        return self.name


class FormTheme(models.Model):
    """Association between forms and themes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='theme_config')
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True, related_name='forms')
    
    # Theme overrides (customize theme per form)
    color_overrides = models.JSONField(default=dict, blank=True)
    typography_overrides = models.JSONField(default=dict, blank=True)
    layout_overrides = models.JSONField(default=dict, blank=True)
    
    # Mobile-specific overrides
    mobile_overrides = models.JSONField(
        default=dict,
        blank=True,
        help_text="Mobile-specific theme adjustments"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_themes'
    
    def __str__(self):
        return f"{self.form.title} - {self.theme.name if self.theme else 'No theme'}"


class ThemeRating(models.Model):
    """User ratings for marketplace themes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='theme_ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'theme_ratings'
        unique_together = [['theme', 'user']]
    
    def __str__(self):
        return f"{self.theme.name} - {self.rating} stars"


class BrandGuideline(models.Model):
    """Brand consistency rules and checks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='brand_guidelines')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Color palette requirements
    required_colors = models.JSONField(
        default=list,
        help_text="List of required brand colors with hex codes"
    )
    forbidden_colors = models.JSONField(default=list, blank=True)
    
    # Typography requirements
    required_fonts = models.JSONField(default=list)
    forbidden_fonts = models.JSONField(default=list, blank=True)
    
    # Logo requirements
    logo_url = models.URLField(blank=True)
    logo_placement_rules = models.JSONField(default=dict, blank=True)
    
    # Validation rules
    min_contrast_ratio = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=4.5,
        help_text="WCAG AA compliance"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'brand_guidelines'
    
    def __str__(self):
        return self.name
