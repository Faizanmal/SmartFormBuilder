"""
UX & Design Enhancement Models

Features:
- Theme Marketplace
- Brand Consistency Engine  
- Accessibility Auto-Fix
- Real-time Co-Editing
- Form Version Comparison
- Team Workflow Management
"""
import uuid
from django.db import models
from django.conf import settings


class ThemeMarketplace(models.Model):
    """
    Marketplace for form themes
    Supports browsing, purchasing, and rating themes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Theme info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    preview_image = models.URLField(blank=True)
    preview_images = models.JSONField(default=list, help_text="Array of preview image URLs")
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marketplace_themes'
    )
    author_name = models.CharField(max_length=200, blank=True)
    author_website = models.URLField(blank=True)
    
    # Categorization
    category = models.CharField(
        max_length=50,
        choices=[
            ('business', 'Business'),
            ('creative', 'Creative'),
            ('minimal', 'Minimal'),
            ('modern', 'Modern'),
            ('classic', 'Classic'),
            ('colorful', 'Colorful'),
            ('dark', 'Dark Mode'),
            ('accessible', 'Accessibility-First'),
            ('industry', 'Industry-Specific'),
        ],
        default='modern'
    )
    tags = models.JSONField(default=list)
    industries = models.JSONField(default=list, help_text="Suitable industries")
    
    # Theme configuration
    theme_config = models.JSONField(
        default=dict,
        help_text="Complete theme configuration"
    )
    css_variables = models.JSONField(default=dict)
    custom_css = models.TextField(blank=True)
    custom_fonts = models.JSONField(default=list)
    
    # Pricing
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # Stats
    download_count = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-rating_average', '-download_count']
    
    def __str__(self):
        return self.name


class ThemePurchase(models.Model):
    """Track theme purchases"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    theme = models.ForeignKey(
        ThemeMarketplace,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='theme_purchases'
    )
    
    # Transaction
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    transaction_id = models.CharField(max_length=200, blank=True)
    payment_provider = models.CharField(max_length=50, default='stripe')
    
    # License
    license_key = models.CharField(max_length=100, unique=True)
    license_type = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Single Use'),
            ('unlimited', 'Unlimited Use'),
            ('team', 'Team License'),
        ],
        default='unlimited'
    )
    
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['theme', 'user']


class ThemeReview(models.Model):
    """User reviews for marketplace themes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    theme = models.ForeignKey(
        ThemeMarketplace,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='theme_reviews'
    )
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(blank=True)
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['theme', 'user']


class EnhancedBrandGuideline(models.Model):
    """
    Enhanced brand consistency engine
    Stores and enforces brand guidelines across forms with AI validation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enhanced_brand_guidelines'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Colors
    primary_color = models.CharField(max_length=7, default='#000000')
    secondary_color = models.CharField(max_length=7, default='#666666')
    accent_color = models.CharField(max_length=7, default='#0066cc')
    background_color = models.CharField(max_length=7, default='#ffffff')
    text_color = models.CharField(max_length=7, default='#333333')
    error_color = models.CharField(max_length=7, default='#dc3545')
    success_color = models.CharField(max_length=7, default='#28a745')
    
    color_palette = models.JSONField(
        default=list,
        help_text="Full color palette with names and hex values"
    )
    
    # Typography
    primary_font = models.CharField(max_length=100, default='Inter')
    secondary_font = models.CharField(max_length=100, blank=True)
    heading_font = models.CharField(max_length=100, blank=True)
    font_scale = models.FloatField(default=1.0)
    base_font_size = models.IntegerField(default=16)
    
    typography_config = models.JSONField(
        default=dict,
        help_text="Detailed typography settings"
    )
    
    # Logo & Assets
    logo_url = models.URLField(blank=True)
    logo_dark_url = models.URLField(blank=True, help_text="Logo for dark backgrounds")
    favicon_url = models.URLField(blank=True)
    
    # Spacing & Layout
    border_radius = models.IntegerField(default=4)
    spacing_unit = models.IntegerField(default=8)
    max_width = models.IntegerField(default=640)
    
    # Component styles
    button_style = models.JSONField(default=dict)
    input_style = models.JSONField(default=dict)
    card_style = models.JSONField(default=dict)
    
    # Voice & Tone
    voice_guidelines = models.JSONField(
        default=dict,
        help_text="AI guidelines for text generation"
    )
    
    # Validation rules
    enforce_colors = models.BooleanField(default=True)
    enforce_fonts = models.BooleanField(default=True)
    enforce_spacing = models.BooleanField(default=False)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-updated_at']
    
    def __str__(self):
        return self.name


