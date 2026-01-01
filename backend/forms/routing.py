"""
WebSocket routing for real-time collaboration and interactive features
"""
from django.urls import re_path
from . import consumers
from . import consumers_interactive

websocket_urlpatterns = [
    # Original form collaboration
    re_path(r'ws/form/(?P<form_id>[0-9a-f-]+)/$', consumers.FormCollaborationConsumer.as_asgi()),
    
    # Interactive features
    re_path(r'ws/collaboration/(?P<form_id>[0-9a-f-]+)/$', consumers_interactive.CollaborationConsumer.as_asgi()),
    re_path(r'ws/analytics/(?P<form_id>[0-9a-f-]+)/$', consumers_interactive.AnalyticsConsumer.as_asgi()),
    re_path(r'ws/workflow/(?P<workflow_id>[0-9a-f-]+)/$', consumers_interactive.WorkflowExecutionConsumer.as_asgi()),
]
