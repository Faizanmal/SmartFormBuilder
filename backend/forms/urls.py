"""
URL patterns for forms app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    FormViewSet, FormGenerateView, SubmissionViewSet,
    PublicSubmissionView, FormTemplateViewSet, NotificationConfigViewSet
)

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='form')
router.register(r'templates', FormTemplateViewSet, basename='template')
router.register(r'generate', FormGenerateView, basename='generate')

# Nested router for form submissions
forms_router = routers.NestedDefaultRouter(router, r'forms', lookup='form')
forms_router.register(r'submissions', SubmissionViewSet, basename='form-submissions')
forms_router.register(r'notifications', NotificationConfigViewSet, basename='form-notifications')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(forms_router.urls)),
    # Public submission endpoint (no auth)
    path('public/submit/<slug:form_slug>/', PublicSubmissionView.as_view({'post': 'create'}), name='public-submit'),
]
