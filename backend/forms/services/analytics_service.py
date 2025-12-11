"""
Form analytics and tracking service
"""
from django.db.models import Count
import user_agents


class FormAnalyticsService:
    """Service for tracking and analyzing form interactions"""
    
    @staticmethod
    def track_event(form, session_id, event_type, request, field_id=None, field_label=None, 
                    step_number=None, event_data=None):
        """Track a form interaction event"""
        from forms.models_advanced import FormAnalytics
        
        # Parse user agent
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        ua = user_agents.parse(user_agent_string)
        
        # Determine device type
        if ua.is_mobile:
            device_type = 'mobile'
        elif ua.is_tablet:
            device_type = 'tablet'
        else:
            device_type = 'desktop'
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get referrer
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Create analytics event
        event = FormAnalytics.objects.create(
            form=form,
            session_id=session_id,
            event_type=event_type,
            field_id=field_id or '',
            field_label=field_label or '',
            step_number=step_number,
            event_data=event_data or {},
            ip_address=ip_address,
            user_agent=user_agent_string[:500],
            device_type=device_type,
            browser=f"{ua.browser.family} {ua.browser.version_string}",
            referrer=referrer[:200] if referrer else '',
        )
        
        return event
    
    @staticmethod
    def get_field_analytics(form, date_from=None, date_to=None):
        """Get field-level analytics (focus, errors, completion time)"""
        from forms.models_advanced import FormAnalytics
        
        events = FormAnalytics.objects.filter(form=form)
        
        if date_from:
            events = events.filter(created_at__gte=date_from)
        if date_to:
            events = events.filter(created_at__lte=date_to)
        
        field_stats = {}
        
        # Group events by field
        field_events = events.exclude(field_id='').values('field_id', 'field_label', 'event_type').annotate(
            count=Count('id')
        )
        
        for event in field_events:
            field_id = event['field_id']
            if field_id not in field_stats:
                field_stats[field_id] = {
                    'label': event['field_label'],
                    'focus_count': 0,
                    'error_count': 0,
                    'blur_count': 0,
                }
            
            if event['event_type'] == 'field_focus':
                field_stats[field_id]['focus_count'] = event['count']
            elif event['event_type'] == 'field_error':
                field_stats[field_id]['error_count'] = event['count']
            elif event['event_type'] == 'field_blur':
                field_stats[field_id]['blur_count'] = event['count']
        
        # Calculate error rate for each field
        for field_id, stats in field_stats.items():
            if stats['focus_count'] > 0:
                stats['error_rate'] = round((stats['error_count'] / stats['focus_count']) * 100, 2)
            else:
                stats['error_rate'] = 0
        
        return field_stats
    
    @staticmethod
    def get_funnel_analytics(form, date_from=None, date_to=None):
        """Get conversion funnel data"""
        from forms.models_advanced import FormAnalytics
        
        events = FormAnalytics.objects.filter(form=form)
        
        if date_from:
            events = events.filter(created_at__gte=date_from)
        if date_to:
            events = events.filter(created_at__lte=date_to)
        
        # Count unique sessions at each stage
        views = events.filter(event_type='view').values('session_id').distinct().count()
        starts = events.filter(event_type='start').values('session_id').distinct().count()
        submits = events.filter(event_type='submit').values('session_id').distinct().count()
        
        # Calculate drop-off rates
        view_to_start_rate = (starts / views * 100) if views > 0 else 0
        start_to_submit_rate = (submits / starts * 100) if starts > 0 else 0
        overall_conversion = (submits / views * 100) if views > 0 else 0
        
        return {
            'views': views,
            'starts': starts,
            'submits': submits,
            'view_to_start_rate': round(view_to_start_rate, 2),
            'start_to_submit_rate': round(start_to_submit_rate, 2),
            'overall_conversion': round(overall_conversion, 2),
            'drop_off_at_start': views - starts,
            'drop_off_after_start': starts - submits,
        }
    
    @staticmethod
    def get_device_analytics(form, date_from=None, date_to=None):
        """Get analytics by device type"""
        from forms.models_advanced import FormAnalytics
        
        events = FormAnalytics.objects.filter(form=form, event_type='view')
        
        if date_from:
            events = events.filter(created_at__gte=date_from)
        if date_to:
            events = events.filter(created_at__lte=date_to)
        
        device_breakdown = events.values('device_type').annotate(count=Count('id'))
        
        total = sum(item['count'] for item in device_breakdown)
        
        return [
            {
                'device_type': item['device_type'],
                'count': item['count'],
                'percentage': round((item['count'] / total * 100), 2) if total > 0 else 0
            }
            for item in device_breakdown
        ]
    
    @staticmethod
    def get_geographic_analytics(form, date_from=None, date_to=None):
        """Get analytics by geography"""
        from forms.models_advanced import FormAnalytics
        
        events = FormAnalytics.objects.filter(form=form, event_type='view')
        
        if date_from:
            events = events.filter(created_at__gte=date_from)
        if date_to:
            events = events.filter(created_at__lte=date_to)
        
        country_breakdown = events.exclude(country='').values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        city_breakdown = events.exclude(city='').values('city', 'country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return {
            'top_countries': list(country_breakdown),
            'top_cities': list(city_breakdown),
        }
    
    @staticmethod
    def get_time_series_data(form, date_from=None, date_to=None, interval='day'):
        """Get time series data for views and submissions"""
        from forms.models_advanced import FormAnalytics
        from django.db.models.functions import TruncDate, TruncHour
        
        events = FormAnalytics.objects.filter(form=form)
        
        if date_from:
            events = events.filter(created_at__gte=date_from)
        if date_to:
            events = events.filter(created_at__lte=date_to)
        
        if interval == 'hour':
            truncate_func = TruncHour
        else:
            truncate_func = TruncDate
        
        # Views over time
        views_data = events.filter(event_type='view').annotate(
            period=truncate_func('created_at')
        ).values('period').annotate(count=Count('id')).order_by('period')
        
        # Submissions over time
        submissions_data = events.filter(event_type='submit').annotate(
            period=truncate_func('created_at')
        ).values('period').annotate(count=Count('id')).order_by('period')
        
        return {
            'views': list(views_data),
            'submissions': list(submissions_data),
        }
    
    @staticmethod
    def generate_heat_map_data(form, date_from=None, date_to=None):
        """Generate heat map data showing field engagement"""
        field_analytics = FormAnalyticsService.get_field_analytics(form, date_from, date_to)
        
        # Convert to heat map format
        heat_map = []
        for field_id, stats in field_analytics.items():
            heat_map.append({
                'field_id': field_id,
                'field_label': stats['label'],
                'engagement_score': stats['focus_count'],
                'error_rate': stats['error_rate'],
                'intensity': min(100, stats['focus_count'] / 10),  # Normalize to 0-100
            })
        
        return sorted(heat_map, key=lambda x: x['engagement_score'], reverse=True)
