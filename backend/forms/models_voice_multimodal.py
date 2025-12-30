"""
Voice & Multimodal Input Models

Features:
- Voice-to-Text Form Filling with NLP
- Multimodal Input (Camera, QR, Barcode, OCR)
- Screen Reader Optimization with AI Alt-Text
- NFC Integration
- AR Form Preview
"""
from django.db import models
import uuid


# ============================================================================
# VOICE INPUT & PROCESSING
# ============================================================================

class VoiceFormConfig(models.Model):
    """Voice input configuration for forms"""
    VOICE_ENGINES = [
        ('whisper', 'OpenAI Whisper'),
        ('google', 'Google Speech-to-Text'),
        ('azure', 'Azure Speech'),
        ('aws', 'AWS Transcribe'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='voice_config')
    
    is_enabled = models.BooleanField(default=False)
    voice_engine = models.CharField(max_length=20, choices=VOICE_ENGINES, default='whisper')
    
    # Language settings
    primary_language = models.CharField(max_length=10, default='en-US')
    supported_languages = models.JSONField(default=list, help_text="Additional supported languages")
    auto_detect_language = models.BooleanField(default=True)
    
    # Voice interaction settings
    continuous_listening = models.BooleanField(default=False, help_text="Keep listening between fields")
    voice_commands_enabled = models.BooleanField(default=True, help_text="Enable next/back/submit commands")
    voice_feedback_enabled = models.BooleanField(default=True, help_text="Read back entered values")
    
    # TTS settings
    tts_enabled = models.BooleanField(default=True)
    tts_voice = models.CharField(max_length=50, default='alloy')
    tts_speed = models.FloatField(default=1.0)
    
    # Field reading
    read_field_labels = models.BooleanField(default=True)
    read_help_text = models.BooleanField(default=True)
    read_validation_errors = models.BooleanField(default=True)
    
    # NLP settings
    smart_parsing = models.BooleanField(default=True, help_text="Use NLP to parse voice input")
    context_awareness = models.BooleanField(default=True, help_text="Use conversation context")
    
    # Noise handling
    noise_cancellation = models.BooleanField(default=True)
    confidence_threshold = models.FloatField(default=0.75, help_text="Minimum confidence for acceptance")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'voice_form_configs'
    
    def __str__(self):
        return f"Voice config for {self.form.title}"


class VoiceInteraction(models.Model):
    """Log of voice interactions"""
    INTERACTION_TYPES = [
        ('transcription', 'Voice to Text'),
        ('command', 'Voice Command'),
        ('tts', 'Text to Speech'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='voice_interactions')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100)
    
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    field_id = models.CharField(max_length=100, blank=True)
    
    # Audio data
    audio_duration_ms = models.IntegerField(default=0)
    audio_url = models.URLField(blank=True)
    
    # Transcription
    transcribed_text = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0)
    language_detected = models.CharField(max_length=10, blank=True)
    
    # NLP parsing
    parsed_value = models.JSONField(null=True, blank=True, help_text="Extracted structured value")
    intent_detected = models.CharField(max_length=50, blank=True)
    entities_extracted = models.JSONField(default=list)
    
    # Result
    accepted = models.BooleanField(default=False)
    correction_needed = models.BooleanField(default=False)
    final_value = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voice_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', 'session_id']),
        ]
    
    def __str__(self):
        return f"Voice interaction - {self.interaction_type}"


# ============================================================================
# MULTIMODAL INPUT (CAMERA, QR, BARCODE, OCR)
# ============================================================================

