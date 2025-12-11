"""
Views for automation features including:
- Form Optimization
- Lead Nurturing Workflows
- Form Personalization
- Compliance Scanning
- Voice Design
- Predictive Analytics
- Integration Marketplace
- AI Content Generation
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Form, Submission
from .models_advanced import (
    NurturingWorkflow, WorkflowExecution, FormIntegration, AlertConfig, AlertHistory,
    VoiceDesignSession, ComplianceScan, OptimizationSuggestion,
    DailyFormStats, GeneratedContent, PersonalizationRule
)
from .services.optimization_service import FormOptimizationService
from .services.workflow_service import WorkflowService
from .services.personalization_service import PersonalizationService
from .services.compliance_service import ComplianceService
from .services.voice_design_service import VoiceDesignService
from .services.predictive_analytics_service import PredictiveAnalyticsService
from .services.marketplace_service import IntegrationMarketplaceService
from .services.ai_content_service import AIContentService


# ========================================
# FORM OPTIMIZATION
# ========================================

class FormOptimizationViewSet(viewsets.ViewSet):
    """API for AI-powered form optimization"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FormOptimizationService()
    
    @action(detail=True, methods=['get'])
    def analyze(self, request, pk=None):
        """Analyze form performance and get optimization score"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        analysis = self.service.analyze_form_performance(form.id)
        return Response(analysis)
    
    @action(detail=True, methods=['get'])
    def suggestions(self, request, pk=None):
        """Get AI-generated optimization suggestions"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        # Get stored suggestions
        suggestions = OptimizationSuggestion.objects.filter(
            form=form,
            status='pending'
        ).values(
            'id', 'category', 'priority', 'title', 
            'description', 'expected_impact', 'target_field_id'
        )
        
        return Response(list(suggestions))
    
    @action(detail=True, methods=['post'])
    def generate_suggestions(self, request, pk=None):
        """Generate new optimization suggestions using AI"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        suggestions = self.service.generate_optimization_suggestions(form.id)
        
        # Store suggestions
        for suggestion in suggestions:
            OptimizationSuggestion.objects.create(
                form=form,
                category=suggestion.get('category', 'conversion'),
                priority=suggestion.get('priority', 'medium'),
                title=suggestion.get('title'),
                description=suggestion.get('description'),
                expected_impact=suggestion.get('expected_impact'),
                target_field_id=suggestion.get('field_id', ''),
                current_value=suggestion.get('current_value', {}),
                suggested_value=suggestion.get('suggested_value', {}),
            )
        
        return Response({'suggestions': suggestions, 'count': len(suggestions)})
    
    @action(detail=True, methods=['post'], url_path='apply/(?P<suggestion_id>[^/.]+)')
    def apply_suggestion(self, request, pk=None, suggestion_id=None):
        """Apply an optimization suggestion"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        suggestion = get_object_or_404(
            OptimizationSuggestion, 
            pk=suggestion_id, 
            form=form
        )
        
        result = self.service.apply_optimization(form.id, {
            'field_id': suggestion.target_field_id,
            'change_type': suggestion.category,
            'current_value': suggestion.current_value,
            'suggested_value': suggestion.suggested_value,
        })
        
        if result.get('success'):
            suggestion.status = 'applied'
            suggestion.applied_at = timezone.now()
            suggestion.applied_by = request.user
            suggestion.save()
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def auto_optimize(self, request, pk=None):
        """Run automatic optimization on the form"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        result = self.service.auto_optimize_form(form.id)
        return Response(result)
    
    @action(detail=True, methods=['post'], url_path='dismiss/(?P<suggestion_id>[^/.]+)')
    def dismiss_suggestion(self, request, pk=None, suggestion_id=None):
        """Dismiss an optimization suggestion"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        suggestion = get_object_or_404(
            OptimizationSuggestion, 
            pk=suggestion_id, 
            form=form
        )
        suggestion.status = 'dismissed'
        suggestion.save()
        return Response({'status': 'dismissed'})


