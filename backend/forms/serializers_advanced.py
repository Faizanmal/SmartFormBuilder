"""
Serializers for advanced form features
"""
from rest_framework import serializers
from forms.models_advanced import (
    FormStep, PartialSubmission, FormABTest, TeamMember,
    FormComment, FormShare, FormAnalytics, LeadScore,
    AutomatedFollowUp, WhiteLabelConfig, AuditLog, ConsentRecord,
    ConversationalSession, ScheduledReport
)


class FormStepSerializer(serializers.ModelSerializer):
    """Serializer for form steps"""
    
    class Meta:
        model = FormStep
        fields = ['id', 'form', 'step_number', 'title', 'description', 'fields', 'conditional_logic', 'created_at']
        read_only_fields = ['id', 'created_at']


class PartialSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for partial submissions"""
    
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = PartialSubmission
        fields = [
            'id', 'form', 'email', 'payload_json', 'current_step',
            'resume_token', 'is_abandoned', 'abandoned_at', 'recovery_email_sent',
            'expires_at', 'progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'resume_token', 'is_abandoned', 'abandoned_at', 'recovery_email_sent', 'created_at', 'updated_at']
    
    def get_progress(self, obj):
        schema = obj.form.schema_json
        total_steps = len(schema.get('steps', [schema]))
        return min(100, int((obj.current_step / total_steps) * 100))


class FormABTestSerializer(serializers.ModelSerializer):
    """Serializer for A/B tests"""
    
    variant_a_conversion_rate = serializers.ReadOnlyField()
    variant_b_conversion_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = FormABTest
        fields = [
            'id', 'form', 'name', 'description', 'variant_a_schema', 'variant_b_schema',
            'traffic_split', 'status', 'variant_a_views', 'variant_a_submissions',
            'variant_b_views', 'variant_b_submissions', 'variant_a_conversion_rate',
            'variant_b_conversion_rate', 'start_date', 'end_date', 'winner', 'created_at'
        ]
        read_only_fields = [
            'id', 'variant_a_views', 'variant_a_submissions', 'variant_b_views',
            'variant_b_submissions', 'winner', 'created_at'
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team members"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = TeamMember
        fields = ['id', 'team', 'user', 'user_email', 'role', 'invited_by', 'invited_at']
        read_only_fields = ['id', 'invited_by', 'invited_at']


class FormCommentSerializer(serializers.ModelSerializer):
    """Serializer for form comments"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    resolved_by_email = serializers.EmailField(source='resolved_by.email', read_only=True)
    
    class Meta:
        model = FormComment
        fields = [
            'id', 'form', 'user', 'user_email', 'field_id', 'content',
            'resolved', 'resolved_by', 'resolved_by_email', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'resolved_by', 'resolved_at', 'created_at', 'updated_at']


class FormShareSerializer(serializers.ModelSerializer):
    """Serializer for form sharing"""
    
    class Meta:
        model = FormShare
        fields = [
            'id', 'form', 'shared_with_user', 'shared_with_email', 'permission',
            'share_token', 'expires_at', 'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'share_token', 'created_by', 'created_at']


class FormAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for analytics events"""
    
    class Meta:
        model = FormAnalytics
        fields = [
            'id', 'form', 'session_id', 'event_type', 'field_id', 'field_label',
            'step_number', 'event_data', 'ip_address', 'user_agent', 'device_type',
            'browser', 'country', 'city', 'referrer', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LeadScoreSerializer(serializers.ModelSerializer):
    """Serializer for lead scores"""
    
    submission_data = serializers.JSONField(source='submission.payload_json', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    
    class Meta:
        model = LeadScore
        fields = [
            'id', 'submission', 'submission_data', 'total_score', 'score_breakdown',
            'quality', 'assigned_to', 'assigned_to_email', 'follow_up_status',
            'notes', 'last_contacted_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_score', 'score_breakdown', 'quality', 'created_at', 'updated_at']


class AutomatedFollowUpSerializer(serializers.ModelSerializer):
    """Serializer for automated follow-ups"""
    
    class Meta:
        model = AutomatedFollowUp
        fields = [
            'id', 'form', 'submission', 'sequence_step', 'send_after_hours',
            'subject', 'content', 'status', 'scheduled_for', 'sent_at',
            'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'sent_at', 'error_message', 'created_at']


class WhiteLabelConfigSerializer(serializers.ModelSerializer):
    """Serializer for white-label configuration"""
    
    class Meta:
        model = WhiteLabelConfig
        fields = [
            'id', 'custom_domain', 'logo_url', 'primary_color', 'secondary_color',
            'custom_css', 'email_from_name', 'email_from_address', 'email_footer',
            'hide_branding', 'custom_terms_url', 'custom_privacy_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'ssl_certificate': {'write_only': True},
            'ssl_key': {'write_only': True},
        }


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action', 'resource_type', 'resource_id',
            'details', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConsentRecordSerializer(serializers.ModelSerializer):
    """Serializer for consent records"""
    
    class Meta:
        model = ConsentRecord
        fields = [
            'id', 'submission', 'consent_type', 'granted', 'consent_text',
            'ip_address', 'user_agent', 'created_at', 'revoked_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationalSessionSerializer(serializers.ModelSerializer):
    """Serializer for conversational form sessions"""
    
    class Meta:
        model = ConversationalSession
        fields = [
            'id', 'form', 'session_token', 'conversation_history', 'collected_data',
            'current_field_id', 'is_complete', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'session_token', 'created_at', 'updated_at']


class ScheduledReportSerializer(serializers.ModelSerializer):
    """Serializer for scheduled reports"""
    
    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'form', 'schedule_type', 'recipients', 'report_options',
            'is_active', 'next_run', 'last_run', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'next_run', 'last_run', 'created_at', 'updated_at']