class MultimodalInputConfig(models.Model):
    """Configuration for multimodal input methods"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='multimodal_config')
    
    # Camera features
    camera_enabled = models.BooleanField(default=False)
    front_camera_allowed = models.BooleanField(default=True)
    back_camera_allowed = models.BooleanField(default=True)
    
    # QR Code scanning
    qr_scanning_enabled = models.BooleanField(default=False)
    qr_auto_submit = models.BooleanField(default=False, help_text="Auto-submit after QR scan")
    
    # Barcode scanning
    barcode_scanning_enabled = models.BooleanField(default=False)
    barcode_formats = models.JSONField(
        default=list,
        help_text="Supported formats: CODE128, EAN13, QR, etc."
    )
    
    # OCR (Document scanning)
    ocr_enabled = models.BooleanField(default=False)
    ocr_languages = models.JSONField(default=list, help_text="Languages for OCR")
    ocr_document_types = models.JSONField(
        default=list,
        help_text="Document types: ID, passport, license, receipt, etc."
    )
    
    # ID verification
    id_verification_enabled = models.BooleanField(default=False)
    id_types_accepted = models.JSONField(
        default=list,
        help_text="Accepted ID types: passport, drivers_license, national_id"
    )
    
    # Image quality settings
    min_image_quality = models.IntegerField(default=70, help_text="Minimum quality %")
    max_file_size_mb = models.IntegerField(default=10)
    auto_enhance_images = models.BooleanField(default=True)
    
    # AR Preview
    ar_preview_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'multimodal_input_configs'
    
    def __str__(self):
        return f"Multimodal config for {self.form.title}"


class OCRExtraction(models.Model):
    """OCR extraction results from documents"""
    DOCUMENT_TYPES = [
        ('id_card', 'ID Card'),
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('business_card', 'Business Card'),
        ('receipt', 'Receipt'),
        ('invoice', 'Invoice'),
        ('form', 'Filled Form'),
        ('custom', 'Custom Document'),
    ]
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('review_needed', 'Review Needed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ocr_extractions')
    session_id = models.CharField(max_length=100)
    
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    # Input
    image_url = models.URLField()
    image_size = models.JSONField(default=dict, help_text="Width, height")
    
    # Extraction results
    raw_text = models.TextField(blank=True)
    extracted_fields = models.JSONField(
        default=dict,
        help_text="Field name to value mapping"
    )
    confidence_scores = models.JSONField(
        default=dict,
        help_text="Confidence per field"
    )
    
    # Field mapping
    field_mappings = models.JSONField(
        default=dict,
        help_text="Map OCR fields to form fields"
    )
    
    # Quality metrics
    overall_confidence = models.FloatField(default=0)
    image_quality_score = models.FloatField(default=0)
    
    # Review
    needs_manual_review = models.BooleanField(default=False)
    review_fields = models.JSONField(default=list, help_text="Fields requiring review")
    reviewed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ocr_extractions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OCR - {self.document_type} ({self.status})"


class QRBarcodesScan(models.Model):
    """QR/Barcode scan results"""
    SCAN_TYPES = [
        ('qr', 'QR Code'),
        ('code128', 'Code 128'),
        ('ean13', 'EAN-13'),
        ('ean8', 'EAN-8'),
        ('upc', 'UPC'),
        ('code39', 'Code 39'),
        ('datamatrix', 'Data Matrix'),
        ('pdf417', 'PDF417'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='qr_barcode_scans')
    session_id = models.CharField(max_length=100)
    
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES)
    raw_value = models.TextField()
    
    # Parsed data
    parsed_data = models.JSONField(default=dict, help_text="Parsed structured data")
    data_type = models.CharField(max_length=50, blank=True, help_text="URL, vCard, WiFi, etc.")
    
    # Field mapping
    target_field_id = models.CharField(max_length=100, blank=True)
    applied_to_fields = models.JSONField(default=dict, help_text="Field IDs and values applied")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'qr_barcode_scans'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.scan_type} scan - {self.raw_value[:50]}"


# ============================================================================
# ACCESSIBILITY & SCREEN READER
# ============================================================================

class AIAltText(models.Model):
    """AI-generated alt text for form images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ai_alt_texts')
    
    image_url = models.URLField()
    image_context = models.CharField(max_length=100, blank=True, help_text="header, field_image, etc.")
    field_id = models.CharField(max_length=100, blank=True)
    
    # AI generated alt text
    alt_text_generated = models.TextField()
    alt_text_language = models.CharField(max_length=10, default='en')
    
    # Multiple language versions
    translations = models.JSONField(default=dict, help_text="Language code to alt text mapping")
    
    # Quality
    confidence_score = models.FloatField(default=0)
    needs_review = models.BooleanField(default=False)
    
    # Manual override
    alt_text_manual = models.TextField(blank=True)
    manually_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_alt_texts'
    
    def __str__(self):
        return f"Alt text for {self.image_url[:50]}"
    
    @property
    def effective_alt_text(self):
        """Return manual alt text if available, otherwise AI generated"""
        return self.alt_text_manual if self.alt_text_manual else self.alt_text_generated