# ========================================
# LEAD NURTURING WORKFLOWS
# ========================================

class WorkflowViewSet(viewsets.ModelViewSet):
    """API for managing nurturing workflows"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = WorkflowService()
    
    def get_queryset(self):
        return NurturingWorkflow.objects.filter(
            form__user=self.request.user
        )
    
    def list(self, request):
        form_id = request.query_params.get('form_id')
        queryset = self.get_queryset()
        if form_id:
            queryset = queryset.filter(form_id=form_id)
        
        workflows = queryset.values(
            'id', 'name', 'description', 'status', 'trigger_type',
            'is_active', 'total_triggered', 'total_completed', 'total_failed',
            'created_at'
        )
        return Response(list(workflows))
    
    def create(self, request):
        form = get_object_or_404(Form, pk=request.data.get('form_id'), user=request.user)
        
        workflow = NurturingWorkflow.objects.create(
            form=form,
            name=request.data.get('name'),
            description=request.data.get('description', ''),
            trigger_type=request.data.get('trigger_type', 'submission'),
            trigger_conditions=request.data.get('trigger_conditions', {}),
            actions=request.data.get('actions', []),
        )
        
        return Response({
            'id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status,
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        workflow = get_object_or_404(self.get_queryset(), pk=pk)
        return Response({
            'id': str(workflow.id),
            'form_id': str(workflow.form.id),
            'name': workflow.name,
            'description': workflow.description,
            'status': workflow.status,
            'trigger_type': workflow.trigger_type,
            'trigger_conditions': workflow.trigger_conditions,
            'actions': workflow.actions,
            'is_active': workflow.is_active,
            'total_triggered': workflow.total_triggered,
            'total_completed': workflow.total_completed,
            'total_failed': workflow.total_failed,
            'created_at': workflow.created_at,
        })
    
    def update(self, request, pk=None):
        workflow = get_object_or_404(self.get_queryset(), pk=pk)
        
        workflow.name = request.data.get('name', workflow.name)
        workflow.description = request.data.get('description', workflow.description)
        workflow.trigger_type = request.data.get('trigger_type', workflow.trigger_type)
        workflow.trigger_conditions = request.data.get('trigger_conditions', workflow.trigger_conditions)
        workflow.actions = request.data.get('actions', workflow.actions)
        workflow.save()
        
        return Response({'status': 'updated'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a workflow"""
        workflow = get_object_or_404(self.get_queryset(), pk=pk)
        workflow.status = 'active'
        workflow.is_active = True
        workflow.save()
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a workflow"""
        workflow = get_object_or_404(self.get_queryset(), pk=pk)
        workflow.status = 'paused'
        workflow.is_active = False
        workflow.save()
        return Response({'status': 'paused'})
    
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Manually trigger a workflow"""
        workflow = get_object_or_404(self.get_queryset(), pk=pk)
        submission_id = request.data.get('submission_id')
        submission = get_object_or_404(Submission, pk=submission_id)
        
        result = self.service.trigger_workflow(workflow.id, submission.payload_json)
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get workflow execution history"""
        workflow = get_object_or_404(self.get_queryset(), pk=pk)
        executions = WorkflowExecution.objects.filter(workflow=workflow).values(
            'id', 'status', 'current_action_index', 'error_message',
            'started_at', 'completed_at'
        )[:50]
        return Response(list(executions))
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get workflow templates"""
        templates = self.service.get_workflow_templates()
        return Response(templates)


# ========================================
# FORM PERSONALIZATION
# ========================================

