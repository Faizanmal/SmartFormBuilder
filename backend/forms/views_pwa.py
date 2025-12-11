"""
Views for PWA, SMS, and push notification features
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from forms.services.sms_service import SMSService, SMSNotificationPreferences


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_push(request):
    """Subscribe to push notifications"""
    subscription = request.data.get('subscription')
    
    if not subscription:
        return Response({'error': 'Subscription data required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Store subscription in user profile or separate model
    # For now, we'll just acknowledge
    # In production, store this in a PushSubscription model
    
    return Response({
        'message': 'Subscribed successfully',
        'subscription': subscription
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_push(request):
    """Unsubscribe from push notifications"""
    endpoint = request.data.get('endpoint')
    
    if not endpoint:
        return Response({'error': 'Endpoint required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Remove subscription from database
    # PushSubscription.objects.filter(endpoint=endpoint, user=request.user).delete()
    
    return Response({'message': 'Unsubscribed successfully'})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def sms_settings(request):
    """Get or update SMS notification settings"""
    
    if request.method == 'GET':
        # Get current settings
        preferences = SMSNotificationPreferences.get_preferences(request.user)
        return Response(preferences)
    
    elif request.method == 'PATCH':
        # Update settings
        enabled = request.data.get('enabled')
        phone_number = request.data.get('phone_number')
        
        user = request.user
        
        if enabled is not None:
            user.sms_notifications_enabled = enabled
        
        if phone_number is not None:
            # Validate phone number
            sms_service = SMSService()
            validation = sms_service.validate_phone_number(phone_number)
            
            if not validation.get('valid'):
                return Response({
                    'error': 'Invalid phone number',
                    'details': validation.get('error')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.phone_number = validation['formatted']
        
        user.save()
        
        return Response({
            'message': 'Settings updated successfully',
            'enabled': user.sms_notifications_enabled,
            'phone_number': user.phone_number
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_sms(request):
    """Send a test SMS to verify configuration"""
    
    phone_number = request.data.get('phone_number') or request.user.phone_number
    
    if not phone_number:
        return Response({'error': 'Phone number required'}, status=status.HTTP_400_BAD_REQUEST)
    
    sms_service = SMSService()
    message_sid = sms_service.send_sms(
        phone_number,
        "This is a test message from SmartFormBuilder. Your SMS notifications are working!"
    )
    
    if message_sid:
        return Response({
            'message': 'Test SMS sent successfully',
            'sid': message_sid
        })
    else:
        return Response({
            'error': 'Failed to send SMS'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_sms_notification(request):
    """Send SMS notification (for form owners)"""
    
    form_id = request.data.get('form_id')
    recipients = request.data.get('recipients', [])
    message = request.data.get('message')
    
    if not form_id or not recipients or not message:
        return Response({
            'error': 'form_id, recipients, and message required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify user owns the form
    from forms.models import Form
    form = get_object_or_404(Form, id=form_id, created_by=request.user)
    
    sms_service = SMSService()
    results = sms_service.send_bulk_sms(recipients, message)
    
    return Response({
        'sent': results['sent'],
        'failed': results['failed'],
        'errors': results['errors']
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def pwa_health(request):
    """Health check endpoint for PWA"""
    return Response({'status': 'ok', 'timestamp': 'now'})


@api_view(['POST'])
def handle_sms_webhook(request):
    """Handle incoming SMS replies from Twilio"""
    
    # Twilio webhook payload
    from_number = request.POST.get('From')
    body = request.POST.get('Body')
    message_sid = request.POST.get('MessageSid')
    
    # Process the incoming message
    # You could implement auto-responses, commands, etc.
    
    # Example: respond to incoming SMS
    from twilio.twiml.messaging_response import MessagingResponse
    
    response = MessagingResponse()
    response.message("Thank you for your message! We'll get back to you soon.")
    
    return Response(str(response), content_type='application/xml')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def offline_sync_status(request):
    """Get sync status for offline submissions"""
    
    # This would check for any pending submissions
    # that were created offline and need syncing
    
    return Response({
        'pending_count': 0,
        'last_sync': None,
        'sync_enabled': True
    })
