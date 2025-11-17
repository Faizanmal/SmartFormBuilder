"""
API Views for forms app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .models import Form, Submission, FormTemplate, FormVersion, NotificationConfig
from .serializers import (
    FormSerializer, FormCreateSerializer, SubmissionSerializer,
    SubmissionCreateSerializer, FormTemplateSerializer, FormGenerateSerializer,
    FormVersionSerializer, NotificationConfigSerializer, SubmissionExportSerializer
)
from .services.ai_service import FormGeneratorService
from .services.conditional_logic import ConditionalLogicEngine
from .services.export_service import SubmissionExporter
from .services.notification_service import NotificationService
from core.middleware.rate_limit import SubmissionRateLimiter


class FormViewSet(viewsets.ModelViewSet):
    """ViewSet for Form CRUD operations"""
    
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Form.objects.filter(user=self.request.user).select_related('user')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FormCreateSerializer
        return FormSerializer
    
    def perform_create(self, serializer):
        """Handle form creation with optional AI generation"""
        prompt = serializer.validated_data.pop('prompt', None)
        context = serializer.validated_data.pop('context', None)
        
        # If prompt is provided, generate schema using AI
        if prompt:
            ai_service = FormGeneratorService()
            try:
                schema = ai_service.generate_form_schema(prompt, context)
                serializer.validated_data['schema_json'] = schema
                serializer.validated_data['title'] = schema.get('title', serializer.validated_data.get('title', 'Untitled Form'))
                serializer.validated_data['description'] = schema.get('description', '')
                serializer.validated_data['settings_json'] = schema.get('settings', {})
            except Exception as e:
                return Response(
                    {'error': f'AI generation failed: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a form"""
        form = self.get_object()
        
        # Create version snapshot before publishing
        if form.status == 'draft':
            form.create_version()
        
        form.published_at = timezone.now()
        form.is_active = True
        form.status = 'published'
        form.save()
        return Response({'status': 'published', 'published_at': form.published_at, 'version': form.version})
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get version history for a form"""
        form = self.get_object()
        versions = form.versions.all()
        serializer = FormVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def revert(self, request, pk=None):
        """Revert form to a specific version"""
        form = self.get_object()
        version_id = request.data.get('version_id')
        
        if not version_id:
            return Response({'error': 'version_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        version = get_object_or_404(FormVersion, id=version_id, form=form)
        
        # Save current state as new version before reverting
        form.create_version()
        
        # Revert to selected version
        form.schema_json = version.schema_json
        form.settings_json = version.settings_json
        form.save()
        
        return Response({'status': 'reverted', 'version': form.version})
        form = self.get_object()
        form.published_at = timezone.now()
        form.is_active = True
        form.save()
        return Response({'status': 'published', 'published_at': form.published_at})
    
    @action(detail=True, methods=['get'])
    def embed(self, request, pk=None):
        """Get embed code for form"""
        form = self.get_object()
        embed_code = f'''<script defer src="https://cdn.formforge.io/embed.js"></script>
<div id="formforge-embed" data-form-slug="{form.slug}"></div>
<script>
  FormForge.init({{ selector: '#formforge-embed', slug: '{form.slug}', apiKey: 'YOUR_PUBLIC_KEY' }});
</script>'''
        
        hosted_link = f"https://forms.formforge.io/{form.slug}"
        
        return Response({
            'embed_code': embed_code,
            'hosted_link': hosted_link,
            'slug': form.slug
        })
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for form"""
        form = self.get_object()
        
        # Get submission stats by day (last 30 days)
        from django.db.models import Count
        from django.utils import timezone
class SubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Submission operations"""
    
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        form_id = self.kwargs.get('form_pk')
        if form_id:
            form = get_object_or_404(Form, id=form_id, user=self.request.user)
            return Submission.objects.filter(form=form)
        return Submission.objects.filter(form__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def export(self, request, form_pk=None):
        """Export submissions to CSV, JSON, or XLSX"""
        form = get_object_or_404(Form, id=form_pk, user=request.user)
        
        serializer = SubmissionExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        export_format = serializer.validated_data.get('format', 'csv')
        date_from = serializer.validated_data.get('date_from')
        date_to = serializer.validated_data.get('date_to')
        fields = serializer.validated_data.get('fields')
        
        # Query submissions
        queryset = Submission.objects.filter(form=form)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Flatten submissions
        submissions = [SubmissionExporter.flatten_submission(s) for s in queryset]
        
        # Export based on format
        if export_format == 'csv':
            csv_data = SubmissionExporter.to_csv(submissions, fields)
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{form.slug}_submissions.csv"'
            return response
        
        elif export_format == 'json':
            json_data = SubmissionExporter.to_json(submissions)
            response = HttpResponse(json_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{form.slug}_submissions.json"'
            return response
        
        elif export_format == 'xlsx':
            try:
                xlsx_data = SubmissionExporter.to_xlsx(submissions, fields)
                response = HttpResponse(
                    xlsx_data,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{form.slug}_submissions.xlsx"'
                return response
            except ImportError:
                return Response(
                    {'error': 'XLSX export requires openpyxl. Please install it.'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
        
        return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)


class FormGenerateView(viewsets.GenericViewSet):
    """ViewSet for AI form generation"""
    
    serializer_class = FormGenerateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Generate form schema from natural language description"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        prompt = serializer.validated_data['prompt']
        context = serializer.validated_data.get('context', '')
        
        ai_service = FormGeneratorService()
        
        try:
            schema = ai_service.generate_form_schema(prompt, context)
            return Response(schema, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Submission operations"""
    
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        form_id = self.kwargs.get('form_pk')
        if form_id:
            form = get_object_or_404(Form, id=form_id, user=self.request.user)
            return Submission.objects.filter(form=form)
        return Submission.objects.filter(form__user=self.request.user)


class PublicSubmissionView(viewsets.GenericViewSet):
    """Public API for form submissions (no auth required)"""
    
    serializer_class = SubmissionCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, form_slug=None):
        """Accept form submission from public"""
        form = get_object_or_404(Form, slug=form_slug, is_active=True)
        
        # Check rate limit for this form/IP combination
        ip_address = self.get_client_ip(request)
        is_allowed, retry_after = SubmissionRateLimiter.check_limit(form_slug, ip_address)
        
        if not is_allowed:
            return Response({
                'error': 'Rate limit exceeded',
                'message': f'Too many submissions. Please try again in {retry_after} seconds.',
                'retry_after': retry_after
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payload = serializer.validated_data['payload']
        
        # Validate submission with conditional logic
        is_valid, errors = ConditionalLogicEngine.validate_submission(
            form.schema_json,
            payload
        )
        
        if not is_valid:
            return Response({
                'error': 'Validation failed',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        # Create submission
        submission = Submission.objects.create(
            form=form,
            payload_json=payload,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Increment form submission count
        form.submissions_count += 1
        form.save(update_fields=['submissions_count'])
        
        # Send notifications
        try:
            NotificationService.process_submission_notifications(submission, form)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Notification failed: {e}")
        
        # Trigger integrations (sync to Google Sheets, email, etc.)
        from integrations.services.sync_service import sync_submission_to_integrations
        try:
            sync_submission_to_integrations(submission)
        except Exception as e:
            # Log error but don't fail the submission
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Integration sync failed: {e}")
        
        return Response({
            'id': submission.id,
            'message': 'Submission received successfully',
            'redirect': form.settings_json.get('redirect', '')
        }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class FormTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for FormTemplate (read-only)"""
    
    serializer_class = FormTemplateSerializer
    permission_classes = [IsAuthenticated]
    queryset = FormTemplate.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Create a new form from template"""
        template = self.get_object()
        
        # Create form from template
        form = Form.objects.create(
            user=request.user,
            title=f"{template.name} (Copy)",
            description=template.description,
            schema_json=template.schema_json,
            settings_json={}
        )
        
        # Increment template usage count
        template.usage_count += 1
        template.save(update_fields=['usage_count'])
        
        return Response(FormSerializer(form).data, status=status.HTTP_201_CREATED)


class NotificationConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for NotificationConfig CRUD"""
    
    serializer_class = NotificationConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        form_id = self.kwargs.get('form_pk')
        if form_id:
            form = get_object_or_404(Form, id=form_id, user=self.request.user)
            return NotificationConfig.objects.filter(form=form)
        return NotificationConfig.objects.filter(form__user=self.request.user)
    
    def perform_create(self, serializer):
        form_id = self.kwargs.get('form_pk')
        form = get_object_or_404(Form, id=form_id, user=self.request.user)
        serializer.save(form=form)
