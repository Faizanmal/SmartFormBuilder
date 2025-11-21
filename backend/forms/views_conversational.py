"""
Additional advanced views for conversational forms and reporting
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
import uuid

from forms.models import Form
from forms.models_advanced import ConversationalSession, ScheduledReport
from forms.serializers_advanced import ConversationalSessionSerializer, ScheduledReportSerializer
from forms.services.conversational_service import ConversationalFormService
from forms.services.voice_service import VoiceInputService
from forms.services.reporting_service import ReportingService


class ConversationalFormViewSet(viewsets.ModelViewSet):
    """ViewSet for conversational/chatbot-style forms"""
    
    queryset = ConversationalSession.objects.all()
    serializer_class = ConversationalSessionSerializer
    
    def get_permissions(self):
        # Allow anyone to start a conversation
        if self.action in ['create', 'respond', 'voice_input']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """Start a new conversational form session"""
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, id=form_id)
        
        # Create session
        session_token = str(uuid.uuid4())
        session = ConversationalSession.objects.create(
            form=form,
            session_token=session_token,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Generate first question
        conv_service = ConversationalFormService()
        form_schema = form.fields_schema
        
        next_question = conv_service.generate_next_question(
            form_schema,
            [],
            {}
        )
        
        return Response({
            'session_token': session_token,
            'session_id': str(session.id),
            'question': next_question,
            'form_title': form.title
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def respond(self, request):
        """Submit a response to the current question"""
        session_token = request.data.get('session_token')
        user_response = request.data.get('response')
        
        session = get_object_or_404(ConversationalSession, session_token=session_token)
        
        if session.is_complete:
            return Response({
                'error': 'This conversation is already complete'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse and validate response
        conv_service = ConversationalFormService()
        form_schema = session.form.fields_schema
        
        # Get current field info
        current_field = next(
            (f for f in form_schema.get('fields', []) if f['id'] == session.current_field_id),
            None
        )
        
        if current_field:
            try:
                # Parse user response
                parsed_value = conv_service.parse_user_response(
                    user_response,
                    current_field['type'],
                    current_field.get('options')
                )
                
                # Update collected data
                session.collected_data[session.current_field_id] = parsed_value
                
                # Add to conversation history
                session.conversation_history.append({
                    'question': current_field['label'],
                    'response': user_response,
                    'parsed_value': parsed_value,
                    'timestamp': timezone.now().isoformat()
                })
                
            except ValueError as e:
                return Response({
                    'error': str(e),
                    'retry': True
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate next question
        next_question = conv_service.generate_next_question(
            form_schema,
            session.conversation_history,
            session.collected_data
        )
        
        if next_question.get('complete'):
            # Form complete
            session.is_complete = True
            session.completed_at = timezone.now()
            
            # Create actual submission
            from forms.models import Submission
            submission = Submission.objects.create(
                form=session.form,
                payload_json=session.collected_data,
                ip_address=session.ip_address,
                user_agent=session.user_agent
            )
            
            # Generate summary
            summary = conv_service.generate_summary(form_schema, session.collected_data)
            
            session.save()
            
            return Response({
                'complete': True,
                'summary': summary,
                'submission_id': str(submission.id),
                'collected_data': session.collected_data
            })
        
        # Update session with current field
        session.current_field_id = next_question['field_id']
        session.save()
        
        return Response({
            'complete': False,
            'question': next_question,
            'progress': len(session.collected_data) / len(form_schema.get('fields', []))
        })
    
    @action(detail=False, methods=['post'])
    def voice_input(self, request):
        """Process voice input"""
        session_token = request.data.get('session_token')
        audio_data = request.data.get('audio_data')  # Base64 encoded
        audio_format = request.data.get('audio_format', 'webm')
        
        session = get_object_or_404(ConversationalSession, session_token=session_token)
        
        # Transcribe audio
        voice_service = VoiceInputService()
        try:
            transcribed_text = voice_service.transcribe_audio(audio_data, audio_format)
            
            # Check if it's a command
            command_result = voice_service.enable_voice_commands(audio_data)
            
            if command_result['command'] != 'input':
                return Response({
                    'command': command_result['command'],
                    'transcription': transcribed_text
                })
            
            # Process as regular input by calling respond
            request.data['response'] = transcribed_text
            return self.respond(request)
            
        except Exception as e:
            return Response({
                'error': f'Voice transcription failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def text_to_speech(self, request):
        """Convert question to speech"""
        text = request.data.get('text')
        voice = request.data.get('voice', 'alloy')
        
        voice_service = VoiceInputService()
        audio_data = voice_service.text_to_speech(text, voice)
        
        if audio_data:
            return Response({'audio_data': audio_data})
        else:
            return Response({
                'error': 'Text-to-speech conversion failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def session_history(self, request):
        """Get conversation history for a session"""
        session_token = request.query_params.get('session_token')
        session = get_object_or_404(ConversationalSession, session_token=session_token)
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ReportingViewSet(viewsets.ModelViewSet):
    """ViewSet for automated reporting"""
    
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter to user's forms
        user_forms = Form.objects.filter(created_by=self.request.user)
        return ScheduledReport.objects.filter(form__in=user_forms)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate an ad-hoc report"""
        form_id = request.data.get('form_id')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to', timezone.now().isoformat())
        report_type = request.data.get('report_type', 'summary')
        
        form = get_object_or_404(Form, id=form_id, created_by=request.user)
        
        # Parse dates
        from django.utils.dateparse import parse_datetime
        date_from_dt = parse_datetime(date_from)
        date_to_dt = parse_datetime(date_to)
        
        # Generate report
        report = ReportingService.generate_form_report(
            form,
            date_from_dt,
            date_to_dt,
            report_type
        )
        
        return Response(report)
    
    @action(detail=False, methods=['post'])
    def export_report(self, request):
        """Export report in various formats"""
        form_id = request.data.get('form_id')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to', timezone.now().isoformat())
        export_format = request.data.get('format', 'json')  # csv, json, tableau, powerbi
        
        form = get_object_or_404(Form, id=form_id, created_by=request.user)
        
        # Parse dates
        from django.utils.dateparse import parse_datetime
        date_from_dt = parse_datetime(date_from)
        date_to_dt = parse_datetime(date_to)
        
        # Generate report
        report = ReportingService.generate_form_report(form, date_from_dt, date_to_dt)
        
        # Export to format
        exported_data = ReportingService.export_to_bi_format(report, export_format)
        
        # Return as file download
        from django.http import HttpResponse
        
        if export_format == 'csv':
            response = HttpResponse(exported_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="report_{form.slug}.csv"'
        elif export_format in ['tableau', 'powerbi']:
            response = HttpResponse(exported_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="report_{form.slug}_{export_format}.json"'
        else:
            response = HttpResponse(exported_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="report_{form.slug}.json"'
        
        return response
    
    @action(detail=False, methods=['post'])
    def send_report_email(self, request):
        """Send report via email"""
        form_id = request.data.get('form_id')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to', timezone.now().isoformat())
        recipients = request.data.get('recipients', [])
        include_charts = request.data.get('include_charts', True)
        
        form = get_object_or_404(Form, id=form_id, created_by=request.user)
        
        # Parse dates
        from django.utils.dateparse import parse_datetime
        date_from_dt = parse_datetime(date_from)
        date_to_dt = parse_datetime(date_to)
        
        # Generate and send report
        report = ReportingService.generate_form_report(form, date_from_dt, date_to_dt)
        ReportingService.send_report_email(report, recipients, include_charts)
        
        return Response({
            'message': f'Report sent to {len(recipients)} recipients'
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle scheduled report active status"""
        scheduled_report = self.get_object()
        scheduled_report.is_active = not scheduled_report.is_active
        scheduled_report.save()
        
        serializer = self.get_serializer(scheduled_report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Manually trigger a scheduled report"""
        scheduled_report = self.get_object()
        
        # Calculate date range based on schedule type
        now = timezone.now()
        if scheduled_report.schedule_type == 'daily':
            date_from = now - timedelta(days=1)
        elif scheduled_report.schedule_type == 'weekly':
            date_from = now - timedelta(weeks=1)
        else:  # monthly
            date_from = now - timedelta(days=30)
        
        # Generate and send report
        report = ReportingService.generate_form_report(
            scheduled_report.form,
            date_from,
            now
        )
        ReportingService.send_report_email(
            report,
            scheduled_report.recipients,
            scheduled_report.report_options.get('include_charts', True)
        )
        
        # Update last run
        scheduled_report.last_run = now
        scheduled_report.save()
        
        return Response({
            'message': 'Report sent successfully',
            'sent_to': len(scheduled_report.recipients)
        })
