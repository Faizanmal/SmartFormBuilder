"""
URL routing for PWA features
"""
from django.urls import path
from .views_pwa import (
    subscribe_push,
    unsubscribe_push,
    sms_settings,
    send_test_sms,
    send_sms_notification,
    pwa_health,
    handle_sms_webhook,
    offline_sync_status,
)

urlpatterns = [
    path('push/subscribe/', subscribe_push, name='push-subscribe'),
    path('push/unsubscribe/', unsubscribe_push, name='push-unsubscribe'),
    path('sms/settings/', sms_settings, name='sms-settings'),
    path('sms/test/', send_test_sms, name='sms-test'),
    path('sms/send/', send_sms_notification, name='sms-send'),
    path('sms/webhook/', handle_sms_webhook, name='sms-webhook'),
    path('health/', pwa_health, name='pwa-health'),
    path('offline/sync-status/', offline_sync_status, name='offline-sync-status'),
]
