"""
Views for new advanced features
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone

from forms.models_new_features import *
from forms.serializers_new_features import *
from forms.services.field_dependency_service import FieldDependencyService
from forms.services.bulk_action_service import BulkActionService
from forms.services.spam_detection_service import SpamDetectionService
from forms.services.external_validation_service import ExternalValidationService
from forms.services.new_features_combined_service import *


class FieldDependencyViewSet(viewsets.ModelViewSet):
    """ViewSet for field dependencies"""
    serializer_class = FieldDependencySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FieldDependency.objects.filter(form__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a dependency with sample data"""
        dependency = self.get_object()
        source_value = request.data.get('source_value')
        
        result = FieldDependencyService.execute_dependency(
            dependency, source_value
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def populate_zipcode(self, request):
        """Helper endpoint to populate from ZIP code"""
        zipcode = request.data.get('zipcode')
        country = request.data.get('country', 'US')
        
        result = FieldDependencyService.populate_from_zipcode(zipcode, country)
        return Response(result)


class BulkActionViewSet(viewsets.ModelViewSet):
    """ViewSet for bulk actions"""
    serializer_class = BulkActionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BulkAction.objects.filter(user=self.request.user)
    
    def create(self, request):
        """Create and start a bulk action"""
        form_id = request.data.get('form_id')
        action_type = request.data.get('action_type')
        submission_ids = request.data.get('submission_ids')
        filter_criteria = request.data.get('filter_criteria')
        action_params = request.data.get('action_params', {})
        
        bulk_action = BulkActionService.create_bulk_action(
            form_id=form_id,
            user_id=str(request.user.id),
            action_type=action_type,
            submission_ids=submission_ids,
            filter_criteria=filter_criteria,
            action_params=action_params
        )
        
        serializer = self.get_serializer(bulk_action)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get bulk action progress"""
        progress = BulkActionService.get_bulk_action_progress(pk)
        return Response(progress)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a bulk action"""
        success = BulkActionService.cancel_bulk_action(pk)
        return Response({'cancelled': success})


class SpamDetectionConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for spam detection configuration"""
    serializer_class = SpamDetectionConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SpamDetectionConfig.objects.filter(form__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get spam detection statistics"""
        config = self.get_object()
        days = int(request.query_params.get('days', 30))
        
        stats = SpamDetectionService.get_spam_statistics(
            str(config.form_id), days
        )
        
        return Response(stats)


class ExternalValidationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for external validation rules"""
    serializer_class = ExternalValidationRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExternalValidationRule.objects.filter(form__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate a field value"""
        form_id = request.data.get('form_id')
        field_id = request.data.get('field_id')
        value = request.data.get('value')
        
        result = ExternalValidationService.validate_field(
            form_id, field_id, value
        )
        
        return Response(result)


class FormTestSuiteViewSet(viewsets.ModelViewSet):
    """ViewSet for form test suites"""
    serializer_class = FormTestSuiteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FormTestSuite.objects.filter(form__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """Run test suite"""
        test_suite = self.get_object()
        sample_data = request.data.get('sample_data')
        
        test_run = FormTestingService.create_test_run(
            str(test_suite.id), sample_data
        )
        
        serializer = FormTestRunSerializer(test_run)
        return Response(serializer.data)


class FormTestRunViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for test runs (read-only)"""
    serializer_class = FormTestRunSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FormTestRun.objects.filter(
            test_suite__form__user=self.request.user
        )


class FormPreviewSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for form preview sessions"""
    serializer_class = FormPreviewSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FormPreviewSession.objects.filter(created_by=self.request.user)


class WorkflowPipelineViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow pipelines"""
    serializer_class = WorkflowPipelineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkflowPipeline.objects.filter(form__user=self.request.user)


class SubmissionWorkflowStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for submission workflow status"""
    serializer_class = SubmissionWorkflowStatusSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SubmissionWorkflowStatus.objects.filter(
            submission__form__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Transition to a new stage"""
        workflow_status = self.get_object()
        to_stage_id = request.data.get('to_stage_id')
        reason = request.data.get('reason', '')
        
        updated_status = WorkflowPipelineService.transition_stage(
            str(workflow_status.submission_id),
            to_stage_id,
            str(request.user.id),
            reason
        )
        
        serializer = self.get_serializer(updated_status)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Get kanban board view of submissions"""
        pipeline_id = request.query_params.get('pipeline_id')
        
        if not pipeline_id:
            return Response(
                {'error': 'pipeline_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pipeline = get_object_or_404(WorkflowPipeline, id=pipeline_id)
        stages = pipeline.stage_definitions.all()
        
        kanban_data = []
        for stage in stages:
            submissions = SubmissionWorkflowStatus.objects.filter(
                pipeline=pipeline,
                current_stage=stage
            ).select_related('submission', 'assigned_to')
            
            kanban_data.append({
                'stage': WorkflowStageSerializer(stage).data,
                'submissions': self.get_serializer(submissions, many=True).data,
                'count': submissions.count()
            })
        
        return Response(kanban_data)


class FormOptimizationRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for optimization recommendations"""
    serializer_class = FormOptimizationRecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FormOptimizationRecommendation.objects.filter(
            form__user=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate recommendations for a form"""
        form_id = request.data.get('form_id')
        
        recommendations = OptimizationService.generate_recommendations(form_id)
        serializer = self.get_serializer(recommendations, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply a recommendation"""
        recommendation = self.get_object()
        
        # Apply the changes to the form
        form = recommendation.form
        # Apply logic based on recommendation_type and changes_json
        
        recommendation.status = 'applied'
        recommendation.applied_at = timezone.now()
        recommendation.applied_by = request.user
        recommendation.save()
        
        return Response({'status': 'applied'})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a recommendation"""
        recommendation = self.get_object()
        recommendation.status = 'dismissed'
        recommendation.save()
        
        return Response({'status': 'dismissed'})


class ScheduledReportViewSet(viewsets.ModelViewSet):
    """ViewSet for scheduled reports"""
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ScheduledReport.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Manually trigger report generation"""
        scheduled_report = self.get_object()
        
        execution = ScheduledReportService.generate_report(str(scheduled_report.id))
        serializer = ReportExecutionSerializer(execution)
        
        return Response(serializer.data)


class SubmissionCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for submission comments"""
    serializer_class = SubmissionCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        submission_id = self.request.query_params.get('submission_id')
        queryset = SubmissionComment.objects.filter(
            submission__form__user=self.request.user
        )
        
        if submission_id:
            queryset = queryset.filter(submission_id=submission_id)
        
        return queryset.select_related('user').prefetch_related('mentioned_users')
    
    def create(self, request):
        """Create a new comment"""
        submission_id = request.data.get('submission_id')
        comment_text = request.data.get('comment')
        parent_id = request.data.get('parent_id')
        is_internal = request.data.get('is_internal', True)
        
        comment = SubmissionCommentService.add_comment(
            submission_id=submission_id,
            user_id=str(request.user.id),
            comment=comment_text,
            parent_id=parent_id,
            is_internal=is_internal
        )
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubmissionNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for submission notes"""
    serializer_class = SubmissionNoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SubmissionNote.objects.filter(user=self.request.user)


class CustomFormTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for custom form templates"""
    serializer_class = CustomFormTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CustomFormTemplate.objects.filter(
            models.Q(created_by=self.request.user) |
            models.Q(is_public=True) |
            models.Q(team__members=self.request.user)
        ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Add template to favorites"""
        template = self.get_object()
        
        favorite, created = TemplateFavorite.objects.get_or_create(
            user=request.user,
            template=template
        )
        
        return Response({'favorited': created})
    
    @action(detail=True, methods=['delete'])
    def unfavorite(self, request, pk=None):
        """Remove template from favorites"""
        template = self.get_object()
        
        deleted_count, _ = TemplateFavorite.objects.filter(
            user=request.user,
            template=template
        ).delete()
        
        return Response({'unfavorited': deleted_count > 0})
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Create a form from this template"""
        template = self.get_object()
        new_title = request.data.get('title', f"Form from {template.name}")
        
        from forms.models import Form
        form = Form.objects.create(
            user=request.user,
            title=new_title,
            schema_json=template.schema_json,
            status='draft'
        )
        
        # Update usage count
        template.usage_count += 1
        template.save()
        
        from forms.serializers import FormSerializer
        return Response(FormSerializer(form).data, status=status.HTTP_201_CREATED)


class FormCloneViewSet(viewsets.ModelViewSet):
    """ViewSet for form cloning"""
    serializer_class = FormCloneSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FormClone.objects.filter(cloned_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def clone(self, request):
        """Clone a form"""
        original_form_id = request.data.get('form_id')
        new_title = request.data.get('title')
        include_logic = request.data.get('include_logic', True)
        include_integrations = request.data.get('include_integrations', False)
        include_styling = request.data.get('include_styling', True)
        include_settings = request.data.get('include_settings', True)
        
        cloned_form = FormCloningService.clone_form(
            original_form_id=original_form_id,
            user_id=str(request.user.id),
            new_title=new_title,
            include_logic=include_logic,
            include_integrations=include_integrations,
            include_styling=include_styling,
            include_settings=include_settings
        )
        
        from forms.serializers import FormSerializer
        return Response(FormSerializer(cloned_form).data, status=status.HTTP_201_CREATED)
