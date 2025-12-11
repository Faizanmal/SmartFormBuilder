"""
Serializers for 8 new advanced features:
1. Multi-language/i18n
2. Integration Marketplace
3. Form Scheduling
4. Custom Themes
5. Advanced Security
6. Real-time Collaboration
7. Predictive Analytics
8. Mobile Optimization
"""
from rest_framework import serializers
from .models_i18n import Language, FormTranslation, SubmissionTranslation
from .models_integrations_marketplace import (
    IntegrationProvider, IntegrationConnection, IntegrationWorkflow,
    WebhookEndpoint, WebhookLog, IntegrationTemplate
)
from .models_scheduling import FormSchedule, RecurringForm, FormLifecycleEvent
from .models_themes import Theme, FormTheme, ThemeRating, BrandGuideline
from .models_security import (
    TwoFactorAuth, SSOProvider, DataPrivacyRequest, ConsentTracking,
    SecurityAuditLog, IPAccessControl
)
from .models_collaboration import (
    FormCollaborator, FormEditSession, FormChange, FormComment,
    FormReviewWorkflow, FormReview
)
from .models_predictive import (
    FieldPrediction, SmartDefault, CompletionPrediction, ProgressiveDisclosure
)
from .models_mobile import (
    MobileOptimization, GeolocationField, OfflineSubmission,
    PushNotificationSubscription, FormNotification
)


# ===== Internationalization Serializers =====

class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for languages"""
    
    class Meta:
        model = Language
        fields = '__all__'


class FormTranslationSerializer(serializers.ModelSerializer):
    """Serializer for form translations"""
    
    language_code = serializers.CharField(source='language.code', read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    
    class Meta:
        model = FormTranslation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SubmissionTranslationSerializer(serializers.ModelSerializer):
    """Serializer for submission translations"""
    
    class Meta:
        model = SubmissionTranslation
        fields = '__all__'


# ===== Integration Marketplace Serializers =====

class IntegrationProviderSerializer(serializers.ModelSerializer):
    """Serializer for integration providers"""
    
    class Meta:
        model = IntegrationProvider
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'popularity_score']


class IntegrationConnectionSerializer(serializers.ModelSerializer):
    """Serializer for integration connections"""
    
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_logo = serializers.URLField(source='provider.logo_url', read_only=True)
    
    class Meta:
        model = IntegrationConnection
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at', 'error_count', 'last_error']
        extra_kwargs = {'credentials': {'write_only': True}}


class IntegrationWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for integration workflows"""
    
    class Meta:
        model = IntegrationWorkflow
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at', 'execution_count', 
                           'success_count', 'failure_count', 'last_executed_at']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for webhook endpoints"""
    
    class Meta:
        model = WebhookEndpoint
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at', 'success_count', 
                           'failure_count', 'last_triggered_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    """Serializer for webhook logs"""
    
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    
    class Meta:
        model = WebhookLog
        fields = '__all__'
        read_only_fields = ['created_at']


class IntegrationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for integration templates"""
    
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = IntegrationTemplate
        fields = '__all__'
        read_only_fields = ['usage_count', 'created_at', 'updated_at']


# ===== Scheduling Serializers =====

class FormScheduleSerializer(serializers.ModelSerializer):
    """Serializer for form schedules"""
    
    class Meta:
        model = FormSchedule
        fields = '__all__'
        read_only_fields = ['status', 'activated_at', 'expired_at', 'created_at', 'updated_at']


class RecurringFormSerializer(serializers.ModelSerializer):
    """Serializer for recurring forms"""
    
    template_form_title = serializers.CharField(source='template_form.title', read_only=True)
    
    class Meta:
        model = RecurringForm
        fields = '__all__'
        read_only_fields = ['user', 'last_created_at', 'next_creation_at', 
                           'forms_created_count', 'created_at', 'updated_at']


class FormLifecycleEventSerializer(serializers.ModelSerializer):
    """Serializer for lifecycle events"""
    
    triggered_by_email = serializers.EmailField(source='triggered_by.email', read_only=True)
    
    class Meta:
        model = FormLifecycleEvent
        fields = '__all__'
        read_only_fields = ['created_at']


# ===== Theme Serializers =====

class ThemeSerializer(serializers.ModelSerializer):
    """Serializer for themes"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Theme
        fields = '__all__'
        read_only_fields = ['user', 'downloads_count', 'rating_average', 
                           'rating_count', 'created_at', 'updated_at']


class FormThemeSerializer(serializers.ModelSerializer):
    """Serializer for form themes"""
    
    theme_name = serializers.CharField(source='theme.name', read_only=True)
    compiled_theme = serializers.SerializerMethodField()
    
    class Meta:
        model = FormTheme
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_compiled_theme(self, obj):
        from .services.theme_service import ThemeService
        service = ThemeService()
        result = service.get_compiled_theme(str(obj.form.id))
        return result.get('theme') if result.get('success') else None


class ThemeRatingSerializer(serializers.ModelSerializer):
    """Serializer for theme ratings"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ThemeRating
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class BrandGuidelineSerializer(serializers.ModelSerializer):
    """Serializer for brand guidelines"""
    
    class Meta:
        model = BrandGuideline
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


# ===== Security Serializers =====

