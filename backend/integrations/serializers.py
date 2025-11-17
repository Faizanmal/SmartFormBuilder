"""
Serializers for the integrations app
"""
from rest_framework import serializers
from .models import Integration, WebhookLog


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Integration model"""
    
    class Meta:
        model = Integration
        fields = [
            'id', 'type', 'name', 'config_json', 'status',
            'last_triggered_at', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'last_triggered_at', 'error_message', 'created_at', 'updated_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    """Serializer for WebhookLog model"""
    
    integration_name = serializers.CharField(source='integration.name', read_only=True)
    
    class Meta:
        model = WebhookLog
        fields = [
            'id', 'integration', 'integration_name', 'submission',
            'payload_json', 'response_status_code', 'response_body',
            'status', 'retry_count', 'created_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'created_at', 'delivered_at']
