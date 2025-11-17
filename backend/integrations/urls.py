"""
URL patterns for integrations app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import IntegrationViewSet, WebhookLogViewSet
from .stripe_views import (
    create_payment_checkout,
    create_subscription_session,
    get_portal_session,
    stripe_webhook
)

router = DefaultRouter()
router.register(r'', IntegrationViewSet, basename='integration')
router.register(r'webhook-logs', WebhookLogViewSet, basename='webhook-log')

urlpatterns = [
    path('', include(router.urls)),
    path('stripe/create-checkout/', create_payment_checkout, name='stripe-create-checkout'),
    path('stripe/create-subscription/', create_subscription_session, name='stripe-create-subscription'),
    path('stripe/portal/', get_portal_session, name='stripe-portal'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]
