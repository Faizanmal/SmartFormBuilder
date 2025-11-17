"""
Rate limiting middleware for FormForge API endpoints.
Protects against abuse and ensures fair usage.
"""

from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import time
import hashlib


class RateLimitMiddleware:
    """
    Rate limiting middleware using Django cache backend.
    
    Limits:
    - Public submission endpoint: 10 requests per minute per IP
    - API endpoints (authenticated): 100 requests per minute per user
    - Unauthenticated API: 30 requests per minute per IP
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if rate limiting should apply
        if not self._should_rate_limit(request):
            return self.get_response(request)

        # Get rate limit configuration based on endpoint
        limit, window = self._get_rate_limit_config(request)
        
        # Generate cache key
        cache_key = self._get_cache_key(request)
        
        # Get current request count
        current = cache.get(cache_key, {'count': 0, 'reset_at': time.time() + window})
        
        # Reset if window expired
        if time.time() >= current['reset_at']:
            current = {'count': 0, 'reset_at': time.time() + window}
        
        # Check if limit exceeded
        if current['count'] >= limit:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Please try again in {int(current["reset_at"] - time.time())} seconds.',
                'retry_after': int(current['reset_at'] - time.time())
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Increment counter
        current['count'] += 1
        cache.set(cache_key, current, timeout=window)
        
        # Add rate limit headers to response
        response = self.get_response(request)
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(limit - current['count'])
        response['X-RateLimit-Reset'] = str(int(current['reset_at']))
        
        return response

    def _should_rate_limit(self, request):
        """Determine if request should be rate limited."""
        # Skip rate limiting for:
        # - Static files
        # - Admin panel
        # - Health check endpoints
        path = request.path
        
        if path.startswith('/static/') or path.startswith('/media/'):
            return False
        if path.startswith('/admin/'):
            return False
        if path == '/health/' or path == '/api/health/':
            return False
            
        return True

    def _get_rate_limit_config(self, request):
        """Get rate limit and time window based on endpoint and user."""
        path = request.path
        
        # Public form submission - strict limit
        if '/api/public/submit/' in path:
            return (10, 60)  # 10 requests per minute
        
        # Authenticated API requests - generous limit
        if request.user and request.user.is_authenticated:
            return (100, 60)  # 100 requests per minute
        
        # Unauthenticated API - moderate limit
        if path.startswith('/api/'):
            return (30, 60)  # 30 requests per minute
        
        # Public pages - generous limit
        return (60, 60)  # 60 requests per minute

    def _get_cache_key(self, request):
        """Generate cache key for rate limiting."""
        # Use user ID for authenticated requests
        if request.user and request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            # Use IP address for anonymous requests
            identifier = f"ip:{self._get_client_ip(request)}"
        
        # Include path to separate limits per endpoint type
        endpoint_type = self._get_endpoint_type(request.path)
        
        # Create hash for cache key
        key_string = f"ratelimit:{identifier}:{endpoint_type}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _get_endpoint_type(self, path):
        """Categorize endpoint for rate limiting."""
        if '/api/public/submit/' in path:
            return 'submit'
        elif '/api/auth/' in path:
            return 'auth'
        elif path.startswith('/api/'):
            return 'api'
        else:
            return 'public'


class SubmissionRateLimiter:
    """
    Specialized rate limiter for form submissions with per-form limits.
    Can be used as a decorator or called directly in views.
    """
    
    @staticmethod
    def check_limit(form_slug: str, ip_address: str) -> tuple[bool, int]:
        """
        Check if submission is within rate limits for this form/IP.
        
        Returns:
            tuple: (is_allowed, retry_after_seconds)
        """
        # Per-form, per-IP limit: 3 submissions per 5 minutes
        cache_key = f"submission_limit:{form_slug}:{ip_address}"
        window = 300  # 5 minutes
        limit = 3
        
        current = cache.get(cache_key, {'count': 0, 'reset_at': time.time() + window})
        
        # Reset if window expired
        if time.time() >= current['reset_at']:
            current = {'count': 0, 'reset_at': time.time() + window}
        
        # Check limit
        if current['count'] >= limit:
            retry_after = int(current['reset_at'] - time.time())
            return False, retry_after
        
        # Increment and save
        current['count'] += 1
        cache.set(cache_key, current, timeout=window)
        
        return True, 0

    @staticmethod
    def get_client_ip(request) -> str:
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '0.0.0.0'