class ScreenReaderOptimization(models.Model):
    """Screen reader specific optimizations for forms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='screen_reader_optimization')
    
    # ARIA enhancements
    aria_live_announcements = models.BooleanField(default=True)
    announce_field_count = models.BooleanField(default=True)
    announce_required_fields = models.BooleanField(default=True)
    announce_validation_errors = models.BooleanField(default=True)
    announce_progress = models.BooleanField(default=True)
    
    # Navigation
    enable_landmarks = models.BooleanField(default=True)
    enable_skip_links = models.BooleanField(default=True)
    enable_heading_navigation = models.BooleanField(default=True)
    
    # Reading order
    custom_reading_order = models.JSONField(default=list, help_text="Custom field reading order")
    
    # Field descriptions
    field_descriptions = models.JSONField(
        default=dict,
        help_text="Enhanced descriptions for screen readers per field"
    )
    
    # Error handling
    error_summary_position = models.CharField(
        max_length=20,
        choices=[('top', 'Top'), ('bottom', 'Bottom'), ('inline', 'Inline')],
        default='top'
    )
    
    # Verbosity levels
    verbosity_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'screen_reader_optimizations'
    
    def __str__(self):
        return f"Screen reader config for {self.form.title}"


# ============================================================================
# NFC INTEGRATION
# ============================================================================

class NFCConfig(models.Model):
    """NFC tap-to-fill configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='nfc_configs')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    is_enabled = models.BooleanField(default=True)
    
    # NFC tag data
    nfc_tag_id = models.CharField(max_length=100, unique=True)
    nfc_data = models.JSONField(default=dict, help_text="Data encoded in NFC tag")
    
    # Field mappings
    field_mappings = models.JSONField(
        default=dict,
        help_text="NFC data keys to form field IDs"
    )
    
    # Auto-submit settings
    auto_populate_only = models.BooleanField(default=True)
    auto_submit = models.BooleanField(default=False)
    require_confirmation = models.BooleanField(default=True)
    
    # Usage stats
    usage_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nfc_configs'
    
    def __str__(self):
        return f"NFC: {self.name} for {self.form.title}"


class NFCScan(models.Model):
    """Log of NFC scans"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nfc_config = models.ForeignKey(NFCConfig, on_delete=models.CASCADE, related_name='scans')
    session_id = models.CharField(max_length=100)
    
    # Scan data
    scanned_data = models.JSONField(default=dict)
    device_info = models.JSONField(default=dict)
    
    # Result
    fields_populated = models.JSONField(default=dict)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'nfc_scans'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"NFC scan - {self.created_at}"


# ============================================================================
# AR FORM PREVIEW
# ============================================================================

class ARPreviewConfig(models.Model):
    """AR preview configuration for mobile forms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='ar_preview_config')
    
    is_enabled = models.BooleanField(default=False)
    
    # AR scene settings
    scene_background = models.CharField(
        max_length=20,
        choices=[
            ('transparent', 'Transparent'),
            ('blur', 'Blurred Camera'),
            ('custom', 'Custom Image'),
        ],
        default='blur'
    )
    custom_background_url = models.URLField(blank=True)
    
    # Form placement
    placement_type = models.CharField(
        max_length=20,
        choices=[
            ('floating', 'Floating'),
            ('surface', 'Surface Anchored'),
            ('wall', 'Wall Mounted'),
        ],
        default='floating'
    )
    
    # Size and position
    default_scale = models.FloatField(default=1.0)
    default_distance = models.FloatField(default=1.0, help_text="Distance from camera in meters")
    
    # Interaction settings
    allow_resize = models.BooleanField(default=True)
    allow_rotate = models.BooleanField(default=True)
    allow_reposition = models.BooleanField(default=True)
    
    # Visual effects
    shadow_enabled = models.BooleanField(default=True)
    glow_effect = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ar_preview_configs'
    
    def __str__(self):
        return f"AR Preview for {self.form.title}"


class ARSession(models.Model):
    """AR session tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ar_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    
    # Device info
    device_model = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    ar_framework = models.CharField(max_length=50, blank=True, help_text="ARKit, ARCore, WebXR")
    
    # Session metrics
    duration_seconds = models.IntegerField(default=0)
    interactions_count = models.IntegerField(default=0)
    form_completed = models.BooleanField(default=False)
    
    # Quality metrics
    tracking_quality = models.CharField(max_length=20, blank=True)
    frames_dropped = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ar_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"AR session {self.session_id[:8]}..."
