"""
WebSocket routing for real-time collaboration
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/form/(?P<form_id>[0-9a-f-]+)/$', consumers.FormCollaborationConsumer.as_asgi()),
]
