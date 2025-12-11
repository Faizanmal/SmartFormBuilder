"""
API Views for 8 new advanced features
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

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

from .serializers_advanced_new import *
from .services import (
    i18n_service, integration_marketplace_service, scheduling_service,
    theme_service, security_service, realtime_service
)


# ===== Internationalization Views =====

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for languages"""
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]


class FormTranslationViewSet(viewsets.ModelViewSet):
    """ViewSet for form translations"""
    serializer_class = FormTranslationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormTranslation.objects.filter(form__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def auto_translate(self, request):
        """Auto-translate a form to a target language"""
        form_id = request.data.get('form_id')
        target_language = request.data.get('target_language')
        
        service = i18n_service.I18nService()
        result = service.translate_form(form_id, target_language)
        
        return Response(result)


class SubmissionTranslationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for submission translations"""
    serializer_class = SubmissionTranslationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SubmissionTranslation.objects.filter(
            submission__form__user=self.request.user
        )


# ===== Integration Marketplace Views =====

class IntegrationProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for integration providers"""
    serializer_class = IntegrationProviderSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = IntegrationProvider.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by('-popularity_score')


class IntegrationConnectionViewSet(viewsets.ModelViewSet):
    """ViewSet for integration connections"""
    serializer_class = IntegrationConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return IntegrationConnection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test an integration connection"""
        connection = self.get_object()
        service = integration_marketplace_service.IntegrationMarketplaceService()
        
        # Test based on provider
        if connection.provider.slug == 'salesforce':
            result = service.sync_to_salesforce(
                connection_id=connection.id,
                submission_id=None,  # Test connection only
                test=True
            )
        elif connection.provider.slug == 'hubspot':
            result = service.sync_to_hubspot(
                connection_id=connection.id,
                submission_id=None,
                test=True
            )
        else:
            result = {'success': False, 'error': 'Test not implemented for this provider'}
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh OAuth token"""
        connection = self.get_object()
        service = integration_marketplace_service.IntegrationMarketplaceService()
        result = service.refresh_oauth_token(connection.id)
        return Response(result)


class IntegrationWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for integration workflows"""
    serializer_class = IntegrationWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return IntegrationWorkflow.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a workflow"""
        workflow = self.get_object()
        submission_id = request.data.get('submission_id')
        
        service = integration_marketplace_service.IntegrationMarketplaceService()
        result = service.execute_workflow(workflow.id, submission_id)
        
        return Response(result)


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """ViewSet for webhook endpoints"""
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WebhookEndpoint.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a webhook"""
        webhook = self.get_object()
        test_data = request.data.get('test_data', {'test': True})
        
        service = integration_marketplace_service.IntegrationMarketplaceService()
        result = service.execute_webhook(webhook.id, test_data)
        
        return Response(result)


class WebhookLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for webhook logs"""
    serializer_class = WebhookLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WebhookLog.objects.filter(
            webhook__user=self.request.user
        ).order_by('-created_at')


class IntegrationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for integration templates"""
    serializer_class = IntegrationTemplateSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return IntegrationTemplate.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Use a template to create a workflow"""
        template = self.get_object()
        form_id = request.data.get('form_id')
        
        workflow = IntegrationWorkflow.objects.create(
            user=request.user,
            form_id=form_id,
            provider=template.provider,
            name=template.name,
            trigger=template.configuration.get('trigger'),
            actions=template.configuration.get('actions'),
            field_mapping=template.configuration.get('field_mapping'),
            is_active=True
        )
        
        template.usage_count += 1
        template.save()
        
        return Response(IntegrationWorkflowSerializer(workflow).data)


# ===== Scheduling Views =====

class FormScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for form schedules"""
    serializer_class = FormScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormSchedule.objects.filter(form__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate_now(self, request, pk=None):
        """Manually activate a scheduled form"""
        schedule = self.get_object()
        service = scheduling_service.SchedulingService()
        result = service.activate_form(schedule.form.id)
        return Response(result)


class RecurringFormViewSet(viewsets.ModelViewSet):
    """ViewSet for recurring forms"""
    serializer_class = RecurringFormSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RecurringForm.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FormLifecycleEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for lifecycle events"""
    serializer_class = FormLifecycleEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormLifecycleEvent.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')


# ===== Theme Views =====

class ThemeViewSet(viewsets.ModelViewSet):
    """ViewSet for themes"""
    serializer_class = ThemeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Theme.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            )
        return Theme.objects.filter(is_public=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate theme configuration"""
        theme = self.get_object()
        service = theme_service.ThemeService()
        result = service.validate_theme(theme.colors, theme.typography, theme.custom_css)
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone a theme"""
        theme = self.get_object()
        new_theme = Theme.objects.create(
            user=request.user,
            name=f"{theme.name} (Copy)",
            description=theme.description,
            colors=theme.colors,
            typography=theme.typography,
            spacing=theme.spacing,
            borders=theme.borders,
            shadows=theme.shadows,
            custom_css=theme.custom_css,
            is_public=False
        )
        return Response(ThemeSerializer(new_theme).data)


class FormThemeViewSet(viewsets.ModelViewSet):
    """ViewSet for form themes"""
    serializer_class = FormThemeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormTheme.objects.filter(form__user=self.request.user)


class ThemeRatingViewSet(viewsets.ModelViewSet):
    """ViewSet for theme ratings"""
    serializer_class = ThemeRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ThemeRating.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BrandGuidelineViewSet(viewsets.ModelViewSet):
    """ViewSet for brand guidelines"""
    serializer_class = BrandGuidelineSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BrandGuideline.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ===== Security Views =====

class TwoFactorAuthViewSet(viewsets.ModelViewSet):
    """ViewSet for 2FA"""
    serializer_class = TwoFactorAuthSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TwoFactorAuth.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        service = security_service.SecurityService()
        result = service.setup_2fa(self.request.user.id, 'totp')
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify 2FA code"""
        auth = self.get_object()
        code = request.data.get('code')
        service = security_service.SecurityService()
        result = service.verify_2fa_code(auth.id, code)
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable 2FA"""
        auth = self.get_object()
        service = security_service.SecurityService()
        result = service.disable_2fa(auth.user.id)
        return Response(result)


class SSOProviderViewSet(viewsets.ModelViewSet):
    """ViewSet for SSO providers"""
    serializer_class = SSOProviderSerializer
    permission_classes = [permissions.IsAdminUser]
    
    queryset = SSOProvider.objects.all()


class DataPrivacyRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for data privacy requests"""
    serializer_class = DataPrivacyRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DataPrivacyRequest.objects.all()
        return DataPrivacyRequest.objects.filter(email=self.request.user.email)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify email for privacy request"""
        privacy_request = self.get_object()
        token = request.data.get('token')
        
        if privacy_request.verification_token == token:
            privacy_request.verified_at = timezone.now()
            privacy_request.save()
            return Response({'success': True, 'message': 'Email verified'})
        
        return Response(
            {'success': False, 'error': 'Invalid verification token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a privacy request (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        privacy_request = self.get_object()
        service = security_service.SecurityService()
        
        if privacy_request.request_type == 'export':
            result = service.export_user_data(privacy_request.email)
        elif privacy_request.request_type == 'delete':
            result = service.delete_user_data(privacy_request.email)
        else:
            result = {'success': False, 'error': 'Unknown request type'}
        
        if result['success']:
            privacy_request.status = 'completed'
            privacy_request.processed_by = request.user
            privacy_request.processed_at = timezone.now()
            privacy_request.save()
        
        return Response(result)


class ConsentTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for consent tracking"""
    serializer_class = ConsentTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConsentTracking.objects.filter(
            submission__form__user=self.request.user
        )


class SecurityAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for security audit logs"""
    serializer_class = SecurityAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return SecurityAuditLog.objects.all().order_by('-created_at')
        return SecurityAuditLog.objects.filter(user=self.request.user).order_by('-created_at')


class IPAccessControlViewSet(viewsets.ModelViewSet):
    """ViewSet for IP access control"""
    serializer_class = IPAccessControlSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return IPAccessControl.objects.filter(form__user=self.request.user)


# ===== Collaboration Views =====

class FormCollaboratorViewSet(viewsets.ModelViewSet):
    """ViewSet for form collaborators"""
    serializer_class = FormCollaboratorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormCollaborator.objects.filter(
            Q(form__user=self.request.user) | Q(user=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept collaboration invitation"""
        collaborator = self.get_object()
        if collaborator.user == request.user:
            collaborator.invitation_accepted = True
            collaborator.save()
            return Response({'success': True, 'message': 'Invitation accepted'})
        return Response(
            {'error': 'Unauthorized'},
            status=status.HTTP_403_FORBIDDEN
        )


class FormEditSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for edit sessions"""
    serializer_class = FormEditSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormEditSession.objects.filter(
            form__user=self.request.user,
            is_active=True
        )


class FormChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for form changes"""
    serializer_class = FormChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormChange.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')


class FormCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for form comments"""
    serializer_class = FormCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormComment.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a comment"""
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()
        return Response({'success': True, 'message': 'Comment resolved'})


class FormReviewWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for review workflows"""
    serializer_class = FormReviewWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormReviewWorkflow.objects.filter(
            Q(form__user=self.request.user) | Q(reviewers=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user, submitted_at=timezone.now())


class FormReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for form reviews"""
    serializer_class = FormReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormReview.objects.filter(reviewer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user, reviewed_at=timezone.now())


# ===== Predictive Views =====

class FieldPredictionViewSet(viewsets.ModelViewSet):
    """ViewSet for field predictions"""
    serializer_class = FieldPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FieldPrediction.objects.filter(form__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """Get prediction for a field"""
        form_id = request.data.get('form_id')
        field_name = request.data.get('field_name')
        user_context = request.data.get('user_context', {})
        
        service = realtime_service.PredictiveService()
        result = service.predict_field_value(form_id, field_name, user_context)
        
        return Response(result)


class SmartDefaultViewSet(viewsets.ModelViewSet):
    """ViewSet for smart defaults"""
    serializer_class = SmartDefaultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SmartDefault.objects.filter(form__user=self.request.user)


class CompletionPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for completion predictions"""
    serializer_class = CompletionPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CompletionPrediction.objects.filter(
            submission__form__user=self.request.user
        )


class ProgressiveDisclosureViewSet(viewsets.ModelViewSet):
    """ViewSet for progressive disclosure"""
    serializer_class = ProgressiveDisclosureSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProgressiveDisclosure.objects.filter(form__user=self.request.user)


# ===== Mobile Views =====

class MobileOptimizationViewSet(viewsets.ModelViewSet):
    """ViewSet for mobile optimization"""
    serializer_class = MobileOptimizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MobileOptimization.objects.filter(form__user=self.request.user)


class GeolocationFieldViewSet(viewsets.ModelViewSet):
    """ViewSet for geolocation fields"""
    serializer_class = GeolocationFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return GeolocationField.objects.filter(submission__form__user=self.request.user)


class OfflineSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for offline submissions"""
    serializer_class = OfflineSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OfflineSubmission.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync an offline submission"""
        offline_submission = self.get_object()
        service = realtime_service.MobileService()
        result = service.sync_offline_submission(offline_submission.id)
        return Response(result)


class PushNotificationSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for push notification subscriptions"""
    serializer_class = PushNotificationSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PushNotificationSubscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FormNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for form notifications"""
    serializer_class = FormNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormNotification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """Send a push notification"""
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        body = request.data.get('body')
        data = request.data.get('data', {})
        
        service = realtime_service.MobileService()
        result = service.send_push_notification(user_id, title, body, data)
        
        return Response(result)
