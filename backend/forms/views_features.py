"""
Views for Advanced Features Dashboard:
- Performance Optimization Dashboard
- Advanced Analytics & User Behavior
- Enhanced Accessibility & Compliance
- Mobile-First Improvements
- Real-Time Collaboration
- AI-Powered Optimization
- Advanced Data Quality
- Offline Form Building & Sync
- Smart Form Recovery & Auto-Save
- Integration Marketplace
"""
from rest_framework import viewsets, permissions, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Avg, Sum, Q
from django.shortcuts import get_object_or_404
from datetime import timedelta
import logging

from forms.models import Form, Submission
from forms.models_performance import (
    PerformanceMetric, FieldCompletionMetric, FormCacheConfig,
    PerformanceAlert, AssetOptimization
)
from forms.models_analytics import (
    SessionRecording, DropOffAnalysis, ABTestResult, BehaviorInsight,
    FormFunnel, FunnelStepMetric
)
from forms.models_accessibility import (
    AccessibilityConfig, AccessibilityAudit, AccessibilityIssue,
    UserAccessibilityPreference, ComplianceReport
)
from forms.models_mobile import (
    MobileOptimization
)
from forms.models_collaboration import (
    FormCollaborator, FormEditSession, FormChange,
    FormComment
)
from forms.models_autosave import (
    FormBuilderAutoSave, FormBuilderCrashRecovery
)
from forms.models_data_quality import (
    ExternalValidation, DataCleansingRule
)
from forms.models_predictive import (
    SmartDefault, CompletionPrediction, ProgressiveDisclosure
)
from forms.models_integrations_marketplace import (
    IntegrationTemplate
)
from forms.services.performance_service import PerformanceService
from forms.services.advanced_analytics_service import (
    HeatmapService, SessionRecordingService, DropOffAnalysisService
)
from forms.services.ab_testing_service import ABTestingService
from forms.services.accessibility_service import AccessibilityService
from forms.services.data_quality_service import DataQualityService
from forms.services.optimization_service import FormOptimizationService
from .serializers_features import *

logger = logging.getLogger(__name__)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================
# 1. PERFORMANCE OPTIMIZATION DASHBOARD
# ============================================================

class PerformanceMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for performance metrics"""
    serializer_class = PerformanceMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return PerformanceMetric.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def record(self, request):
        """Record a new performance metric"""
        form_id = request.data.get('form_id')
        metric_type = request.data.get('metric_type')
        value = request.data.get('value')
        metadata = request.data.get('metadata', {})
        
        metric = PerformanceService.record_metric(
            form_id=form_id,
            metric_type=metric_type,
            value=value,
            metadata=metadata
        )
        
        return Response({
            'success': True,
            'metric_id': str(metric.id)
        })


class PerformanceDashboardView(views.APIView):
    """Get comprehensive performance dashboard data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, form_id):
        """Get performance dashboard for a form"""
        form = get_object_or_404(Form, id=form_id, user=request.user)
        days = int(request.query_params.get('days', 30))
        
        dashboard_data = PerformanceService.get_performance_dashboard(
            form_id=str(form.id),
            days=days
        )
        
        return Response(dashboard_data)


class FieldCompletionMetricViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for field completion metrics"""
    serializer_class = FieldCompletionMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FieldCompletionMetric.objects.filter(
            form__user=self.request.user
        ).order_by('-date')
    
    @action(detail=False, methods=['get'])
    def by_form(self, request):
        """Get field metrics for a specific form"""
        form_id = request.query_params.get('form_id')
        if not form_id:
            return Response({'error': 'form_id required'}, status=400)
        
        metrics = self.get_queryset().filter(form_id=form_id)
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)


class FormCacheConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for form cache configuration"""
    serializer_class = FormCacheConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormCacheConfig.objects.filter(form__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def invalidate(self, request, pk=None):
        """Invalidate cache for a form"""
        config = self.get_object()
        CacheService.invalidate_form_cache(str(config.form.id))
        return Response({'success': True, 'message': 'Cache invalidated'})
    
    @action(detail=True, methods=['post'])
    def warm(self, request, pk=None):
        """Pre-warm cache for a form"""
        config = self.get_object()
        CacheService.warm_form_cache(str(config.form.id))
        return Response({'success': True, 'message': 'Cache warmed'})


class PerformanceAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for performance alerts"""
    serializer_class = PerformanceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PerformanceAlert.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save()
        return Response({'success': True})
    
    @action(detail=False, methods=['get'])
    def unacknowledged(self, request):
        """Get unacknowledged alerts"""
        alerts = self.get_queryset().filter(acknowledged=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


class AssetOptimizationViewSet(viewsets.ModelViewSet):
    """ViewSet for asset optimization records"""
    serializer_class = AssetOptimizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AssetOptimization.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def optimize_assets(self, request):
        """Trigger asset optimization for a form"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        result = PerformanceService.optimize_form_assets(str(form.id))
        return Response(result)


class LazyLoadingConfigView(views.APIView):
    """Configure lazy loading for forms"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, form_id):
        """Get lazy loading config for a form"""
        form = get_object_or_404(Form, id=form_id, user=request.user)
        config = PerformanceService.get_lazy_loading_config(str(form.id))
        return Response(config)
    
    def post(self, request, form_id):
        """Update lazy loading config"""
        form = get_object_or_404(Form, id=form_id, user=request.user)
        config = PerformanceService.update_lazy_loading_config(
            str(form.id),
            request.data
        )
        return Response(config)


# ============================================================
# 2. ADVANCED ANALYTICS & USER BEHAVIOR
# ============================================================

class HeatmapViewSet(viewsets.ViewSet):
    """ViewSet for heatmap data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get heatmap data for a form"""
        form_id = request.query_params.get('form_id')
        if not form_id:
            return Response({'error': 'form_id required'}, status=400)
        
        interaction_type = request.query_params.get('interaction_type')
        device_type = request.query_params.get('device_type')
        days = int(request.query_params.get('days', 30))
        
        data = HeatmapService.get_heatmap_data(
            form_id=form_id,
            interaction_type=interaction_type,
            device_type=device_type,
            days=days
        )
        
        return Response(data)
    
    def create(self, request):
        """Record heatmap interaction"""
        form_id = request.data.get('form_id')
        interaction_data = {
            'type': request.data.get('type'),
            'x': request.data.get('x'),
            'y': request.data.get('y'),
            'field_id': request.data.get('field_id', ''),
            'device_type': request.data.get('device_type', 'desktop'),
            'duration': request.data.get('duration', 0)
        }
        
        HeatmapService.record_interaction(form_id, interaction_data)
        return Response({'success': True}, status=201)


class SessionRecordingViewSet(viewsets.ModelViewSet):
    """ViewSet for session recordings"""
    serializer_class = SessionRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return SessionRecording.objects.filter(
            form__user=self.request.user
        ).order_by('-started_at')
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new session recording"""
        form_id = request.data.get('form_id')
        session_data = {
            'session_id': request.data.get('session_id'),
            'device_type': request.data.get('device_type', 'desktop'),
            'browser': request.data.get('browser', ''),
            'os': request.data.get('os', ''),
            'screen_width': request.data.get('screen_width', 0),
            'screen_height': request.data.get('screen_height', 0),
        }
        
        recording = SessionRecordingService.start_recording(form_id, session_data)
        return Response({
            'success': True,
            'recording_id': str(recording.id)
        }, status=201)
    
    @action(detail=True, methods=['post'])
    def add_event(self, request, pk=None):
        """Add an event to a session recording"""
        recording = self.get_object()
        event_data = request.data.get('event', {})
        
        SessionRecordingService.add_event(str(recording.id), event_data)
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a session recording"""
        recording = self.get_object()
        completed = request.data.get('completed', False)
        drop_off_field = request.data.get('drop_off_field', '')
        
        SessionRecordingService.end_recording(
            str(recording.id),
            completed=completed,
            drop_off_field=drop_off_field
        )
        return Response({'success': True})
    
    @action(detail=True, methods=['get'])
    def playback(self, request, pk=None):
        """Get recording data for playback"""
        recording = self.get_object()
        playback_data = SessionRecordingService.get_playback_data(str(recording.id))
        return Response(playback_data)


class DropOffAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for drop-off analysis"""
    serializer_class = DropOffAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DropOffAnalysis.objects.filter(
            form__user=self.request.user
        ).order_by('-date')
    
    @action(detail=False, methods=['get'])
    def by_form(self, request):
        """Get drop-off analysis for a form"""
        form_id = request.query_params.get('form_id')
        days = int(request.query_params.get('days', 30))
        
        if not form_id:
            return Response({'error': 'form_id required'}, status=400)
        
        analysis = DropOffAnalysisService.get_form_analysis(form_id, days)
        return Response(analysis)
    
    @action(detail=False, methods=['get'])
    def field_insights(self, request):
        """Get field-level drop-off insights"""
        form_id = request.query_params.get('form_id')
        
        if not form_id:
            return Response({'error': 'form_id required'}, status=400)
        
        insights = DropOffAnalysisService.get_field_level_insights(form_id)
        return Response(insights)


class ABTestResultViewSet(viewsets.ModelViewSet):
    """ViewSet for A/B test results"""
    serializer_class = ABTestResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ABTestResult.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def statistical_significance(self, request, pk=None):
        """Get statistical significance for an A/B test"""
        result = self.get_object()
        significance = ABTestingService.calculate_significance(str(result.id))
        return Response(significance)


class BehaviorInsightViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for behavior insights"""
    serializer_class = BehaviorInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BehaviorInsight.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate behavior insights for a form"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        insights = DropOffAnalysisService.generate_insights(str(form.id))
        return Response(insights)


class FormFunnelViewSet(viewsets.ModelViewSet):
    """ViewSet for form funnels"""
    serializer_class = FormFunnelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormFunnel.objects.filter(
            form__user=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Get funnel metrics"""
        funnel = self.get_object()
        days = int(request.query_params.get('days', 30))
        
        metrics = FunnelStepMetric.objects.filter(
            funnel=funnel,
            date__gte=timezone.now().date() - timedelta(days=days)
        ).values('step_name').annotate(
            total_entered=Sum('entered_count'),
            total_completed=Sum('completed_count'),
            avg_time=Avg('avg_time_seconds')
        )
        
        return Response(list(metrics))


# ============================================================
# 3. ENHANCED ACCESSIBILITY & COMPLIANCE
# ============================================================

class AccessibilityConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for accessibility configuration"""
    serializer_class = AccessibilityConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AccessibilityConfig.objects.filter(form__user=self.request.user)


class AccessibilityAuditViewSet(viewsets.ModelViewSet):
    """ViewSet for accessibility audits"""
    serializer_class = AccessibilityAuditSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AccessibilityAudit.objects.filter(
            form__user=self.request.user
        ).order_by('-started_at')
    
    @action(detail=False, methods=['post'])
    def run_audit(self, request):
        """Run an accessibility audit on a form"""
        form_id = request.data.get('form_id')
        wcag_level = request.data.get('wcag_level', 'AA')
        
        form = get_object_or_404(Form, id=form_id, user=request.user)
        audit = AccessibilityService.run_accessibility_audit(
            form_id=str(form.id),
            wcag_level=wcag_level
        )
        
        if audit:
            serializer = self.get_serializer(audit)
            return Response(serializer.data, status=201)
        return Response({'error': 'Audit failed'}, status=400)
    
    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        """Get issues for an audit"""
        audit = self.get_object()
        issues = AccessibilityIssue.objects.filter(audit=audit)
        serializer = AccessibilityIssueSerializer(issues, many=True)
        return Response(serializer.data)


class AccessibilityIssueViewSet(viewsets.ModelViewSet):
    """ViewSet for accessibility issues"""
    serializer_class = AccessibilityIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AccessibilityIssue.objects.filter(
            audit__form__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def fix(self, request, pk=None):
        """Mark an issue as fixed and apply auto-fix if available"""
        issue = self.get_object()
        auto_fix = request.data.get('auto_fix', False)
        
        if auto_fix and issue.auto_fix_available:
            result = AccessibilityService.apply_auto_fix(str(issue.id))
            return Response(result)
        
        issue.status = 'fixed'
        issue.fixed_at = timezone.now()
        issue.save()
        return Response({'success': True})


class UserAccessibilityPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for user accessibility preferences"""
    serializer_class = UserAccessibilityPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserAccessibilityPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ComplianceReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for compliance reports"""
    serializer_class = ComplianceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ComplianceReport.objects.filter(
            form__user=self.request.user
        ).order_by('-generated_at')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a compliance report"""
        form_id = request.data.get('form_id')
        standards = request.data.get('standards', ['WCAG21_AA'])
        
        form = get_object_or_404(Form, id=form_id, user=request.user)
        report = AccessibilityService.generate_compliance_report(
            form_id=str(form.id),
            standards=standards
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=201)


# ============================================================
# 4. MOBILE-FIRST INTERACTION IMPROVEMENTS
# (Already in views_advanced_new.py, adding additional endpoints)
# ============================================================

class VoiceInputView(views.APIView):
    """Handle voice input for mobile devices"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Process voice input and convert to text"""
        audio_data = request.FILES.get('audio')
        form_id = request.data.get('form_id')
        field_id = request.data.get('field_id')
        language = request.data.get('language', 'en-US')
        
        if not audio_data:
            return Response({'error': 'No audio data provided'}, status=400)
        
        # Process voice input using speech-to-text service
        from forms.services.voice_service import VoiceService
        result = VoiceService.transcribe_audio(
            audio_data=audio_data.read(),
            language=language
        )
        
        return Response(result)


class GeolocationCaptureView(views.APIView):
    """Capture and validate GPS location for address fields"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Capture and reverse geocode a location"""
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        accuracy = request.data.get('accuracy', 0)
        
        if latitude is None or longitude is None:
            return Response({'error': 'Latitude and longitude required'}, status=400)
        
        from forms.services.i18n_service import GeocodingService
        address = GeocodingService.reverse_geocode(
            latitude=float(latitude),
            longitude=float(longitude)
        )
        
        return Response({
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
            'address': address
        })


class CameraUploadView(views.APIView):
    """Handle camera-captured images from mobile devices"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Process camera-captured image"""
        image = request.FILES.get('image')
        form_id = request.data.get('form_id')
        field_id = request.data.get('field_id')
        optimize = request.data.get('optimize', True)
        
        if not image:
            return Response({'error': 'No image provided'}, status=400)
        
        from forms.services.performance_service import ImageOptimizationService
        
        if optimize:
            result = ImageOptimizationService.optimize_image(
                image_data=image.read(),
                max_width=1920,
                max_height=1080,
                quality=85
            )
        else:
            result = {
                'success': True,
                'url': f'/media/uploads/{form_id}/{field_id}/{image.name}'
            }
        
        return Response(result)


class SwipeGestureConfigView(views.APIView):
    """Configure swipe gestures for multi-step forms"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, form_id):
        """Get swipe gesture config"""
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        try:
            mobile_config = MobileOptimization.objects.get(form=form)
            return Response({
                'swipe_enabled': mobile_config.swipe_gestures_enabled,
                'swipe_sensitivity': mobile_config.swipe_sensitivity if hasattr(mobile_config, 'swipe_sensitivity') else 'medium',
                'haptic_feedback': mobile_config.haptic_feedback if hasattr(mobile_config, 'haptic_feedback') else True
            })
        except MobileOptimization.DoesNotExist:
            return Response({
                'swipe_enabled': True,
                'swipe_sensitivity': 'medium',
                'haptic_feedback': True
            })
    
    def post(self, request, form_id):
        """Update swipe gesture config"""
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        config, created = MobileOptimization.objects.get_or_create(form=form)
        config.swipe_gestures_enabled = request.data.get('swipe_enabled', True)
        config.save()
        
        return Response({'success': True})


# ============================================================
# 5. REAL-TIME COLLABORATION TOOLS
# (Already in views_advanced_new.py, adding additional endpoints)
# ============================================================

class LiveEditingView(views.APIView):
    """Handle live co-editing of forms"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, form_id):
        """Get active edit sessions for a form"""
        form = get_object_or_404(Form, id=form_id)
        
        # Check if user has access
        is_owner = form.user == request.user
        is_collaborator = FormCollaborator.objects.filter(
            form=form, user=request.user
        ).exists()
        
        if not is_owner and not is_collaborator:
            return Response({'error': 'Access denied'}, status=403)
        
        sessions = FormEditSession.objects.filter(
            form=form,
            is_active=True
        ).select_related('user')
        
        return Response({
            'active_sessions': [
                {
                    'session_id': str(s.id),
                    'user_email': s.user.email,
                    'user_name': s.user.get_full_name() or s.user.email,
                    'cursor_position': s.cursor_position,
                    'active_field': s.active_field,
                    'started_at': s.started_at.isoformat()
                }
                for s in sessions
            ]
        })
    
    def post(self, request, form_id):
        """Join an editing session"""
        form = get_object_or_404(Form, id=form_id)
        
        # Check permission
        is_owner = form.user == request.user
        collaborator = FormCollaborator.objects.filter(
            form=form, user=request.user
        ).first()
        
        if not is_owner and not collaborator:
            return Response({'error': 'Access denied'}, status=403)
        
        if collaborator and collaborator.role == 'viewer':
            return Response({'error': 'Viewers cannot edit'}, status=403)
        
        session, created = FormEditSession.objects.get_or_create(
            form=form,
            user=request.user,
            is_active=True,
            defaults={
                'session_id': request.data.get('session_id', str(timezone.now().timestamp())),
            }
        )
        
        return Response({
            'session_id': str(session.id),
            'websocket_url': f'/ws/forms/{form_id}/edit/'
        }, status=201 if created else 200)


class FormVersionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for form version history with diff viewing"""
    serializer_class = FormChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        form_id = self.kwargs.get('form_id')
        return FormChange.objects.filter(
            form_id=form_id,
            form__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def diff(self, request, form_id=None):
        """Get diff between two versions"""
        from_version = request.query_params.get('from')
        to_version = request.query_params.get('to')
        
        if not from_version or not to_version:
            return Response({'error': 'from and to version IDs required'}, status=400)
        
        from forms.services.realtime_service import VersionService
        diff = VersionService.compute_diff(from_version, to_version)
        
        return Response(diff)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None, form_id=None):
        """Restore to a specific version"""
        change = self.get_object()
        
        from forms.services.realtime_service import VersionService
        result = VersionService.restore_version(str(change.id))
        
        return Response(result)


class FormCommentEnhancedViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for in-form comments"""
    serializer_class = FormCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormComment.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Reply to a comment"""
        parent = self.get_object()
        
        comment = FormComment.objects.create(
            form=parent.form,
            user=request.user,
            parent=parent,
            comment_type=request.data.get('comment_type', 'feedback'),
            field_id=parent.field_id,
            content=request.data.get('content')
        )
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a comment thread"""
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_at = timezone.now()
        comment.resolved_by = request.user
        comment.save()
        return Response({'success': True})


# ============================================================
# 6. AI-POWERED FORM OPTIMIZATION
# ============================================================

class AIOptimizationViewSet(viewsets.ViewSet):
    """ViewSet for AI-powered form optimization"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def suggest_field_order(self, request):
        """Get AI suggestions for optimal field order"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        suggestions = FormOptimizationService.suggest_field_order(str(form.id))
        return Response(suggestions)
    
    @action(detail=False, methods=['post'])
    def suggest_validations(self, request):
        """Get AI suggestions for field validations"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        suggestions = FormOptimizationService.suggest_validations(str(form.id))
        return Response(suggestions)
    
    @action(detail=False, methods=['post'])
    def predict_conversion(self, request):
        """Predict conversion rate and get improvement suggestions"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        prediction = FormOptimizationService.predict_conversion_rate(str(form.id))
        return Response(prediction)
    
    @action(detail=False, methods=['post'])
    def auto_ab_test(self, request):
        """Auto-create A/B tests for underperforming forms"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        test = FormOptimizationService.create_auto_ab_test(str(form.id))
        return Response(test)
    
    @action(detail=False, methods=['get'])
    def optimization_score(self, request):
        """Get overall optimization score for a form"""
        form_id = request.query_params.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        score = FormOptimizationService.calculate_optimization_score(str(form.id))
        return Response(score)


class SmartDefaultViewSet(viewsets.ModelViewSet):
    """ViewSet for smart defaults"""
    serializer_class = SmartDefaultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SmartDefault.objects.filter(form__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate smart defaults for a form"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        defaults = FormOptimizationService.generate_smart_defaults(str(form.id))
        return Response(defaults)


class CompletionPredictionViewSet(viewsets.ModelViewSet):
    """ViewSet for completion predictions"""
    serializer_class = CompletionPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CompletionPrediction.objects.filter(
            form__user=self.request.user
        ).order_by('-created_at')


class ProgressiveDisclosureViewSet(viewsets.ModelViewSet):
    """ViewSet for progressive disclosure configuration"""
    serializer_class = ProgressiveDisclosureSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProgressiveDisclosure.objects.filter(form__user=self.request.user)


# ============================================================
# 7. ADVANCED DATA QUALITY FEATURES
# ============================================================

class DataQualityRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for data quality rules"""
    serializer_class = DataQualityRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DataQualityRule.objects.filter(form__user=self.request.user)


class SubmissionQualityScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for submission quality scores"""
    serializer_class = SubmissionQualityScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SubmissionQualityScore.objects.filter(
            submission__form__user=self.request.user
        ).order_by('-calculated_at')
    
    @action(detail=False, methods=['get'])
    def form_average(self, request):
        """Get average quality score for a form"""
        form_id = request.query_params.get('form_id')
        if not form_id:
            return Response({'error': 'form_id required'}, status=400)
        
        avg_score = SubmissionQualityScore.objects.filter(
            submission__form_id=form_id
        ).aggregate(avg=Avg('overall_score'))
        
        return Response({'average_score': avg_score['avg'] or 0})


class DuplicateSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for duplicate submissions"""
    serializer_class = DuplicateSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DuplicateSubmission.objects.filter(
            original__form__user=self.request.user
        ).order_by('-detected_at')
    
    @action(detail=False, methods=['post'])
    def detect(self, request):
        """Run duplicate detection for a form"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        duplicates = DataQualityService.detect_duplicates(str(form.id))
        return Response({
            'duplicates_found': len(duplicates),
            'duplicates': duplicates
        })
    
    @action(detail=True, methods=['post'])
    def merge(self, request, pk=None):
        """Merge duplicate submissions"""
        duplicate = self.get_object()
        keep = request.data.get('keep', 'original')  # 'original' or 'duplicate'
        
        result = DataQualityService.merge_duplicates(
            str(duplicate.id),
            keep=keep
        )
        return Response(result)


class ExternalValidationViewSet(viewsets.ModelViewSet):
    """ViewSet for external validations"""
    serializer_class = ExternalValidationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExternalValidation.objects.filter(
            submission__form__user=self.request.user
        ).order_by('-validated_at')
    
    @action(detail=False, methods=['post'])
    def validate_email(self, request):
        """Validate an email address"""
        email = request.data.get('email')
        
        result = DataQualityService.validate_email(email)
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def validate_address(self, request):
        """Validate a physical address"""
        address = request.data.get('address', {})
        
        result = DataQualityService.validate_address(address)
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def validate_phone(self, request):
        """Validate a phone number"""
        phone = request.data.get('phone')
        country = request.data.get('country', 'US')
        
        result = DataQualityService.validate_phone(phone, country)
        return Response(result)


class DataCleansingRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for data cleansing rules"""
    serializer_class = DataCleansingRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DataCleansingRule.objects.filter(form__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def preview(self, request):
        """Preview cleansing result"""
        rule_id = request.data.get('rule_id')
        sample_data = request.data.get('sample_data')
        
        rule = get_object_or_404(DataCleansingRule, id=rule_id)
        result = DataQualityService.preview_cleansing(str(rule.id), sample_data)
        
        return Response(result)


class ExportWithQualityView(views.APIView):
    """Export submissions with data quality scores"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Export submissions with quality scores"""
        form_id = request.data.get('form_id')
        format_type = request.data.get('format', 'csv')  # csv, json, excel
        include_quality = request.data.get('include_quality', True)
        min_quality_score = request.data.get('min_quality_score', 0)
        
        form = get_object_or_404(Form, id=form_id, user=request.user)
        
        from forms.services.export_service import ExportService
        result = ExportService.export_with_quality(
            form_id=str(form.id),
            format_type=format_type,
            include_quality=include_quality,
            min_quality_score=min_quality_score
        )
        
        return Response(result)


# ============================================================
# 8. OFFLINE FORM BUILDING & SYNC
# ============================================================

class OfflineSyncView(views.APIView):
    """Handle offline form building sync"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get forms available for offline editing"""
        forms = Form.objects.filter(user=request.user).values(
            'id', 'title', 'updated_at'
        )
        
        return Response({
            'forms': list(forms),
            'sync_timestamp': timezone.now().isoformat()
        })
    
    def post(self, request):
        """Sync offline changes"""
        changes = request.data.get('changes', [])
        device_id = request.data.get('device_id')
        
        from forms.services.realtime_service import OfflineSyncService
        
        results = []
        conflicts = []
        
        for change in changes:
            result = OfflineSyncService.apply_offline_change(
                user=request.user,
                change=change,
                device_id=device_id
            )
            
            if result.get('conflict'):
                conflicts.append(result)
            else:
                results.append(result)
        
        return Response({
            'applied': len(results),
            'conflicts': conflicts,
            'sync_timestamp': timezone.now().isoformat()
        })


class ConflictResolutionView(views.APIView):
    """Resolve conflicts from simultaneous offline edits"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get pending conflicts for resolution"""
        from forms.services.realtime_service import OfflineSyncService
        
        conflicts = OfflineSyncService.get_pending_conflicts(request.user)
        return Response(conflicts)
    
    def post(self, request):
        """Resolve a conflict"""
        conflict_id = request.data.get('conflict_id')
        resolution = request.data.get('resolution')  # 'local', 'remote', 'merge'
        merged_data = request.data.get('merged_data')
        
        from forms.services.realtime_service import OfflineSyncService
        
        result = OfflineSyncService.resolve_conflict(
            conflict_id=conflict_id,
            resolution=resolution,
            merged_data=merged_data
        )
        
        return Response(result)


class OfflineAnalyticsView(views.APIView):
    """Offline analytics viewing"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get analytics data packaged for offline viewing"""
        form_id = request.query_params.get('form_id')
        
        if form_id:
            form = get_object_or_404(Form, id=form_id, user=request.user)
            forms = [form]
        else:
            forms = Form.objects.filter(user=request.user)[:10]
        
        offline_data = []
        for form in forms:
            data = {
                'form_id': str(form.id),
                'title': form.title,
                'total_submissions': Submission.objects.filter(form=form).count(),
                'recent_submissions': list(
                    Submission.objects.filter(form=form)
                    .order_by('-created_at')[:50]
                    .values('id', 'data', 'created_at')
                ),
                'conversion_rate': form.conversion_rate if hasattr(form, 'conversion_rate') else 0,
            }
            offline_data.append(data)
        
        return Response({
            'analytics': offline_data,
            'generated_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(hours=24)).isoformat()
        })


# ============================================================
# 9. SMART FORM RECOVERY & AUTO-SAVE
# ============================================================

class AutoSaveViewSet(viewsets.ModelViewSet):
    """ViewSet for form builder auto-saves"""
    serializer_class = FormBuilderAutoSaveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormBuilderAutoSave.objects.filter(
            user=self.request.user
        ).order_by('-last_saved_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def save(self, request):
        """Save form builder state"""
        form_id = request.data.get('form_id')
        temp_id = request.data.get('temp_id')  # For unsaved forms
        
        autosave, created = FormBuilderAutoSave.objects.update_or_create(
            user=request.user,
            form_id=form_id if form_id else None,
            temp_id=temp_id if not form_id else '',
            defaults={
                'schema_json': request.data.get('schema_json', {}),
                'settings_json': request.data.get('settings_json', {}),
                'title': request.data.get('title', ''),
                'description': request.data.get('description', ''),
                'editor_state': request.data.get('editor_state', {}),
                'browser_session_id': request.data.get('browser_session_id', ''),
                'device_info': request.data.get('device_info', {})
            }
        )
        
        return Response({
            'success': True,
            'autosave_id': str(autosave.id),
            'saved_at': autosave.last_saved_at.isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest auto-save for a form"""
        form_id = request.query_params.get('form_id')
        temp_id = request.query_params.get('temp_id')
        
        try:
            if form_id:
                autosave = FormBuilderAutoSave.objects.filter(
                    user=request.user,
                    form_id=form_id
                ).latest('last_saved_at')
            elif temp_id:
                autosave = FormBuilderAutoSave.objects.filter(
                    user=request.user,
                    temp_id=temp_id
                ).latest('last_saved_at')
            else:
                autosave = FormBuilderAutoSave.objects.filter(
                    user=request.user
                ).latest('last_saved_at')
            
            serializer = self.get_serializer(autosave)
            return Response(serializer.data)
        except FormBuilderAutoSave.DoesNotExist:
            return Response({'error': 'No auto-save found'}, status=404)


class CrashRecoveryViewSet(viewsets.ModelViewSet):
    """ViewSet for crash recovery"""
    serializer_class = FormBuilderCrashRecoverySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormBuilderCrashRecovery.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending recovery items"""
        recoveries = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(recoveries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def recover(self, request, pk=None):
        """Recover a crashed session"""
        recovery = self.get_object()
        
        recovery.status = 'recovered'
        recovery.recovered_at = timezone.now()
        recovery.save()
        
        # Also mark the autosave as recovered
        recovery.autosave.is_recovered = True
        recovery.autosave.recovered_at = timezone.now()
        recovery.autosave.save()
        
        return Response({
            'success': True,
            'autosave_id': str(recovery.autosave.id),
            'schema_json': recovery.autosave.schema_json,
            'settings_json': recovery.autosave.settings_json
        })
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a recovery item"""
        recovery = self.get_object()
        recovery.status = 'dismissed'
        recovery.save()
        return Response({'success': True})


class DraftScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for draft scheduling"""
    serializer_class = FormDraftScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FormDraftSchedule.objects.filter(
            form__user=self.request.user
        ).order_by('-scheduled_at')
    
    @action(detail=True, methods=['post'])
    def publish_now(self, request, pk=None):
        """Publish a scheduled draft immediately"""
        schedule = self.get_object()
        
        from forms.services.scheduling_service import SchedulingService
        result = SchedulingService.publish_draft(str(schedule.id))
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a scheduled publication"""
        schedule = self.get_object()
        schedule.status = 'cancelled'
        schedule.save()
        return Response({'success': True})


class SubmissionAutoSaveViewSet(viewsets.ModelViewSet):
    """ViewSet for submission auto-saves (user-facing forms)"""
    serializer_class = SubmissionAutoSaveSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return SubmissionAutoSave.objects.filter(session_id=session_id)
        return SubmissionAutoSave.objects.none()
    
    @action(detail=False, methods=['post'])
    def save(self, request):
        """Auto-save form submission progress"""
        form_id = request.data.get('form_id')
        session_id = request.data.get('session_id')
        
        autosave, created = SubmissionAutoSave.objects.update_or_create(
            form_id=form_id,
            session_id=session_id,
            defaults={
                'data_json': request.data.get('data', {}),
                'current_step': request.data.get('current_step', 1),
                'completed_fields': request.data.get('completed_fields', []),
                'device_info': request.data.get('device_info', {}),
                'user_id': request.user.id if request.user.is_authenticated else None,
            }
        )
        
        return Response({
            'success': True,
            'autosave_id': str(autosave.id),
            'resume_token': autosave.resume_token,
            'saved_at': autosave.last_saved_at.isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def resume(self, request):
        """Resume a saved submission"""
        resume_token = request.query_params.get('token')
        
        try:
            autosave = SubmissionAutoSave.objects.get(resume_token=resume_token)
            
            if autosave.expires_at and autosave.expires_at < timezone.now():
                return Response({'error': 'Resume token expired'}, status=410)
            
            serializer = self.get_serializer(autosave)
            return Response(serializer.data)
        except SubmissionAutoSave.DoesNotExist:
            return Response({'error': 'Resume token not found'}, status=404)


# ============================================================
# 10. INTEGRATION MARKETPLACE
# (Already in views_advanced_new.py, adding user-generated connectors)
# ============================================================

class UserIntegrationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for user-generated integration templates"""
    serializer_class = UserIntegrationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Show user's own templates and public templates
        return UserIntegrationTemplate.objects.filter(
            Q(creator=self.request.user) | Q(is_public=True)
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_templates(self, request):
        """Get only user's own templates"""
        templates = UserIntegrationTemplate.objects.filter(creator=request.user)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a template to the marketplace"""
        template = self.get_object()
        
        if template.creator != request.user:
            return Response({'error': 'Only creator can publish'}, status=403)
        
        template.is_public = True
        template.published_at = timezone.now()
        template.save()
        
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone a public template"""
        template = self.get_object()
        
        clone = UserIntegrationTemplate.objects.create(
            creator=request.user,
            name=f"Copy of {template.name}",
            description=template.description,
            template_type=template.template_type,
            api_config=template.api_config,
            request_template=template.request_template,
            response_mapping=template.response_mapping,
            is_public=False,
            parent_template=template
        )
        
        serializer = self.get_serializer(clone)
        return Response(serializer.data, status=201)


class APIConnectorBuilderView(views.APIView):
    """No-code API connector builder"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Build and test an API connector"""
        name = request.data.get('name')
        api_url = request.data.get('api_url')
        method = request.data.get('method', 'POST')
        headers = request.data.get('headers', {})
        body_template = request.data.get('body_template', {})
        auth_type = request.data.get('auth_type', 'none')
        auth_config = request.data.get('auth_config', {})
        
        # Create the connector template
        template = UserIntegrationTemplate.objects.create(
            creator=request.user,
            name=name,
            template_type='api',
            api_config={
                'url': api_url,
                'method': method,
                'headers': headers,
                'auth_type': auth_type,
                'auth_config': auth_config
            },
            request_template=body_template
        )
        
        # Test the connection if requested
        if request.data.get('test', False):
            from forms.services.integration_marketplace_service import IntegrationMarketplaceService
            test_result = IntegrationMarketplaceService.test_api_connector(str(template.id))
            template.test_status = 'passed' if test_result.get('success') else 'failed'
            template.last_tested_at = timezone.now()
            template.save()
            
            return Response({
                'template_id': str(template.id),
                'test_result': test_result
            }, status=201)
        
        return Response({
            'template_id': str(template.id),
            'message': 'Connector created successfully'
        }, status=201)
    
    def get(self, request):
        """Get available pre-built templates for popular services"""
        category = request.query_params.get('category')
        
        queryset = IntegrationTemplate.objects.filter(is_active=True)
        if category:
            queryset = queryset.filter(category=category)
        
        templates = queryset.values(
            'id', 'name', 'description', 'category',
            'provider__name', 'install_count'
        ).order_by('-install_count')[:50]
        
        return Response(list(templates))


class IntegrationExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for integration execution logs"""
    serializer_class = IntegrationExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return IntegrationExecution.objects.filter(
            workflow__user=self.request.user
        ).order_by('-started_at')
    
    @action(detail=False, methods=['get'])
    def by_workflow(self, request):
        """Get executions for a specific workflow"""
        workflow_id = request.query_params.get('workflow_id')
        if not workflow_id:
            return Response({'error': 'workflow_id required'}, status=400)
        
        executions = self.get_queryset().filter(workflow_id=workflow_id)[:100]
        serializer = self.get_serializer(executions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed execution"""
        execution = self.get_object()
        
        if execution.status != 'failed':
            return Response({'error': 'Only failed executions can be retried'}, status=400)
        
        from forms.services.integration_marketplace_service import IntegrationMarketplaceService
        result = IntegrationMarketplaceService.retry_execution(str(execution.id))
        
        return Response(result)