class BrandValidation(models.Model):
    """Track brand guideline validations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    guideline = models.ForeignKey(
        EnhancedBrandGuideline,
        on_delete=models.CASCADE,
        related_name='validations'
    )
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='brand_validations'
    )
    
    # Validation results
    is_compliant = models.BooleanField(default=False)
    compliance_score = models.FloatField(default=0)
    
    issues = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    auto_fixes_available = models.JSONField(default=list)
    
    validated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-validated_at']


class AccessibilityAutoFix(models.Model):
    """
    Automated accessibility fixes
    AI-powered detection and correction of accessibility issues
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='accessibility_auto_fixes'
    )
    
    # Configuration
    is_enabled = models.BooleanField(default=True)
    auto_apply = models.BooleanField(
        default=False,
        help_text="Automatically apply fixes without confirmation"
    )
    
    # Fix categories
    fix_color_contrast = models.BooleanField(default=True)
    fix_missing_labels = models.BooleanField(default=True)
    fix_focus_indicators = models.BooleanField(default=True)
    fix_aria_attributes = models.BooleanField(default=True)
    fix_heading_structure = models.BooleanField(default=True)
    fix_form_validation = models.BooleanField(default=True)
    fix_touch_targets = models.BooleanField(default=True)
    fix_motion = models.BooleanField(default=True)
    
    # WCAG compliance level
    target_level = models.CharField(
        max_length=10,
        choices=[
            ('A', 'Level A'),
            ('AA', 'Level AA'),
            ('AAA', 'Level AAA'),
        ],
        default='AA'
    )
    
    # Stats
    total_fixes_applied = models.IntegerField(default=0)
    last_scan_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Accessibility auto fixes"