class PersonalizationViewSet(viewsets.ViewSet):
    """API for form personalization rules"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PersonalizationService()
    
    def list(self, request):
        form_id = request.query_params.get('form_id')
        if not form_id:
            return Response({'error': 'form_id required'}, status=400)
        
        form = get_object_or_404(Form, pk=form_id, user=request.user)
        rules = PersonalizationRule.objects.filter(form=form).values(
            'id', 'name', 'is_active', 'priority', 'trigger_type',
            'action_type', 'times_triggered', 'created_at'
        )
        return Response(list(rules))
    
    def create(self, request):
        form = get_object_or_404(Form, pk=request.data.get('form_id'), user=request.user)
        
        rule = PersonalizationRule.objects.create(
            form=form,
            name=request.data.get('name'),
            priority=request.data.get('priority', 0),
            trigger_type=request.data.get('trigger_type'),
            trigger_config=request.data.get('trigger_config', {}),
            action_type=request.data.get('action_type'),
            action_config=request.data.get('action_config', {}),
        )
        
        return Response({
            'id': str(rule.id),
            'name': rule.name,
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        rule = get_object_or_404(
            PersonalizationRule, 
            pk=pk, 
            form__user=request.user
        )
        return Response({
            'id': str(rule.id),
            'form_id': str(rule.form.id),
            'name': rule.name,
            'is_active': rule.is_active,
            'priority': rule.priority,
            'trigger_type': rule.trigger_type,
            'trigger_config': rule.trigger_config,
            'action_type': rule.action_type,
            'action_config': rule.action_config,
            'times_triggered': rule.times_triggered,
        })
    
    def update(self, request, pk=None):
        rule = get_object_or_404(
            PersonalizationRule, 
            pk=pk, 
            form__user=request.user
        )
        
        for field in ['name', 'priority', 'trigger_type', 'trigger_config', 
                      'action_type', 'action_config', 'is_active']:
            if field in request.data:
                setattr(rule, field, request.data[field])
        rule.save()
        
        return Response({'status': 'updated'})
    
    def destroy(self, request, pk=None):
        rule = get_object_or_404(
            PersonalizationRule, 
            pk=pk, 
            form__user=request.user
        )
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def personalize(self, request):
        """Get personalized form schema based on context"""
        form_id = request.data.get('form_id')
        context = request.data.get('context', {})
        
        form = get_object_or_404(Form, pk=form_id)
        result = self.service.personalize_form(form.schema, context)
        return Response(result)


# ========================================
# COMPLIANCE SCANNING
# ========================================

class ComplianceViewSet(viewsets.ViewSet):
    """API for compliance scanning and fixes"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ComplianceService()
    
    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
        """Run compliance scan on a form"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        scan_types = request.data.get('scan_types', ['gdpr', 'wcag'])
        
        # Create scan record
        scan = ComplianceScan.objects.create(
            form=form,
            scan_type='full' if len(scan_types) > 1 else scan_types[0],
            status='running',
            started_at=timezone.now(),
        )
        
        # Run scan
        result = self.service.scan_form(form.schema, scan_types)
        
        # Update scan record
        scan.status = 'completed'
        scan.overall_score = result.get('overall_score', 0)
        scan.issues_found = result.get('total_issues', 0)
        scan.scan_results = result
        scan.completed_at = timezone.now()
        scan.save()
        
        return Response({
            'scan_id': str(scan.id),
            **result
        })
    
    @action(detail=True, methods=['post'])
    def auto_fix(self, request, pk=None):
        """Apply automatic fixes to compliance issues"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        # Get latest scan
        scan = ComplianceScan.objects.filter(form=form).order_by('-created_at').first()
        if not scan:
            return Response({'error': 'No scan found, run scan first'}, status=400)
        
        # Apply fixes
        fixed_schema = self.service.apply_auto_fixes(form.schema, scan.scan_results)
        
        # Update form
        form.schema = fixed_schema.get('schema', form.schema)
        form.save()
        
        # Update scan
        scan.issues_fixed = fixed_schema.get('fixes_applied', 0)
        scan.auto_fixes_applied = fixed_schema.get('fix_details', [])
        scan.save()
        
        return Response(fixed_schema)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get compliance scan history for a form"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        scans = ComplianceScan.objects.filter(form=form).values(
            'id', 'scan_type', 'status', 'overall_score',
            'issues_found', 'issues_fixed', 'created_at'
        )[:20]
        return Response(list(scans))
    
    @action(detail=True, methods=['post'])
    def generate_privacy_policy(self, request, pk=None):
        """Generate privacy policy based on form data collection"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        company_name = request.data.get('company_name', 'Our Company')
        
        policy = self.service.generate_privacy_policy(form.schema, company_name)
        return Response({'policy': policy})


# ========================================
# VOICE DESIGN
# ========================================

class VoiceDesignViewSet(viewsets.ViewSet):
    """API for voice-activated form design"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = VoiceDesignService()
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """Start a new voice design session"""
        form_id = request.data.get('form_id')
        form = None
        initial_schema = request.data.get('initial_schema', {'fields': []})
        
        if form_id:
            form = get_object_or_404(Form, pk=form_id, user=request.user)
            initial_schema = form.schema
        
        session_token = self.service.start_session(initial_schema)
        
        # Save session to database
        VoiceDesignSession.objects.create(
            user=request.user,
            form=form,
            session_token=session_token,
            current_schema=initial_schema,
        )
        
        return Response({
            'session_token': session_token,
            'schema': initial_schema,
        })
    
    @action(detail=False, methods=['post'])
    def process_audio(self, request):
        """Process audio input and execute command"""
        session_token = request.data.get('session_token')
        audio_base64 = request.data.get('audio')
        
        session = get_object_or_404(
            VoiceDesignSession, 
            session_token=session_token,
            user=request.user,
            is_active=True
        )
        
        result = self.service.process_audio_command(session_token, audio_base64)
        
        # Update session
        session.current_schema = result.get('schema', session.current_schema)
        session.command_history.append({
            'transcript': result.get('transcript'),
            'action': result.get('action'),
            'timestamp': timezone.now().isoformat(),
        })
        session.save()
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def process_text(self, request):
        """Process text command (for testing or accessibility)"""
        session_token = request.data.get('session_token')
        command = request.data.get('command')
        
        session = get_object_or_404(
            VoiceDesignSession, 
            session_token=session_token,
            user=request.user,
            is_active=True
        )
        
        result = self.service.process_text_command(session_token, command)
        
        # Update session
        session.current_schema = result.get('schema', session.current_schema)
        session.command_history.append({
            'command': command,
            'action': result.get('action'),
            'timestamp': timezone.now().isoformat(),
        })
        session.save()
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def end_session(self, request):
        """End voice design session and optionally save form"""
        session_token = request.data.get('session_token')
        save_to_form = request.data.get('save_to_form', False)
        
        session = get_object_or_404(
            VoiceDesignSession, 
            session_token=session_token,
            user=request.user
        )
        
        final_schema = self.service.end_session(session_token)
        
        session.is_active = False
        session.ended_at = timezone.now()
        session.current_schema = final_schema
        session.save()
        
        form_id = None
        if save_to_form:
            if session.form:
                session.form.schema = final_schema
                session.form.save()
                form_id = str(session.form.id)
            else:
                form = Form.objects.create(
                    user=request.user,
                    title=final_schema.get('title', 'Voice-Created Form'),
                    description=final_schema.get('description', ''),
                    schema=final_schema,
                )
                form_id = str(form.id)
        
        return Response({
            'schema': final_schema,
            'form_id': form_id,
        })
    
    @action(detail=False, methods=['get'])
    def session_history(self, request):
        """Get command history for current session"""
        session_token = request.query_params.get('session_token')
        session = get_object_or_404(
            VoiceDesignSession, 
            session_token=session_token,
            user=request.user
        )
        return Response({
            'commands': session.command_history,
            'schema': session.current_schema,
        })