class TwoFactorAuthSerializer(serializers.ModelSerializer):
    """Serializer for 2FA"""
    
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TwoFactorAuth
        fields = '__all__'
        read_only_fields = ['user', 'secret_key', 'backup_codes', 'verified_at', 
                           'created_at', 'updated_at']
        extra_kwargs = {'secret_key': {'write_only': True}}
    
    def get_qr_code_url(self, obj):
        if obj.method == 'totp' and obj.secret_key:
            import pyotp
            totp = pyotp.TOTP(obj.secret_key)
            return totp.provisioning_uri(
                name=obj.user.email,
                issuer_name='SmartFormBuilder'
            )
        return None


class SSOProviderSerializer(serializers.ModelSerializer):
    """Serializer for SSO providers"""
    
    class Meta:
        model = SSOProvider
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {'client_secret': {'write_only': True}}


class DataPrivacyRequestSerializer(serializers.ModelSerializer):
    """Serializer for data privacy requests"""
    
    class Meta:
        model = DataPrivacyRequest
        fields = '__all__'
        read_only_fields = ['verification_token', 'verified_at', 'processed_by', 
                           'processed_at', 'export_file_url', 'export_expires_at', 
                           'created_at', 'updated_at']


class ConsentTrackingSerializer(serializers.ModelSerializer):
    """Serializer for consent tracking"""
    
    class Meta:
        model = ConsentTracking
        fields = '__all__'
        read_only_fields = ['created_at', 'revoked_at']


class SecurityAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for security audit logs"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SecurityAuditLog
        fields = '__all__'
        read_only_fields = ['created_at']


class IPAccessControlSerializer(serializers.ModelSerializer):
    """Serializer for IP access control"""
    
    class Meta:
        model = IPAccessControl
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# ===== Collaboration Serializers =====

class FormCollaboratorSerializer(serializers.ModelSerializer):
    """Serializer for form collaborators"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    
    class Meta:
        model = FormCollaborator
        fields = '__all__'
        read_only_fields = ['invited_by', 'invitation_accepted', 'last_active_at', 'created_at']


class FormEditSessionSerializer(serializers.ModelSerializer):
    """Serializer for edit sessions"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FormEditSession
        fields = '__all__'
        read_only_fields = ['user', 'started_at', 'last_activity_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class FormChangeSerializer(serializers.ModelSerializer):
    """Serializer for form changes"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = FormChange
        fields = '__all__'
        read_only_fields = ['user', 'session', 'created_at']


class FormCommentSerializer(serializers.ModelSerializer):
    """Serializer for form comments"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    resolved_by_email = serializers.EmailField(source='resolved_by.email', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = FormComment
        fields = '__all__'
        read_only_fields = ['user', 'resolved_by', 'resolved_at', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email
    
    def get_replies(self, obj):
        if obj.parent_comment is None:
            replies = FormComment.objects.filter(parent_comment=obj)
            return FormCommentSerializer(replies, many=True).data
        return []


class FormReviewSerializer(serializers.ModelSerializer):
    """Serializer for form reviews"""
    
    reviewer_email = serializers.EmailField(source='reviewer.email', read_only=True)
    
    class Meta:
        model = FormReview
        fields = '__all__'
        read_only_fields = ['workflow', 'reviewer', 'reviewed_at', 'created_at']


class FormReviewWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for review workflows"""
    
    submitted_by_email = serializers.EmailField(source='submitted_by.email', read_only=True)
    reviews = FormReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = FormReviewWorkflow
        fields = '__all__'
        read_only_fields = ['submitted_by', 'submitted_at', 'current_approvals', 
                           'created_at', 'updated_at']


# ===== Predictive Serializers =====

class FieldPredictionSerializer(serializers.ModelSerializer):
    """Serializer for field predictions"""
    
    class Meta:
        model = FieldPrediction
        fields = '__all__'
        read_only_fields = ['accuracy_rate', 'usage_count', 'created_at', 'updated_at']


class SmartDefaultSerializer(serializers.ModelSerializer):
    """Serializer for smart defaults"""
    
    class Meta:
        model = SmartDefault
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CompletionPredictionSerializer(serializers.ModelSerializer):
    """Serializer for completion predictions"""
    
    class Meta:
        model = CompletionPrediction
        fields = '__all__'
        read_only_fields = ['created_at']


class ProgressiveDisclosureSerializer(serializers.ModelSerializer):
    """Serializer for progressive disclosure"""
    
    class Meta:
        model = ProgressiveDisclosure
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# ===== Mobile Serializers =====

class MobileOptimizationSerializer(serializers.ModelSerializer):
    """Serializer for mobile optimization settings"""
    
    class Meta:
        model = MobileOptimization
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class GeolocationFieldSerializer(serializers.ModelSerializer):
    """Serializer for geolocation fields"""
    
    class Meta:
        model = GeolocationField
        fields = '__all__'
        read_only_fields = ['created_at']


class OfflineSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for offline submissions"""
    
    class Meta:
        model = OfflineSubmission
        fields = '__all__'
        read_only_fields = ['status', 'sync_attempts', 'last_sync_attempt', 
                           'synced_submission_id', 'synced_at']


class PushNotificationSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for push notification subscriptions"""
    
    class Meta:
        model = PushNotificationSubscription
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class FormNotificationSerializer(serializers.ModelSerializer):
    """Serializer for form notifications"""
    
    class Meta:
        model = FormNotification
        fields = '__all__'
        read_only_fields = ['sent_at', 'delivered_at', 'clicked_at', 'created_at']