class AccessibilityFix(models.Model):
    """Individual accessibility fix record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    config = models.ForeignKey(
        AccessibilityAutoFix,
        on_delete=models.CASCADE,
        related_name='fixes'
    )
    
    # Issue details
    issue_type = models.CharField(max_length=100)
    wcag_criterion = models.CharField(max_length=20, help_text="e.g., 1.4.3")
    severity = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('serious', 'Serious'),
            ('moderate', 'Moderate'),
            ('minor', 'Minor'),
        ]
    )
    
    # Location
    element_selector = models.CharField(max_length=500, blank=True)
    field_id = models.CharField(max_length=100, blank=True)
    
    # Fix details
    original_value = models.JSONField(default=dict)
    fixed_value = models.JSONField(default=dict)
    fix_description = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('detected', 'Detected'),
            ('pending', 'Pending Review'),
            ('applied', 'Applied'),
            ('rejected', 'Rejected'),
            ('reverted', 'Reverted'),
        ],
        default='detected'
    )
    
    applied_at = models.DateTimeField(null=True)
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class RealTimeCollabSession(models.Model):
    """
    Real-time collaboration session for form editing
    Supports multiple editors with presence awareness
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='collab_sessions'
    )
    
    # Session info
    session_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    # Participants
    participants = models.JSONField(
        default=list,
        help_text="List of active participants with cursor positions"
    )
    max_participants = models.IntegerField(default=10)
    
    # Conflict resolution
    conflict_resolution = models.CharField(
        max_length=20,
        choices=[
            ('last_write', 'Last Write Wins'),
            ('first_write', 'First Write Wins'),
            ('merge', 'Auto Merge'),
            ('manual', 'Manual Resolution'),
        ],
        default='merge'
    )
    
    # Operation log for CRDT
    operations = models.JSONField(
        default=list,
        help_text="Ordered list of operations for conflict resolution"
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-started_at']


class CollabParticipant(models.Model):
    """Participant in a collaboration session"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(
        RealTimeCollabSession,
        on_delete=models.CASCADE,
        related_name='session_participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collab_participations'
    )
    
    # Presence
    color = models.CharField(max_length=7, help_text="Cursor/highlight color")
    cursor_position = models.JSONField(default=dict)
    current_field = models.CharField(max_length=100, blank=True)
    
    # Permissions
    can_edit = models.BooleanField(default=True)
    can_comment = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True)


class CollabOperation(models.Model):
    """
    Operation in a collaboration session (for CRDT)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    session = models.ForeignKey(
        RealTimeCollabSession,
        on_delete=models.CASCADE,
        related_name='session_operations'
    )
    participant = models.ForeignKey(
        CollabParticipant,
        on_delete=models.CASCADE,
        related_name='operations'
    )
    
    # Operation details
    operation_type = models.CharField(
        max_length=20,
        choices=[
            ('insert', 'Insert'),
            ('delete', 'Delete'),
            ('update', 'Update'),
            ('move', 'Move'),
        ]
    )
    
    # Target
    target_type = models.CharField(max_length=50)  # field, section, setting
    target_id = models.CharField(max_length=100)
    target_path = models.JSONField(default=list, help_text="Path to nested property")
    
    # Change
    old_value = models.JSONField(null=True)
    new_value = models.JSONField(null=True)
    
    # Vector clock for ordering
    vector_clock = models.JSONField(default=dict)
    sequence_number = models.BigIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sequence_number']


class FormVersionDiff(models.Model):
    """
    Form version comparison and diff
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='version_diffs'
    )
    
    # Versions being compared
    version_a = models.ForeignKey(
        'forms.FormVersion',
        on_delete=models.CASCADE,
        related_name='diffs_as_a'
    )
    version_b = models.ForeignKey(
        'forms.FormVersion',
        on_delete=models.CASCADE,
        related_name='diffs_as_b'
    )
    
    # Diff results
    changes = models.JSONField(
        default=list,
        help_text="List of changes between versions"
    )
    
    # Summary
    fields_added = models.IntegerField(default=0)
    fields_removed = models.IntegerField(default=0)
    fields_modified = models.IntegerField(default=0)
    settings_changed = models.IntegerField(default=0)
    
    # Visual diff
    visual_diff_url = models.URLField(blank=True)
    side_by_side_diff = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['version_a', 'version_b']


class TeamWorkspace(models.Model):
    """
    Team workspace for collaborative form management
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_workspaces'
    )
    
    # Settings
    default_brand_guideline = models.ForeignKey(
        EnhancedBrandGuideline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Features
    features = models.JSONField(
        default=dict,
        help_text="Enabled workspace features"
    )
    
    # Stats
    form_count = models.IntegerField(default=0)
    member_count = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    """Member of a team workspace"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    workspace = models.ForeignKey(
        TeamWorkspace,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspace_memberships'
    )
    
    # Role
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Admin'),
            ('editor', 'Editor'),
            ('viewer', 'Viewer'),
        ],
        default='viewer'
    )
    
    # Permissions
    can_create_forms = models.BooleanField(default=True)
    can_delete_forms = models.BooleanField(default=False)
    can_publish_forms = models.BooleanField(default=False)
    can_view_submissions = models.BooleanField(default=True)
    can_export_data = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    
    custom_permissions = models.JSONField(default=dict)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_workspace_invites'
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True)
    
    class Meta:
        unique_together = ['workspace', 'user']


class WorkspaceInvite(models.Model):
    """Pending workspace invitation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    workspace = models.ForeignKey(
        TeamWorkspace,
        on_delete=models.CASCADE,
        related_name='pending_invites'
    )
    
    email = models.EmailField()
    role = models.CharField(max_length=20, default='viewer')
    
    invite_token = models.CharField(max_length=100, unique=True)
    
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspace_invites_sent'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
            ('expired', 'Expired'),
        ],
        default='pending'
    )
    
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True)


