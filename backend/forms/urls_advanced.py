"""
URL routing for advanced form features
"""
from django.urls import path, include
from rest_framework_nested import routers
from .views_advanced import (
    FormStepViewSet, PartialSubmissionViewSet, FormABTestViewSet,
    FormCommentViewSet, FormShareViewSet,
    FormAnalyticsViewSet, LeadScoreViewSet, AutomatedFollowUpViewSet,
    WhiteLabelConfigViewSet, AuditLogViewSet
)
from .views_conversational import ConversationalFormViewSet, ReportingViewSet

router = routers.DefaultRouter()

# Advanced features
router.register(r'partial-submissions', PartialSubmissionViewSet, basename='partial-submission')
router.register(r'ab-tests', FormABTestViewSet, basename='ab-test')
router.register(r'form-shares', FormShareViewSet, basename='form-share')
router.register(r'lead-scores', LeadScoreViewSet, basename='lead-score')
router.register(r'follow-ups', AutomatedFollowUpViewSet, basename='follow-up')
router.register(r'white-label', WhiteLabelConfigViewSet, basename='white-label')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'conversational', ConversationalFormViewSet, basename='conversational')
router.register(r'reports', ReportingViewSet, basename='report')

# Form-specific resources (using query parameters instead of nested routing)
router.register(r'form-steps', FormStepViewSet, basename='form-step')
router.register(r'form-comments', FormCommentViewSet, basename='form-comment')
router.register(r'form-analytics', FormAnalyticsViewSet, basename='form-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
