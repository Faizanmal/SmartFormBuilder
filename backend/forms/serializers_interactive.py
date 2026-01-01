"""
Django REST Framework serializers for all interactive feature models.
Includes nested serializers, custom fields, and validation logic.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models_interactive import (
    CollaborationSession, UserSession, CollaborationMessage, CursorPosition,
    GamificationProfile, Achievement, UserAchievement, PointsLog, DailyStreak,
    InteractiveFormAnalytics, InteractiveFieldAnalytics, InteractiveAnalyticsEvent, InteractiveAnalyticsSnapshot,
    InteractiveWorkflow, InteractiveWorkflowStep, InteractiveWorkflowExecution, InteractiveWorkflowStepExecution,
    VoiceTranscription, VoiceCommand,
    ChatSession, ChatMessage, ChatSuggestion,
    FormSubmission, SubmissionField,
    ARAsset, ARPreview,
    GestureSettings, GestureEvent,
)

User = get_user_model()


# ==================== COLLABORATION SERIALIZERS ====================

class CursorPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursorPosition
        fields = ['id', 'x', 'y', 'field_id', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class UserSessionSerializer(serializers.ModelSerializer):
    cursor = CursorPositionSerializer(read_only=True)
    user_data = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = ['id', 'username', 'email', 'color', 'joined_at', 'left_at', 'last_activity', 'cursor', 'user_data']
        read_only_fields = ['id', 'joined_at', 'last_activity']
    
    def get_user_data(self, obj):
        if obj.user:
            return {'id': obj.user.id, 'email': obj.user.email}
        return None


class CollaborationMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user_session.username', read_only=True)
    user_color = serializers.CharField(source='user_session.color', read_only=True)
    read_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationMessage
        fields = ['id', 'message_type', 'content', 'timestamp', 'user_name', 'user_color', 'read_count']
        read_only_fields = ['id', 'timestamp']
    
    def get_read_count(self, obj):
        return obj.read_by.count()


class CollaborationSessionSerializer(serializers.ModelSerializer):
    users = UserSessionSerializer(many=True, read_only=True)
    messages = CollaborationMessageSerializer(many=True, read_only=True)
    active_user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationSession
        fields = ['id', 'form_id', 'created_at', 'updated_at', 'is_active', 'max_users', 
                  'users', 'messages', 'active_user_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_user_count(self, obj):
        return obj.users.filter(left_at__isnull=True).count()


# ==================== GAMIFICATION SERIALIZERS ====================

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'key', 'name', 'description', 'icon', 'difficulty', 'points_reward', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'unlocked_at']
        read_only_fields = ['id', 'unlocked_at']


class PointsLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsLog
        fields = ['id', 'amount', 'reason', 'description', 'form_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class DailyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStreak
        fields = ['id', 'current_count', 'max_count', 'last_activity_date', 'created_at']
        read_only_fields = ['id', 'last_activity_date', 'created_at']


class GamificationProfileSerializer(serializers.ModelSerializer):
    achievements = UserAchievementSerializer(source='user.achievements', many=True, read_only=True)
    points_logs = PointsLogSerializer(source='user.points_logs', many=True, read_only=True)
    daily_streak = DailyStreakSerializer(source='user.daily_streak', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = GamificationProfile
        fields = ['id', 'user_name', 'total_points', 'level', 'experience', 'experience_to_next_level',
                  'current_streak', 'longest_streak', 'created_at', 'updated_at',
                  'achievements', 'points_logs', 'daily_streak']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== ANALYTICS SERIALIZERS ====================

class InteractiveFieldAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveFieldAnalytics
        fields = ['id', 'field_id', 'field_label', 'views', 'interactions', 'drop_offs',
                  'average_time_spent', 'error_count', 'help_clicks']
        read_only_fields = ['id']


class InteractiveAnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveAnalyticsEvent
        fields = ['id', 'event_type', 'session_id', 'field_id', 'value', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class InteractiveAnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveAnalyticsSnapshot
        fields = ['id', 'period', 'period_date', 'views', 'submissions', 'completion_rate']
        read_only_fields = ['id', 'period_date']


class InteractiveFormAnalyticsSerializer(serializers.ModelSerializer):
    fields = InteractiveFieldAnalyticsSerializer(many=True, read_only=True)
    snapshots = InteractiveAnalyticsSnapshotSerializer(many=True, read_only=True)
    events_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InteractiveFormAnalytics
        fields = ['id', 'form_id', 'total_views', 'total_submissions', 'completion_rate',
                  'average_completion_time', 'bounce_rate', 'conversion_rate',
                  'created_at', 'last_updated', 'fields', 'snapshots', 'events_count']
        read_only_fields = ['id', 'created_at', 'last_updated']
    
    def get_events_count(self, obj):
        return obj.events.count()


# ==================== WORKFLOW SERIALIZERS ====================

class InteractiveWorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveWorkflowStep
        fields = ['id', 'order', 'action_type', 'action_config', 'condition']
        read_only_fields = ['id']


class InteractiveWorkflowStepExecutionSerializer(serializers.ModelSerializer):
    step_detail = InteractiveWorkflowStepSerializer(source='step', read_only=True)
    
    class Meta:
        model = InteractiveWorkflowStepExecution
        fields = ['id', 'step_detail', 'status', 'input_data', 'output_data', 'error_message',
                  'started_at', 'completed_at']
        read_only_fields = ['id', 'started_at', 'completed_at']


class InteractiveWorkflowExecutionSerializer(serializers.ModelSerializer):
    step_executions = InteractiveWorkflowStepExecutionSerializer(many=True, read_only=True)
    
    class Meta:
        model = InteractiveWorkflowExecution
        fields = ['id', 'status', 'trigger_data', 'result', 'error_message',
                  'started_at', 'completed_at', 'execution_time', 'step_executions']
        read_only_fields = ['id', 'started_at', 'completed_at']


class InteractiveWorkflowSerializer(serializers.ModelSerializer):
    steps = InteractiveWorkflowStepSerializer(many=True, read_only=True)
    executions = InteractiveWorkflowExecutionSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    executions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InteractiveWorkflow
        fields = ['id', 'name', 'description', 'form_id', 'owner_name', 'status', 'trigger_type',
                  'trigger_config', 'is_active', 'created_at', 'updated_at', 'published_at',
                  'steps', 'executions', 'executions_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at']


class InteractiveWorkflowCreateUpdateSerializer(serializers.ModelSerializer):
    steps = InteractiveWorkflowStepSerializer(many=True, required=False)
    
    class Meta:
        model = InteractiveWorkflow
        fields = ['name', 'description', 'form_id', 'status', 'trigger_type', 'trigger_config', 'is_active', 'steps']
    
    def create(self, validated_data):
        steps_data = validated_data.pop('steps', [])
        workflow = InteractiveWorkflow.objects.create(**validated_data)
        
        for step_data in steps_data:
            InteractiveWorkflowStep.objects.create(workflow=workflow, **step_data)
        
        return workflow
    
    def update(self, instance, validated_data):
        steps_data = validated_data.pop('steps', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if steps_data is not None:
            instance.steps.all().delete()
            for step_data in steps_data:
                InteractiveWorkflowStep.objects.create(workflow=instance, **step_data)
        
        return instance


# ==================== VOICE SERIALIZERS ====================

class VoiceTranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceTranscription
        fields = ['id', 'form_id', 'field_id', 'audio_file', 'text', 'confidence', 
                  'language', 'duration', 'created_at']
        read_only_fields = ['id', 'created_at']


class VoiceCommandSerializer(serializers.ModelSerializer):
    transcription = VoiceTranscriptionSerializer(read_only=True)
    
    class Meta:
        model = VoiceCommand
        fields = ['id', 'form_id', 'command_type', 'parameters', 'executed', 'result',
                  'error', 'created_at', 'transcription']
        read_only_fields = ['id', 'executed', 'result', 'error', 'created_at']


# ==================== CHATBOT SERIALIZERS ====================

class ChatSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSuggestion
        fields = ['id', 'text', 'icon', 'action']
        read_only_fields = ['id']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'content', 'metadata', 'rating', 'feedback', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    suggestions = ChatSuggestionSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'form_id', 'title', 'is_active', 'created_at', 'updated_at',
                  'messages', 'suggestions', 'message_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last = obj.messages.last()
        return ChatMessageSerializer(last).data if last else None


# ==================== SUBMISSION SERIALIZERS ====================

class SubmissionFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionField
        fields = ['id', 'field_id', 'field_label', 'value']
        read_only_fields = ['id']


class FormSubmissionSerializer(serializers.ModelSerializer):
    fields = SubmissionFieldSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = FormSubmission
        fields = ['id', 'form_id', 'user_name', 'status', 'data', 'ip_address',
                  'user_agent', 'referrer', 'completion_time', 'created_at', 'submitted_at', 'fields']
        read_only_fields = ['id', 'created_at', 'submitted_at', 'ip_address', 'user_agent']


class FormSubmissionCreateSerializer(serializers.ModelSerializer):
    fields = SubmissionFieldSerializer(many=True, required=False)
    
    class Meta:
        model = FormSubmission
        fields = ['form_id', 'data', 'completion_time', 'fields']
    
    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        submission = FormSubmission.objects.create(**validated_data)
        
        for field_data in fields_data:
            SubmissionField.objects.create(submission=submission, **field_data)
        
        return submission


# ==================== AR/VR SERIALIZERS ====================

class ARAssetSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = ARAsset
        fields = ['id', 'name', 'description', 'asset_type', 'file', 'thumbnail', 'form_id',
                  'owner_name', 'metadata', 'is_public', 'created_at', 'updated_at', 'file_size']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_file_size(self, obj):
        if obj.file:
            return obj.file.size
        return 0


class ARPreviewSerializer(serializers.ModelSerializer):
    asset_detail = ARAssetSerializer(source='asset', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = ARPreview
        fields = ['id', 'form_id', 'asset_detail', 'rotation', 'scale', 'position',
                  'started_at', 'ended_at', 'duration']
        read_only_fields = ['id', 'started_at', 'ended_at']
    
    def get_duration(self, obj):
        if obj.ended_at and obj.started_at:
            return int((obj.ended_at - obj.started_at).total_seconds())
        return None


# ==================== GESTURE SERIALIZERS ====================

class GestureSettingsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = GestureSettings
        fields = ['id', 'user_name', 'enabled', 'sensitivity', 'gestures', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GestureEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GestureEvent
        fields = ['id', 'form_id', 'gesture_type', 'direction', 'coordinates', 'action_triggered', 'created_at']
        read_only_fields = ['id', 'created_at']
