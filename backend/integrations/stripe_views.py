"""
Views for Stripe webhooks and checkout
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from integrations.services.stripe_service import (
    create_checkout_session,
    create_subscription_checkout,
    handle_webhook_event,
    process_payment_success,
    process_subscription_created,
    process_subscription_updated,
    process_subscription_deleted,
    get_subscription_portal_url,
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_checkout(request):
    """Create Stripe Checkout session for form payment"""
    from forms.models import Form
    
    form_id = request.data.get('form_id')
    submission_data = request.data.get('submission_data')
    success_url = request.data.get('success_url')
    cancel_url = request.data.get('cancel_url')
    
    try:
        form = Form.objects.get(id=form_id)
        
        session = create_checkout_session(
            form=form,
            submission_data=submission_data,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return Response({
            'checkout_url': session.url,
            'session_id': session.id
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription_session(request):
    """Create Stripe Checkout session for subscription upgrade"""
    
    price_id = request.data.get('price_id')
    success_url = request.data.get('success_url')
    cancel_url = request.data.get('cancel_url')
    
    try:
        session = create_subscription_checkout(
            user=request.user,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return Response({
            'checkout_url': session.url,
            'session_id': session.id
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portal_session(request):
    """Get Stripe Customer Portal session URL"""
    
    return_url = request.query_params.get('return_url', 'http://localhost:3000/dashboard')
    
    try:
        portal_url = get_subscription_portal_url(request.user, return_url)
        
        return Response({
            'portal_url': portal_url
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = handle_webhook_event(payload, sig_header)
    except ValueError as e:
        return HttpResponse(str(e), status=400)
    
    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object
        
        if session.mode == 'payment':
            # Payment for form submission
            process_payment_success(session)
        elif session.mode == 'subscription':
            # New subscription
            subscription = session.subscription
            if subscription:
                import stripe
                subscription_obj = stripe.Subscription.retrieve(subscription)
                process_subscription_created(subscription_obj)
    
    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        process_subscription_updated(subscription)
    
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        process_subscription_deleted(subscription)
    
    elif event.type == 'invoice.payment_failed':
        # Handle failed payment
        pass
    
    return HttpResponse(status=200)
