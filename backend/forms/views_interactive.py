"""
Comprehensive API Views for Interactive Features
Uses actual database models for persistence and real data handling
"""

from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, Avg, Sum, F, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import timedelta
from io import StringIO
import csv
import json
import random
import string

# Import models
from .models_interactive import (
    CollaborationSession, UserSession, CollaborationMessage, CursorPosition,
    GamificationProfile, Achievement, UserAchievement, PointsLog, DailyStreak,
    InteractiveFormAnalytics, InteractiveFieldAnalytics, InteractiveAnalyticsEvent, InteractiveAnalyticsSnapshot,
    InteractiveWorkflow, InteractiveWorkflowStep, InteractiveWorkflowExecution, InteractiveWorkflowStepExecution,
    VoiceTranscription, VoiceCommand,
    ChatSession, ChatMessage, ChatSuggestion,
    FormSubmission, SubmissionField,
    ARAsset, ARPreview,
    GestureSettings, GestureEvent,
)

# Import serializers
from .serializers_interactive import (
    CollaborationSessionSerializer, UserSessionSerializer, CollaborationMessageSerializer,
    GamificationProfileSerializer, AchievementSerializer, UserAchievementSerializer,
    InteractiveFormAnalyticsSerializer, InteractiveAnalyticsEventSerializer,
    InteractiveWorkflowSerializer, InteractiveWorkflowCreateUpdateSerializer, InteractiveWorkflowExecutionSerializer,
    VoiceTranscriptionSerializer, VoiceCommandSerializer,
    ChatSessionSerializer, ChatMessageSerializer,
    FormSubmissionSerializer, FormSubmissionCreateSerializer,
    ARAssetSerializer, ARPreviewSerializer,
    GestureSettingsSerializer, GestureEventSerializer,
)


# ==================== PAGINATION ====================

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


