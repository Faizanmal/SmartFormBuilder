"""
Stripe payment integration service
"""
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(form, submission_data, success_url, cancel_url):
    """Create a Stripe Checkout session for form payment"""
    
    # Get payment field from form schema
    payment_field = next(
        (f for f in form.schema_json.get('fields', []) if f.get('type') == 'payment'),
        None
    )
    
    if not payment_field:
        raise ValueError("No payment field found in form")
    
    amount = payment_field.get('amount', 0)  # Amount in cents
    currency = payment_field.get('currency', 'usd')
    description = payment_field.get('label', 'Form Payment')
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': description,
                    'description': f"Payment for {form.title}",
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'form_id': str(form.id),
            'form_title': form.title,
            'submission_data': str(submission_data),
        }
    )
    
    return session


def create_subscription_checkout(user, price_id, success_url, cancel_url):
    """Create Stripe Checkout session for subscription"""
    
    # Get or create Stripe customer
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
            metadata={'user_id': str(user.id)}
        )
        user.stripe_customer_id = customer.id
        user.save(update_fields=['stripe_customer_id'])
    
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': str(user.id),
        }
    )
    
    return session


def create_payment_intent(amount, currency='usd', metadata=None):
    """Create a PaymentIntent for custom payment flows"""
    
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        metadata=metadata or {},
        automatic_payment_methods={'enabled': True},
    )
    
    return intent


def handle_webhook_event(payload, sig_header):
    """Handle and verify Stripe webhook events"""
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise ValueError("Invalid signature")
    
    return event


def process_payment_success(session):
    """Process successful payment from Checkout session"""
    from forms.models import Submission, Form
    
    metadata = session.metadata
    form_id = metadata.get('form_id')
    submission_data = metadata.get('submission_data')
    
    if form_id and submission_data:
        form = Form.objects.get(id=form_id)
        
        # Create submission with payment info
        import json
        submission = Submission.objects.create(
            form=form,
            payload_json=json.loads(submission_data),
            payment_status='paid',
            payment_id=session.payment_intent,
            payment_amount=session.amount_total,
        )
        
        return submission
    
    return None


def process_subscription_created(subscription):
    """Process new subscription creation"""
    from users.models import User
    
    customer_id = subscription.customer
    user = User.objects.filter(stripe_customer_id=customer_id).first()
    
    if user:
        user.stripe_subscription_id = subscription.id
        user.stripe_subscription_status = subscription.status
        
        # Update user plan based on subscription
        # Map price IDs to plan tiers
        price_id = subscription['items']['data'][0]['price']['id']
        plan_map = {
            settings.STRIPE_PRICE_STARTER: 'starter',
            settings.STRIPE_PRICE_PRO: 'pro',
            settings.STRIPE_PRICE_BUSINESS: 'business',
        }
        user.plan = plan_map.get(price_id, 'free')
        user.save()
    
    return user


def process_subscription_updated(subscription):
    """Process subscription updates"""
    from users.models import User
    
    customer_id = subscription.customer
    user = User.objects.filter(stripe_customer_id=customer_id).first()
    
    if user:
        user.stripe_subscription_status = subscription.status
        user.save(update_fields=['stripe_subscription_status'])
    
    return user


def process_subscription_deleted(subscription):
    """Process subscription cancellation"""
    from users.models import User
    
    customer_id = subscription.customer
    user = User.objects.filter(stripe_customer_id=customer_id).first()
    
    if user:
        user.stripe_subscription_id = None
        user.stripe_subscription_status = 'canceled'
        user.plan = 'free'
        user.save()
    
    return user


def get_subscription_portal_url(user, return_url):
    """Create Stripe Customer Portal session URL"""
    
    if not user.stripe_customer_id:
        raise ValueError("User does not have a Stripe customer ID")
    
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=return_url,
    )
    
    return session.url
