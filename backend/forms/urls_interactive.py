"""
URL Configuration for Interactive Features
"""
from django.urls import path
from . import views_interactive as views

urlpatterns = [
    # Collaboration
    path('collaboration/join/', views.join_collaboration, name='collaboration-join'),
    path('collaboration/leave/', views.leave_collaboration, name='collaboration-leave'),
    path('collaboration/sessions/<str:form_id>/', views.get_active_sessions, name='collaboration-sessions'),
    path('collaboration/message/', views.send_collaboration_message, name='collaboration-message'),
    path('collaboration/messages/<str:form_id>/', views.get_collaboration_messages, name='collaboration-messages'),
    path('collaboration/cursor/update/', views.update_cursor_position, name='collaboration-cursor'),
    
    # Gamification
    path('gamification/profile/', views.get_gamification_profile, name='gamification-profile'),
    path('gamification/award-points/', views.award_points, name='gamification-award-points'),
    path('gamification/unlock-achievement/', views.unlock_achievement, name='gamification-unlock-achievement'),
    path('gamification/leaderboard/', views.get_leaderboard, name='gamification-leaderboard'),
    path('gamification/update-streak/', views.update_streak, name='gamification-update-streak'),
    
    # Analytics
    path('analytics/forms/<str:form_id>/', views.get_form_analytics, name='analytics-form'),
    path('analytics/track/', views.track_analytics_event, name='analytics-track'),
    path('analytics/fields/<str:form_id>/<str:field_id>/', views.get_field_analytics, name='analytics-field'),
    path('analytics/export/<str:form_id>/', views.export_analytics, name='analytics-export'),
    
    # Workflows
    path('workflows/', views.list_workflows, name='workflow-list'),
    path('workflows/create/', views.create_workflow, name='workflow-create'),
    path('workflows/<pk>/', views.update_workflow, name='workflow-detail'),
    path('workflows/<pk>/update/', views.update_workflow, name='workflow-update'),
    path('workflows/<pk>/delete/', views.delete_workflow, name='workflow-delete'),
    path('workflows/<pk>/execute/', views.execute_workflow, name='workflow-execute'),
    path('workflows/<pk>/executions/', views.get_workflow_executions, name='workflow-executions'),
    
    # Voice
    path('voice/transcribe/', views.transcribe_voice, name='voice-transcribe'),
    path('voice/parse/', views.parse_voice_command, name='voice-parse'),
    
    # Chatbot
    path('chatbot/message/', views.send_chat_message, name='chatbot-message'),
    path('chatbot/suggestions/', views.get_chat_suggestions, name='chatbot-suggestions'),
    path('chatbot/feedback/', views.submit_chat_feedback, name='chatbot-feedback'),
    
    # Submissions
    path('forms/<str:form_id>/submit/', views.submit_form, name='form-submit'),
    path('submissions/<str:submission_id>/', views.get_submission, name='submission-detail'),
    path('submissions/', views.list_submissions, name='submission-list'),
    
    # Gesture Settings
    path('settings/gestures/', views.get_gesture_settings, name='gesture-settings-get'),
    path('settings/gestures/update/', views.update_gesture_settings, name='gesture-settings-update'),
    path('settings/gestures/track/', views.track_gesture_event, name='gesture-track'),
    
    # AR/VR
    path('ar/assets/', views.ARAssetViewSet.as_view({'get': 'list', 'post': 'create'}), name='ar-assets-list'),
    path('ar/assets/<str:pk>/', views.ARAssetViewSet.as_view({'delete': 'destroy'}), name='ar-assets-detail'),
    path('ar/preview/start/', views.start_ar_preview, name='ar-preview-start'),
    path('ar/preview/<str:preview_id>/end/', views.end_ar_preview, name='ar-preview-end'),
]
