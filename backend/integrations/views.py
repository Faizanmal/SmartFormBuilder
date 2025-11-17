"""
API Views for integrations app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.conf import settings
import secrets

from .models import Integration, WebhookLog
from .serializers import IntegrationSerializer, WebhookLogSerializer
from .services.google_sheets import get_authorization_url, exchange_code_for_tokens


class IntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Integration operations"""
    
    serializer_class = IntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Integration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test an integration"""
        integration = self.get_object()
        
        # TODO: Implement test logic based on integration type
        
        return Response({
            'status': 'success',
            'message': f'Test {integration.get_type_display()} integration'
        })
    
    @action(detail=False, methods=['get'])
    def google_sheets_auth(self, request):
        """Initiate Google Sheets OAuth2 flow"""
        form_id = request.query_params.get('form_id')
        
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        request.session['oauth_form_id'] = form_id
        
        auth_url, _ = get_authorization_url(state)
        
        return Response({
            'authorization_url': auth_url,
            'state': state
        })
    
    @action(detail=False, methods=['post'])
    def google_sheets_connect(self, request):
        """Complete Google Sheets OAuth2 flow and create integration"""
        code = request.data.get('code')
        state = request.data.get('state')
        form_id = request.data.get('form_id')
        
        # Verify state token
        stored_state = request.session.get('oauth_state')
        if not stored_state or stored_state != state:
            return Response(
                {'error': 'Invalid state token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Exchange code for tokens
            credentials = exchange_code_for_tokens(code)
            
            # Create integration
            integration = Integration.objects.create(
                user=request.user,
                form_id=form_id if form_id else None,
                type='google_sheets',
                name='Google Sheets',
                status='active'
            )
            integration.set_config(credentials)
            integration.save()
            
            # Clear session
            request.session.pop('oauth_state', None)
            request.session.pop('oauth_form_id', None)
            
            return Response(IntegrationSerializer(integration).data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WebhookLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for WebhookLog (read-only)"""
    
    serializer_class = WebhookLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = WebhookLog.objects.filter(
            integration__user=self.request.user
        ).select_related('integration', 'submission')
        
        # Filter by integration if provided
        integration_id = self.request.query_params.get('integration')
        if integration_id:
            queryset = queryset.filter(integration_id=integration_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed webhook delivery"""
        webhook_log = self.get_object()
        
        if webhook_log.status not in ['failed']:
            return Response(
                {'error': 'Can only retry failed webhooks'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue retry task
        from integrations.tasks import deliver_webhook
        deliver_webhook.delay(str(webhook_log.id))
        
        return Response({
            'status': 'success',
            'message': 'Webhook retry queued'
        })