# ========================================
# PREDICTIVE ANALYTICS
# ========================================

class PredictiveAnalyticsViewSet(viewsets.ViewSet):
    """API for predictive analytics and forecasting"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PredictiveAnalyticsService()
    
    @action(detail=True, methods=['get'])
    def forecast(self, request, pk=None):
        """Get submission forecast for a form"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        days = int(request.query_params.get('days', 7))
        
        prediction = self.service.predict_submissions(form.id, days)
        return Response(prediction)
    
    @action(detail=True, methods=['get'])
    def anomalies(self, request, pk=None):
        """Detect anomalies in form performance"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        anomalies = self.service.detect_anomalies(form.id)
        return Response(anomalies)
    
    @action(detail=True, methods=['get'])
    def insights(self, request, pk=None):
        """Get AI-generated insights about form performance"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        insights = self.service.generate_insights(form.id)
        return Response(insights)
    
    @action(detail=True, methods=['get'])
    def trends(self, request, pk=None):
        """Get trend analysis for a form"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        daily_stats = DailyFormStats.objects.filter(form=form).order_by('-date')[:30]
        
        trend_data = []
        for stat in daily_stats:
            trend_data.append({
                'date': stat.date.isoformat(),
                'views': stat.views,
                'submissions': stat.submissions,
                'conversion_rate': stat.conversion_rate,
                'abandonment_rate': stat.abandonment_rate,
                'avg_completion_time': stat.avg_completion_time,
            })
        
        return Response({
            'data': trend_data,
            'period': '30 days',
        })


# ========================================
# ALERTS
# ========================================

class AlertViewSet(viewsets.ModelViewSet):
    """API for managing analytics alerts"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AlertConfig.objects.filter(form__user=self.request.user)
    
    def list(self, request):
        form_id = request.query_params.get('form_id')
        queryset = self.get_queryset()
        if form_id:
            queryset = queryset.filter(form_id=form_id)
        
        alerts = queryset.values(
            'id', 'name', 'alert_type', 'is_active',
            'threshold_value', 'last_triggered_at', 'trigger_count'
        )
        return Response(list(alerts))
    
    def create(self, request):
        form = get_object_or_404(Form, pk=request.data.get('form_id'), user=request.user)
        
        alert = AlertConfig.objects.create(
            form=form,
            name=request.data.get('name'),
            alert_type=request.data.get('alert_type'),
            threshold_value=request.data.get('threshold_value', 0),
            threshold_direction=request.data.get('threshold_direction', 'above'),
            comparison_period=request.data.get('comparison_period', 'day'),
            notification_channels=request.data.get('notification_channels', ['email']),
            notification_emails=request.data.get('notification_emails', []),
            slack_webhook=request.data.get('slack_webhook', ''),
            cooldown_minutes=request.data.get('cooldown_minutes', 60),
        )
        
        return Response({
            'id': str(alert.id),
            'name': alert.name,
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get alert trigger history"""
        alert = get_object_or_404(self.get_queryset(), pk=pk)
        history = AlertHistory.objects.filter(alert_config=alert).values(
            'id', 'triggered_value', 'threshold_value', 'message',
            'acknowledged', 'created_at'
        )[:50]
        return Response(list(history))
    
    @action(detail=True, methods=['post'], url_path='acknowledge/(?P<history_id>[^/.]+)')
    def acknowledge(self, request, pk=None, history_id=None):
        """Acknowledge an alert"""
        alert = get_object_or_404(self.get_queryset(), pk=pk)
        history = get_object_or_404(AlertHistory, pk=history_id, alert_config=alert)
        
        history.acknowledged = True
        history.acknowledged_by = request.user
        history.acknowledged_at = timezone.now()
        history.save()
        
        return Response({'status': 'acknowledged'})


# ========================================
# INTEGRATION MARKETPLACE
# ========================================

class IntegrationMarketplaceViewSet(viewsets.ViewSet):
    """API for integration marketplace"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = IntegrationMarketplaceService()
    
    @action(detail=False, methods=['get'])
    def catalog(self, request):
        """Get available integrations"""
        category = request.query_params.get('category')
        catalog = self.service.get_integration_catalog(category)
        return Response(catalog)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get integration categories"""
        catalog = self.service.get_integration_catalog()
        categories = list(set(i['category'] for i in catalog))
        return Response(categories)
    
    def list(self, request):
        """List user's configured integrations"""
        form_id = request.query_params.get('form_id')
        queryset = FormIntegration.objects.filter(form__user=request.user)
        if form_id:
            queryset = queryset.filter(form_id=form_id)
        
        integrations = queryset.values(
            'id', 'integration_id', 'name', 'status',
            'sync_on_submit', 'last_sync_at', 'last_sync_status'
        )
        return Response(list(integrations))
    
    def create(self, request):
        """Set up a new integration"""
        form = get_object_or_404(Form, pk=request.data.get('form_id'), user=request.user)
        integration_id = request.data.get('integration_id')
        
        # Get integration info from catalog
        catalog = self.service.get_integration_catalog()
        integration_info = next(
            (i for i in catalog if i['id'] == integration_id), 
            None
        )
        
        if not integration_info:
            return Response({'error': 'Integration not found'}, status=404)
        
        integration = FormIntegration.objects.create(
            form=form,
            integration_id=integration_id,
            name=integration_info['name'],
            auth_type=integration_info.get('auth_type', 'api_key'),
            config=request.data.get('config', {}),
            field_mapping=request.data.get('field_mapping', {}),
        )
        
        return Response({
            'id': str(integration.id),
            'name': integration.name,
            'status': integration.status,
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        """Connect/authenticate an integration"""
        integration = get_object_or_404(
            FormIntegration, 
            pk=pk, 
            form__user=request.user
        )
        
        credentials = request.data.get('credentials', {})
        
        # Try to connect
        result = self.service.connect_integration(
            integration.integration_id,
            credentials
        )
        
        if result.get('success'):
            integration.credentials = credentials  # Should encrypt in production
            integration.status = 'connected'
            integration.save()
        else:
            integration.status = 'error'
            integration.sync_error = result.get('error', 'Connection failed')
            integration.save()
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Manually sync data to integration"""
        integration = get_object_or_404(
            FormIntegration, 
            pk=pk, 
            form__user=request.user
        )
        
        submission_id = request.data.get('submission_id')
        if submission_id:
            submission = get_object_or_404(Submission, pk=submission_id)
            data = submission.payload_json
        else:
            data = request.data.get('data', {})
        
        result = self.service.sync_to_integration(
            integration.integration_id,
            integration.credentials,
            data,
            integration.field_mapping
        )
        
        integration.last_sync_at = timezone.now()
        integration.last_sync_status = 'success' if result.get('success') else 'error'
        integration.sync_error = result.get('error', '')
        integration.save()
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def suggest_mapping(self, request, pk=None):
        """Get AI-suggested field mappings"""
        integration = get_object_or_404(
            FormIntegration, 
            pk=pk, 
            form__user=request.user
        )
        
        form_fields = integration.form.schema.get('fields', [])
        suggestions = self.service.suggest_field_mapping(
            integration.integration_id,
            form_fields
        )
        return Response(suggestions)
    
    @action(detail=True, methods=['post'])
    def oauth_callback(self, request, pk=None):
        """Handle OAuth callback"""
        integration = get_object_or_404(
            FormIntegration, 
            pk=pk, 
            form__user=request.user
        )
        
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        
        result = self.service.handle_oauth_callback(
            integration.integration_id,
            code,
            redirect_uri
        )
        
        if result.get('success'):
            integration.credentials = result.get('tokens', {})
            integration.status = 'connected'
            integration.save()
        
        return Response(result)


# ========================================
# AI CONTENT GENERATION
# ========================================

class AIContentViewSet(viewsets.ViewSet):
    """API for AI-powered content generation"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = AIContentService()
    
    @action(detail=True, methods=['post'])
    def generate_description(self, request, pk=None):
        """Generate form description"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        description = self.service.generate_form_description(
            form.title,
            form.schema.get('fields', []),
            context=request.data.get('context'),
            tone=request.data.get('tone', 'professional'),
        )
        
        # Store generated content
        GeneratedContent.objects.create(
            form=form,
            content_type='description',
            content={'text': description},
        )
        
        return Response({'description': description})
    
    @action(detail=True, methods=['post'])
    def generate_thank_you(self, request, pk=None):
        """Generate thank you message"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        content = self.service.generate_thank_you_message(
            form.title,
            form_type=request.data.get('form_type', 'contact'),
            brand_name=request.data.get('brand_name'),
            next_steps=request.data.get('next_steps'),
        )
        
        GeneratedContent.objects.create(
            form=form,
            content_type='thank_you',
            content=content,
        )
        
        return Response(content)
    
    @action(detail=True, methods=['post'])
    def generate_email(self, request, pk=None):
        """Generate email template"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        template = self.service.generate_email_template(
            template_type=request.data.get('template_type', 'confirmation'),
            form_title=form.title,
            brand_name=request.data.get('brand_name'),
            fields=form.schema.get('fields', []),
        )
        
        GeneratedContent.objects.create(
            form=form,
            content_type='email_template',
            content=template,
        )
        
        return Response(template)
    
    @action(detail=True, methods=['post'])
    def generate_placeholders(self, request, pk=None):
        """Generate field placeholders"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        placeholders = self.service.generate_field_placeholders(
            form.schema.get('fields', [])
        )
        
        return Response({'placeholders': placeholders})
    
    @action(detail=True, methods=['post'])
    def generate_help_text(self, request, pk=None):
        """Generate help text for a field"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        field = request.data.get('field')
        
        help_text = self.service.generate_field_help_text(
            field,
            context=request.data.get('context'),
        )
        
        return Response({'help_text': help_text})
    
    @action(detail=True, methods=['post'])
    def generate_questions(self, request, pk=None):
        """Generate survey/quiz questions"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        questions = self.service.generate_form_questions(
            topic=request.data.get('topic'),
            question_count=request.data.get('count', 5),
            question_type=request.data.get('type', 'open'),
            context=request.data.get('context'),
        )
        
        return Response({'questions': questions})
    
    @action(detail=True, methods=['post'])
    def improve_copy(self, request, pk=None):
        """Improve all form text content"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        improved_schema = self.service.improve_form_copy(
            form.schema,
            improvements=request.data.get('improvements'),
        )
        
        return Response({'schema': improved_schema})
    
    @action(detail=True, methods=['post'])
    def translate(self, request, pk=None):
        """Translate form to another language"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        target_language = request.data.get('language', 'Spanish')
        
        translated_schema = self.service.translate_form(
            form.schema,
            target_language,
        )
        
        GeneratedContent.objects.create(
            form=form,
            content_type='translation',
            content=translated_schema,
            language=target_language[:10],
        )
        
        return Response({'schema': translated_schema})
    
    @action(detail=True, methods=['post'])
    def generate_consent(self, request, pk=None):
        """Generate GDPR consent text"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        consent = self.service.generate_consent_text(
            purposes=request.data.get('purposes', ['data processing']),
            company_name=request.data.get('company_name', 'Our Company'),
            privacy_url=request.data.get('privacy_url'),
        )
        
        GeneratedContent.objects.create(
            form=form,
            content_type='consent_text',
            content=consent,
        )
        
        return Response(consent)
    
    @action(detail=True, methods=['post'])
    def suggest_improvements(self, request, pk=None):
        """Get AI suggestions for form improvements"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        suggestions = self.service.suggest_form_improvements(
            form.schema,
            analytics=request.data.get('analytics'),
        )
        
        return Response({'suggestions': suggestions})
    
    @action(detail=True, methods=['get'])
    def generated_content(self, request, pk=None):
        """Get all generated content for a form"""
        form = get_object_or_404(Form, pk=pk, user=request.user)
        
        content = GeneratedContent.objects.filter(form=form).values(
            'id', 'content_type', 'content', 'language',
            'is_applied', 'created_at'
        )[:50]
        
        return Response(list(content))
