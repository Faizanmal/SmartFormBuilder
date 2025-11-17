"""
URL patterns for users app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TeamViewSet, APIKeyViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'api-keys', APIKeyViewSet, basename='apikey')

urlpatterns = [
    path('', include(router.urls)),
]
