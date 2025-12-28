"""
URL patterns for forms app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    FormViewSet, FormGenerateView, SubmissionViewSet,
    PublicSubmissionView, FormTemplateViewSet, NotificationConfigViewSet,
    FormDraftView, PublicFormView
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
    # Public form endpoint (no auth)
    path('public/form/<slug:slug>/', PublicFormView.as_view({'get': 'retrieve'}), name='public-form'),
    # Form draft endpoints (no auth - save & resume)
    path('public/draft/<slug:form_slug>/', FormDraftView.as_view({'post': 'create'}), name='public-draft-create'),
    path('public/draft/token/<str:draft_token>/', FormDraftView.as_view({'get': 'retrieve'}), name='public-draft-get'),
    path('public/draft/token/<str:draft_token>/send-link/', FormDraftView.as_view({'post': 'send_resume_link'}), name='public-draft-send-link'),
    
    # New advanced features
    path('advanced/', include('forms.urls_advanced')),
    path('advanced/', include('forms.urls_advanced_new')),
    path('features/', include('forms.urls_features')),
    path('automation/', include('forms.urls_automation')),
    path('new-features/', include('forms.urls_new_features')),
]
