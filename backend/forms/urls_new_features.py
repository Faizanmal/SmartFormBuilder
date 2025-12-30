"""
URL routing for new advanced features
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from forms.views_new_features import *

router = DefaultRouter()

# Field Dependencies & Auto-Population
router.register(r'field-dependencies', FieldDependencyViewSet, basename='field-dependency')
router.register(r'external-api-providers', viewsets.ModelViewSet, basename='external-api-provider')

# Bulk Actions
router.register(r'bulk-actions', BulkActionViewSet, basename='bulk-action')

# Spam Detection
# router.register(r'spam-configs', SpamDetectionConfigViewSet, basename='spam-config')

# External Validation
router.register(r'validation-rules', ExternalValidationRuleViewSet, basename='validation-rule')

# Form Testing
router.register(r'test-suites', FormTestSuiteViewSet, basename='test-suite')
router.register(r'test-runs', FormTestRunViewSet, basename='test-run')
router.register(r'preview-sessions', FormPreviewSessionViewSet, basename='preview-session')

# Workflow Pipeline
router.register(r'workflow-pipelines', WorkflowPipelineViewSet, basename='workflow-pipeline')
router.register(r'submission-workflow-status', SubmissionWorkflowStatusViewSet, basename='submission-workflow')

# Optimization Recommendations
# router.register(r'optimization-recommendations', FormOptimizationRecommendationViewSet, basename='optimization-recommendation')

# Scheduled Reports
# router.register(r'scheduled-reports', ScheduledReportViewSet, basename='scheduled-report')

# Submission Comments
router.register(r'submission-comments', SubmissionCommentViewSet, basename='submission-comment')
router.register(r'submission-notes', SubmissionNoteViewSet, basename='submission-note')

# Form Cloning & Templates
router.register(r'form-templates', CustomFormTemplateViewSet, basename='form-template')
router.register(r'form-clones', FormCloneViewSet, basename='form-clone')

urlpatterns = [
    path('', include(router.urls)),
]
