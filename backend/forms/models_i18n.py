"""
Internationalization (i18n) models for multi-language support
"""
from django.db import models
import uuid


class Language(models.Model):
    """Supported languages in the platform"""
    code = models.CharField(max_length=10, unique=True, help_text="ISO 639-1 language code (e.g., 'en', 'es', 'ar')")
    name = models.CharField(max_length=100, help_text="Language name in English")
    native_name = models.CharField(max_length=100, help_text="Language name in native script")
    is_rtl = models.BooleanField(default=False, help_text="Right-to-left language")
    is_active = models.BooleanField(default=True)
    flag_emoji = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'languages'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class FormTranslation(models.Model):
    """Store translations for form fields and content"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    schema_translations = models.JSONField(
        default=dict,
        help_text="Field labels, placeholders, validation messages translated"
    )
    auto_translated = models.BooleanField(default=False, help_text="Whether this was auto-translated by AI")
    is_approved = models.BooleanField(default=False, help_text="Manual review approval")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_translations'
        unique_together = [['form', 'language']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.form.title} - {self.language.code}"


class SubmissionTranslation(models.Model):
    """Store translated submission field names for exports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    translated_data = models.JSONField(
        default=dict,
        help_text="Submission data with translated field names"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'submission_translations'
        unique_together = [['submission', 'language']]
    
    def __str__(self):
        return f"Submission {self.submission.id} - {self.language.code}"
