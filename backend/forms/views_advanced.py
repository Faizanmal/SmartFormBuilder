"""
API views for advanced form features
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta

from forms.models import Form
from forms.models_advanced import (
    FormStep, PartialSubmission, FormABTest, TeamMember,
    FormShare, FormAnalytics, LeadScore,
    AutomatedFollowUp, WhiteLabelConfig, AuditLog
)
from forms.models_collaboration import FormComment
from forms.serializers_advanced import (
    FormStepSerializer, PartialSubmissionSerializer, FormABTestSerializer,
    TeamMemberSerializer, FormCommentSerializer, FormShareSerializer,
    FormAnalyticsSerializer, LeadScoreSerializer, AutomatedFollowUpSerializer,
    WhiteLabelConfigSerializer, AuditLogSerializer
)
from forms.services.multi_step_service import MultiStepFormService
from forms.services.ab_testing_service import ABTestingService
from forms.services.analytics_service import FormAnalyticsService
from forms.services.lead_scoring_service import LeadScoringService
from forms.services.follow_up_service import FollowUpService


class FormStepViewSet(viewsets.ModelViewSet):
    """ViewSet for managing form steps"""
    
    serializer_class = FormStepSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        form_id = self.request.query_params.get('form_id')
        if form_id:
            form = get_object_or_404(Form, id=form_id, user=self.request.user)
            return FormStep.objects.filter(form=form)
        return FormStep.objects.filter(form__user=self.request.user)


class PartialSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing partial/draft submissions"""
    
    serializer_class = PartialSubmissionSerializer
    permission_classes = [AllowAny]  # Public endpoint
    
    def get_queryset(self):
        return PartialSubmission.objects.all()
    
    @action(detail=False, methods=['post'])
    def save_progress(self, request):
        """Save or update partial submission"""
        form_slug = request.data.get('form_slug')
        email = request.data.get('email')
        payload = request.data.get('payload', {})
        current_step = request.data.get('current_step', 1)
        
        form = get_object_or_404(Form, slug=form_slug, is_active=True)
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        partial, resume_token = MultiStepFormService.save_partial_submission(
            form, email, payload, current_step, ip_address, user_agent
        )
        
        return Response({
            'id': partial.id,
            'resume_token': resume_token,
            'message': 'Progress saved successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def resume(self, request):
        """Resume a partial submission"""
        resume_token = request.query_params.get('token')
        
        if not resume_token:
            return Response({'error': 'Resume token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        partial = MultiStepFormService.get_partial_submission(resume_token)
        
        if not partial:
            return Response({'error': 'Invalid or expired resume token'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(partial)
        return Response(serializer.data)


class FormABTestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing A/B tests"""
    
    serializer_class = FormABTestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FormABTest.objects.filter(form__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start an A/B test"""
        ab_test = self.get_object()
        ab_test.status = 'running'
        ab_test.start_date = timezone.now()
        ab_test.save()
        return Response({'status': 'running', 'start_date': ab_test.start_date})
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop an A/B test"""
        ab_test = self.get_object()
        ab_test.status = 'completed'
        ab_test.end_date = timezone.now()
        ab_test.save()
        return Response({'status': 'completed', 'end_date': ab_test.end_date})
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get A/B test results with statistical significance"""
        ab_test = self.get_object()
        results = ABTestingService.get_test_results(ab_test)
        return Response(results)
    
    @action(detail=True, methods=['post'])
    def declare_winner(self, request, pk=None):
        """Manually declare a winner"""
        ab_test = self.get_object()
        winner = request.data.get('winner')
        
        if winner not in ['a', 'b']:
            return Response({'error': 'Winner must be "a" or "b"'}, status=status.HTTP_400_BAD_REQUEST)
        
        ab_test.winner = winner
        ab_test.status = 'completed'
        ab_test.end_date = timezone.now()
        ab_test.save()
        
        return Response({'winner': winner, 'status': 'completed'})


class TeamMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for managing team members"""
    
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        team_id = self.kwargs.get('team_pk')
        if team_id:
            # Check if user owns or is member of the team
            from users.models import Team
            team = get_object_or_404(Team, id=team_id)
            if team.owner == self.request.user or self.request.user in team.members.all():
                return TeamMember.objects.filter(team=team)
        return TeamMember.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)


class FormCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for form comments and annotations"""
    
    serializer_class = FormCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        form_id = self.kwargs.get('form_pk')
        if form_id:
            form = get_object_or_404(Form, id=form_id)
            # Check if user has access to this form
            return FormComment.objects.filter(form=form)
        return FormComment.objects.none()
    
    def perform_create(self, serializer):
        form_id = self.kwargs.get('form_pk')
        form = get_object_or_404(Form, id=form_id)
        serializer.save(form=form, user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, form_pk=None, pk=None):
        """Resolve a comment"""
        comment = self.get_object()
        comment.resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()
        return Response({'status': 'resolved'})


class FormShareViewSet(viewsets.ModelViewSet):
    """ViewSet for form sharing"""
    
    serializer_class = FormShareSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FormShare.objects.filter(form__user=self.request.user)
    
    def perform_create(self, serializer):
        import secrets
        share_token = secrets.token_urlsafe(32)
        serializer.save(created_by=self.request.user, share_token=share_token)


class FormAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for form analytics (read-only)"""
    
    serializer_class = FormAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        form_id = self.kwargs.get('form_pk')
        if form_id:
            form = get_object_or_404(Form, id=form_id, user=self.request.user)
            return FormAnalytics.objects.filter(form=form)
        return FormAnalytics.objects.none()
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request, form_pk=None):
        """Get comprehensive analytics dashboard data"""
        form = get_object_or_404(Form, id=form_pk, user=request.user)
        
        # Get date range from query params
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            date_from = timezone.datetime.fromisoformat(date_from)
        else:
            date_from = timezone.now() - timedelta(days=30)
        
        if date_to:
            date_to = timezone.datetime.fromisoformat(date_to)
        
        # Gather all analytics data
        field_analytics = FormAnalyticsService.get_field_analytics(form, date_from, date_to)
        funnel_analytics = FormAnalyticsService.get_funnel_analytics(form, date_from, date_to)
        device_analytics = FormAnalyticsService.get_device_analytics(form, date_from, date_to)
        geographic_analytics = FormAnalyticsService.get_geographic_analytics(form, date_from, date_to)
        time_series = FormAnalyticsService.get_time_series_data(form, date_from, date_to)
        heat_map = FormAnalyticsService.generate_heat_map_data(form, date_from, date_to)
        
        return Response({
            'field_analytics': field_analytics,
            'funnel': funnel_analytics,
            'devices': device_analytics,
            'geography': geographic_analytics,
            'time_series': time_series,
            'heat_map': heat_map,
        })


class LeadScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for lead scoring and management"""
    
    serializer_class = LeadScoreSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LeadScore.objects.filter(submission__form__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign lead to team member"""
        lead = self.get_object()
        user_id = request.data.get('user_id')
        
        from users.models import User
        assigned_to = get_object_or_404(User, id=user_id)
        
        lead.assigned_to = assigned_to
        lead.save()
        
        return Response({'assigned_to': assigned_to.email})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update follow-up status"""
        lead = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status not in ['pending', 'contacted', 'negotiating', 'won', 'lost']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        lead.follow_up_status = new_status
        if notes:
            lead.notes = notes
        if new_status == 'contacted':
            lead.last_contacted_at = timezone.now()
        lead.save()
        
        return Response({'status': new_status})
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get lead analytics"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            date_from = timezone.datetime.fromisoformat(date_from)
        if date_to:
            date_to = timezone.datetime.fromisoformat(date_to)
        
        analytics = LeadScoringService.get_lead_analytics(request.user, date_from, date_to)
        return Response(analytics)


class AutomatedFollowUpViewSet(viewsets.ModelViewSet):
    """ViewSet for managing automated follow-ups"""
    
    serializer_class = AutomatedFollowUpSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AutomatedFollowUp.objects.filter(form__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """Manually trigger a follow-up email"""
        follow_up = self.get_object()
        success = FollowUpService.send_follow_up(follow_up)
        
        if success:
            return Response({'status': 'sent', 'sent_at': follow_up.sent_at})
        else:
            return Response({'status': 'failed', 'error': follow_up.error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WhiteLabelConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for white-label configuration"""
    
    serializer_class = WhiteLabelConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WhiteLabelConfig.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs (read-only)"""
    
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AuditLog.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export audit logs"""
        logs = self.get_queryset()
        
        # Apply date filter
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            logs = logs.filter(created_at__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__lte=date_to)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