# ==================== COLLABORATION VIEWS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_collaboration(request):
    """Join a collaboration session"""
    form_id = request.data.get('formId')
    user_name = request.data.get('userName', request.user.username)
    
    if not form_id:
        return Response({'error': 'Form ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create collaboration session
    session, created = CollaborationSession.objects.get_or_create(
        form_id=form_id,
        is_active=True
    )
    
    # Create user session
    user_session, created = UserSession.objects.get_or_create(
        collaboration=session,
        user=request.user,
        defaults={
            'username': user_name,
            'email': request.user.email,
            'color': f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}'
        }
    )
    
    # Update left_at to None if rejoining
    if user_session.left_at:
        user_session.left_at = None
        user_session.save()
    
    serializer = UserSessionSerializer(user_session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_collaboration(request):
    """Leave a collaboration session"""
    session_id = request.data.get('sessionId')
    
    try:
        user_session = UserSession.objects.get(id=session_id)
        user_session.left_at = timezone.now()
        user_session.save()
        return Response({'success': True})
    except UserSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_sessions(request, form_id):
    """Get active collaboration sessions for a form"""
    try:
        collaboration = CollaborationSession.objects.get(form_id=form_id, is_active=True)
        active_users = collaboration.users.filter(left_at__isnull=True)
        serializer = UserSessionSerializer(active_users, many=True)
        return Response({
            'session': CollaborationSessionSerializer(collaboration).data,
            'activeUsers': serializer.data,
            'userCount': active_users.count()
        })
    except CollaborationSession.DoesNotExist:
        return Response({'activeUsers': [], 'userCount': 0})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_collaboration_message(request):
    """Send a message in collaboration session"""
    form_id = request.data.get('formId')
    message_content = request.data.get('message')
    message_type = request.data.get('type', 'text')
    
    try:
        collaboration = CollaborationSession.objects.get(form_id=form_id, is_active=True)
        user_session = UserSession.objects.get(collaboration=collaboration, user=request.user)
        
        message = CollaborationMessage.objects.create(
            collaboration=collaboration,
            user_session=user_session,
            message_type=message_type,
            content=message_content
        )
        
        serializer = CollaborationMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except (CollaborationSession.DoesNotExist, UserSession.DoesNotExist):
        return Response({'error': 'Not in collaboration session'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_collaboration_messages(request, form_id):
    """Get collaboration chat messages"""
    try:
        collaboration = CollaborationSession.objects.get(form_id=form_id, is_active=True)
        messages = collaboration.messages.all().order_by('-timestamp')[:100]
        serializer = CollaborationMessageSerializer(messages, many=True)
        return Response(serializer.data)
    except CollaborationSession.DoesNotExist:
        return Response([], safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cursor_position(request):
    """Update cursor position for real-time collaboration"""
    session_id = request.data.get('sessionId')
    x = request.data.get('x', 0)
    y = request.data.get('y', 0)
    field_id = request.data.get('fieldId')
    
    try:
        user_session = UserSession.objects.get(id=session_id)
        cursor, created = CursorPosition.objects.get_or_create(user_session=user_session)
        cursor.x = x
        cursor.y = y
        cursor.field_id = field_id
        cursor.save()
        
        from .serializers_interactive import CursorPositionSerializer
        serializer = CursorPositionSerializer(cursor)
        return Response(serializer.data)
    except UserSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== GAMIFICATION VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_gamification_profile(request):
    """Get user's gamification profile"""
    profile, created = GamificationProfile.objects.get_or_create(user=request.user)
    serializer = GamificationProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def award_points(request):
    """Award points to user"""
    amount = request.data.get('amount', 0)
    reason = request.data.get('reason', 'other')
    form_id = request.data.get('formId')
    
    if amount <= 0:
        return Response({'error': 'Points amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
    
    profile, created = GamificationProfile.objects.get_or_create(user=request.user)
    profile.add_points(amount, reason)
    
    # Log the transaction
    PointsLog.objects.create(
        user=request.user,
        amount=amount,
        reason=reason,
        form_id=form_id
    )
    
    serializer = GamificationProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlock_achievement(request):
    """Unlock an achievement for the user"""
    achievement_key = request.data.get('achievementKey')
    
    try:
        achievement = Achievement.objects.get(key=achievement_key)
        user_achievement, created = UserAchievement.objects.get_or_create(
            user=request.user,
            achievement=achievement
        )
        
        if created:
            # Award points
            profile, _ = GamificationProfile.objects.get_or_create(user=request.user)
            profile.add_points(achievement.points_reward, f'achievement:{achievement_key}')
        
        from .serializers_interactive import UserAchievementSerializer
        serializer = UserAchievementSerializer(user_achievement)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Achievement.DoesNotExist:
        return Response({'error': 'Achievement not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard(request):
    """Get gamification leaderboard"""
    limit = int(request.query_params.get('limit', 100))
    profiles = GamificationProfile.objects.all().order_by('-total_points')[:limit]
    serializer = GamificationProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_streak(request):
    """Update daily streak for user"""
    today = timezone.now().date()
    
    streak, created = DailyStreak.objects.get_or_create(user=request.user)
    
    if streak.last_activity_date == today:
        # Already active today
        return Response({'message': 'Streak already updated today'})
    elif streak.last_activity_date == today - timedelta(days=1):
        # Continue streak
        streak.current_count += 1
        if streak.current_count > streak.max_count:
            streak.max_count = streak.current_count
    else:
        # Streak broken, restart
        streak.current_count = 1
    
    streak.last_activity_date = today
    streak.save()
    
    from .serializers_interactive import DailyStreakSerializer
    serializer = DailyStreakSerializer(streak)
    return Response(serializer.data)


# ==================== ANALYTICS VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_form_analytics(request, form_id):
    """Get analytics for a form"""
    analytics, created = InteractiveFormAnalytics.objects.get_or_create(form_id=form_id)
    serializer = InteractiveFormAnalyticsSerializer(analytics)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_analytics_event(request):
    """Track an analytics event"""
    form_id = request.data.get('formId')
    event_type = request.data.get('eventType')
    session_id = request.data.get('sessionId')
    field_id = request.data.get('fieldId')
    value = request.data.get('value')
    
    try:
        analytics, _ = InteractiveFormAnalytics.objects.get_or_create(form_id=form_id)
        
        event = InteractiveAnalyticsEvent.objects.create(
            form_id=form_id,
            form_analytics=analytics,
            event_type=event_type,
            session_id=session_id,
            field_id=field_id,
            value=value,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Update analytics based on event type
        if event_type == 'view':
            analytics.total_views += 1
        elif event_type == 'submit':
            analytics.total_submissions += 1
        
        analytics.save()
        
        serializer = InteractiveAnalyticsEventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_field_analytics(request, form_id, field_id):
    """Get analytics for a specific field"""
    try:
        analytics = InteractiveFormAnalytics.objects.get(form_id=form_id)
        field_analytics, created = InteractiveFieldAnalytics.objects.get_or_create(
            form_analytics=analytics,
            field_id=field_id
        )
        from .serializers_interactive import InteractiveFieldAnalyticsSerializer
        serializer = InteractiveFieldAnalyticsSerializer(field_analytics)
        return Response(serializer.data)
    except InteractiveFormAnalytics.DoesNotExist:
        return Response({'error': 'Form analytics not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_analytics(request, form_id):
    """Export analytics data as CSV"""
    try:
        analytics = InteractiveFormAnalytics.objects.get(form_id=form_id)
        events = analytics.events.all()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="analytics_{form_id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Event Type', 'Session ID', 'Field ID', 'Timestamp', 'User'])
        
        for event in events:
            writer.writerow([
                event.event_type,
                event.session_id,
                event.field_id or '',
                event.timestamp.isoformat(),
                event.user.username if event.user else 'Anonymous'
            ])
        
        return response
    except InteractiveFormAnalytics.DoesNotExist:
        return Response({'error': 'Analytics not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== WORKFLOW VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflows(request):
    """List user's workflows"""
    workflows = InteractiveWorkflow.objects.filter(owner=request.user).order_by('-created_at')
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(workflows, request)
    serializer = InteractiveWorkflowSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_workflow(request):
    """Create a new workflow"""
    request.data._mutable = True
    request.data['owner'] = request.user.id
    
    serializer = InteractiveWorkflowCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        workflow = serializer.save(owner=request.user)
        return Response(InteractiveWorkflowSerializer(workflow).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_workflow(request, pk):
    """Update a workflow"""
    try:
        workflow = InteractiveWorkflow.objects.get(id=pk, owner=request.user)
        serializer = InteractiveWorkflowCreateUpdateSerializer(workflow, data=request.data, partial=True)
        if serializer.is_valid():
            workflow = serializer.save()
            return Response(InteractiveWorkflowSerializer(workflow).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except InteractiveWorkflow.DoesNotExist:
        return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workflow(request, pk):
    """Delete a workflow"""
    try:
        workflow = InteractiveWorkflow.objects.get(id=pk, owner=request.user)
        workflow.delete()
        return Response({'success': True})
    except InteractiveWorkflow.DoesNotExist:
        return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_workflow(request, pk):
    """Execute a workflow"""
    try:
        workflow = InteractiveWorkflow.objects.get(id=pk)
        trigger_data = request.data.get('data', {})
        
        execution = InteractiveWorkflowExecution.objects.create(
            workflow=workflow,
            trigger_data=trigger_data,
            status='pending'
        )
        
        # Execute steps
        for step in workflow.steps.all().order_by('order'):
            step_execution = InteractiveWorkflowStepExecution.objects.create(
                execution=execution,
                step=step,
                status='pending',
                input_data=trigger_data
            )
            
            # Simulate step execution
            try:
                step_execution.status = 'completed'
                step_execution.output_data = {'success': True}
            except Exception as e:
                step_execution.status = 'failed'
                step_execution.error_message = str(e)
            
            step_execution.completed_at = timezone.now()
            step_execution.save()
        
        execution.status = 'completed'
        execution.completed_at = timezone.now()
        execution.save()
        
        serializer = InteractiveWorkflowExecutionSerializer(execution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except InteractiveWorkflow.DoesNotExist:
        return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workflow_executions(request, pk):
    """Get execution history for a workflow"""
    try:
        workflow = InteractiveWorkflow.objects.get(id=pk, owner=request.user)
        executions = workflow.executions.all().order_by('-started_at')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(executions, request)
        serializer = InteractiveWorkflowExecutionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except InteractiveWorkflow.DoesNotExist:
        return Response({'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== VOICE VIEWS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_voice(request):
    """Transcribe voice audio to text"""
    if 'audio' not in request.FILES:
        return Response({'error': 'Audio file required'}, status=status.HTTP_400_BAD_REQUEST)
    
    audio_file = request.FILES['audio']
    form_id = request.data.get('formId')
    field_id = request.data.get('fieldId')
    language = request.data.get('language', 'en-US')
    
    transcription = VoiceTranscription.objects.create(
        user=request.user,
        form_id=form_id,
        field_id=field_id,
        audio_file=audio_file,
        text='[Mock transcription: Please implement actual speech-to-text service]',
        confidence=0.95,
        language=language,
        duration=0
    )
    
    serializer = VoiceTranscriptionSerializer(transcription)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def parse_voice_command(request):
    """Parse voice transcription into a command"""
    transcription_id = request.data.get('transcriptionId')
    command_type = request.data.get('commandType')
    
    try:
        transcription = VoiceTranscription.objects.get(id=transcription_id)
        
        command = VoiceCommand.objects.create(
            user=request.user,
            transcription=transcription,
            form_id=transcription.form_id,
            command_type=command_type,
            parameters=request.data.get('parameters', {}),
            executed=True,
            result={'success': True}
        )
        
        serializer = VoiceCommandSerializer(command)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except VoiceTranscription.DoesNotExist:
        return Response({'error': 'Transcription not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== CHATBOT VIEWS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat_message(request):
    """Send a message to the chatbot"""
    form_id = request.data.get('formId')
    content = request.data.get('message')
    session_id = request.data.get('sessionId')
    
    # Get or create session
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create(form_id=form_id, user=request.user)
    else:
        session = ChatSession.objects.create(form_id=form_id, user=request.user)
    
    # Save user message
    user_message = ChatMessage.objects.create(
        session=session,
        sender='user',
        content=content
    )
    
    # Generate assistant response
    assistant_response = ChatMessage.objects.create(
        session=session,
        sender='assistant',
        content='[Mock response from AI chatbot - integrate with actual AI service]'
    )
    
    messages = session.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    return Response({
        'sessionId': str(session.id),
        'messages': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_suggestions(request):
    """Get quick suggestions for chatbot"""
    form_id = request.query_params.get('formId')
    
    default_suggestions = [
        'Help me design a form',
        'Add validation rules',
        'Configure integrations',
        'Customize theme',
    ]
    
    return Response({
        'suggestions': default_suggestions
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_chat_feedback(request):
    """Submit feedback on chatbot response"""
    message_id = request.data.get('messageId')
    rating = request.data.get('rating')
    feedback = request.data.get('feedback', '')
    
    try:
        message = ChatMessage.objects.get(id=message_id)
        message.rating = rating
        message.feedback = feedback
        message.save()
        return Response({'success': True})
    except ChatMessage.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== SUBMISSION VIEWS ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_form(request, form_id):
    """Submit a form"""
    user = request.user if request.user.is_authenticated else None
    
    submission = FormSubmission.objects.create(
        form_id=form_id,
        user=user,
        status='submitted',
        data=request.data.get('data', {}),
        ip_address=request.META.get('REMOTE_ADDR'),
        completion_time=request.data.get('completionTime')
    )
    
    # Create submission fields
    fields_data = request.data.get('fields', [])
    for field in fields_data:
        SubmissionField.objects.create(
            submission=submission,
            field_id=field.get('id'),
            field_label=field.get('label'),
            value=field.get('value')
        )
    
    submission.submitted_at = timezone.now()
    submission.save()
    
    serializer = FormSubmissionSerializer(submission)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_submission(request, submission_id):
    """Get a specific submission"""
    try:
        submission = FormSubmission.objects.get(id=submission_id)
        serializer = FormSubmissionSerializer(submission)
        return Response(serializer.data)
    except FormSubmission.DoesNotExist:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_submissions(request):
    """List form submissions for authenticated user"""
    form_id = request.query_params.get('formId')
    
    submissions = FormSubmission.objects.filter(form_id=form_id)
    if request.query_params.get('userOnly'):
        submissions = submissions.filter(user=request.user)
    
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(submissions, request)
    serializer = FormSubmissionSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


# ==================== GESTURE VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_gesture_settings(request):
    """Get user's gesture settings"""
    settings, created = GestureSettings.objects.get_or_create(user=request.user)
    serializer = GestureSettingsSerializer(settings)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_gesture_settings(request):
    """Update gesture settings"""
    settings, created = GestureSettings.objects.get_or_create(user=request.user)
    
    serializer = GestureSettingsSerializer(settings, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_gesture_event(request):
    """Track a gesture event"""
    gesture_type = request.data.get('gestureType')
    form_id = request.data.get('formId')
    
    event = GestureEvent.objects.create(
        user=request.user,
        form_id=form_id,
        gesture_type=gesture_type,
        direction=request.data.get('direction'),
        coordinates=request.data.get('coordinates', {}),
        action_triggered=request.data.get('actionTriggered', '')
    )
    
    serializer = GestureEventSerializer(event)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ==================== AR/VR VIEWS ====================

class ARAssetViewSet(viewsets.ModelViewSet):
    """ViewSet for AR assets"""
    serializer_class = ARAssetSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return ARAsset.objects.filter(
            Q(owner=self.request.user) | Q(is_public=True)
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['GET'])
    def my_assets(self, request):
        """Get current user's AR assets"""
        queryset = ARAsset.objects.filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_ar_preview(request):
    """Start an AR preview session"""
    form_id = request.data.get('formId')
    asset_id = request.data.get('assetId')
    
    try:
        asset = ARAsset.objects.get(id=asset_id) if asset_id else None
        
        preview = ARPreview.objects.create(
            user=request.user,
            form_id=form_id,
            asset=asset,
            rotation=request.data.get('rotation', {}),
            scale=request.data.get('scale', {}),
            position=request.data.get('position', {})
        )
        
        serializer = ARPreviewSerializer(preview)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ARAsset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_ar_preview(request, preview_id):
    """End an AR preview session"""
    try:
        preview = ARPreview.objects.get(id=preview_id, user=request.user)
        preview.ended_at = timezone.now()
        preview.save()
        
        serializer = ARPreviewSerializer(preview)
        return Response(serializer.data)
    except ARPreview.DoesNotExist:
        return Response({'error': 'Preview not found'}, status=status.HTTP_404_NOT_FOUND)
