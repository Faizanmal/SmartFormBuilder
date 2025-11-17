"""
Serializers for the forms app
"""
from rest_framework import serializers
from .models import Form, Submission, FormTemplate


class FormSerializer(serializers.ModelSerializer):
    """Serializer for Form model"""
    
    conversion_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Form
        fields = [
            'id', 'title', 'slug', 'description', 'schema_json',
            'settings_json', 'published_at', 'is_active',
            'views_count', 'submissions_count', 'conversion_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'submissions_count', 'created_at', 'updated_at']


class FormCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating forms"""
    
    prompt = serializers.CharField(write_only=True, required=False, help_text="Natural language description for AI generation")
    context = serializers.CharField(write_only=True, required=False, help_text="Additional context for AI generation")
    
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'schema_json', 'settings_json', 'prompt', 'context']
        read_only_fields = ['id']


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model"""
    
    class Meta:
        model = Submission
        fields = ['id', 'form', 'payload_json', 'ip_address', 'user_agent', 'processed_at', 'created_at']
        read_only_fields = ['id', 'processed_at', 'created_at']


class SubmissionCreateSerializer(serializers.Serializer):
    """Serializer for creating submissions (public API)"""
    
    payload = serializers.JSONField()
    
    def validate_payload(self, value):
        """Validate that payload contains required fields"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Payload must be a JSON object")
        return value


class FormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for FormTemplate model"""
    
    class Meta:
        model = FormTemplate
        fields = [
            'id', 'name', 'description', 'category', 'schema_json',
            'thumbnail_url', 'usage_count', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']


class FormGenerateSerializer(serializers.Serializer):
    """Serializer for AI form generation request"""
    
    prompt = serializers.CharField(max_length=2000, help_text="Natural language description of the form")
    context = serializers.CharField(max_length=500, required=False, allow_blank=True, help_text="Business type or additional context")
    
    def validate_prompt(self, value):
        """Validate prompt is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Prompt cannot be empty")
        return value.strip()