class EnhancedFormComment(models.Model):
    """
    Enhanced comments on form elements for collaboration with threading
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='enhanced_collab_comments'
    )
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enhanced_form_comments_authored'
    )
    
    # Target
    target_type = models.CharField(
        max_length=20,
        choices=[
            ('form', 'Entire Form'),
            ('field', 'Field'),
            ('section', 'Section'),
            ('setting', 'Setting'),
        ],
        default='form'
    )
    target_id = models.CharField(max_length=100, blank=True)
    
    # Comment
    content = models.TextField()
    
    # Thread
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Mentions
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='mentioned_in_comments',
        blank=True
    )
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class DesignSystem(models.Model):
    """
    Custom design system for consistent form styling
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='design_systems'
    )
    workspace = models.ForeignKey(
        TeamWorkspace,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='design_systems'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Design tokens
    colors = models.JSONField(default=dict)
    typography = models.JSONField(default=dict)
    spacing = models.JSONField(default=dict)
    borders = models.JSONField(default=dict)
    shadows = models.JSONField(default=dict)
    animations = models.JSONField(default=dict)
    
    # Component definitions
    components = models.JSONField(
        default=dict,
        help_text="Component style definitions"
    )
    
    # Breakpoints
    breakpoints = models.JSONField(
        default=dict,
        help_text="Responsive breakpoints"
    )
    
    # Generated CSS
    compiled_css = models.TextField(blank=True)
    css_variables = models.TextField(blank=True)
    
    is_published = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default='1.0.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class EnhancedFormTemplate(models.Model):
    """
    Enhanced form templates with categorization, sharing, and marketplace integration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    
    # Creator
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_form_templates'
    )
    
    # Template content
    schema = models.JSONField(default=dict)
    settings = models.JSONField(default=dict)
    theme_config = models.JSONField(default=dict)
    
    # Categorization
    category = models.CharField(max_length=100, blank=True)
    subcategory = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list)
    industry = models.CharField(max_length=100, blank=True)
    use_case = models.CharField(max_length=100, blank=True)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Stats
    use_count = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    # Workspace
    workspace = models.ForeignKey(
        TeamWorkspace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-use_count']
    
    def __str__(self):
        return self.name


class AnimationConfig(models.Model):
    """
    Form animation and transition configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='animation_config'
    )
    
    # Enable animations
    is_enabled = models.BooleanField(default=True)
    respect_reduced_motion = models.BooleanField(default=True)
    
    # Page/Step transitions
    page_transition = models.CharField(
        max_length=50,
        choices=[
            ('none', 'None'),
            ('fade', 'Fade'),
            ('slide', 'Slide'),
            ('slide-up', 'Slide Up'),
            ('scale', 'Scale'),
            ('flip', 'Flip'),
        ],
        default='fade'
    )
    transition_duration = models.IntegerField(default=300, help_text="Duration in ms")
    transition_easing = models.CharField(max_length=100, default='ease-in-out')
    
    # Field animations
    field_entrance = models.CharField(max_length=50, default='fade-in')
    field_stagger = models.IntegerField(default=50, help_text="Stagger delay in ms")
    
    # Interaction animations
    focus_animation = models.CharField(max_length=50, default='glow')
    error_animation = models.CharField(max_length=50, default='shake')
    success_animation = models.CharField(max_length=50, default='check')
    
    # Loading states
    loading_animation = models.CharField(max_length=50, default='spinner')
    skeleton_loading = models.BooleanField(default=True)
    
    # Custom animations
    custom_keyframes = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
