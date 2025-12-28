"""
Advanced analytics, heatmaps, and session recording service
"""
from django.db.models import Avg, Count, Sum, F, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta
import logging
import math
from scipy import stats as scipy_stats

from forms.models_analytics import (
    FormHeatmapData, SessionRecording, SessionEvent,
    DropOffAnalysis, ABTestResult, BehaviorInsight,
    FormFunnel, FunnelStepMetric
)
from forms.models import Form, ABTest, FormVariant

logger = logging.getLogger(__name__)


class HeatmapService:
    """Service for heatmap data collection and analysis"""
    
    @classmethod
    def record_interaction(cls, form_id: str, data: dict):
        """Record a heatmap interaction"""
        today = timezone.now().date()
        
        # Try to aggregate with existing data point
        existing = FormHeatmapData.objects.filter(
            form_id=form_id,
            field_id=data.get('field_id', ''),
            interaction_type=data['type'],
            device_type=data.get('device_type', 'desktop'),
            date=today,
            # Cluster nearby points (within 5% of each other)
            x_position__gte=data['x'] - 2.5,
            x_position__lte=data['x'] + 2.5,
            y_position__gte=data['y'] - 2.5,
            y_position__lte=data['y'] + 2.5,
        ).first()
        
        if existing:
            existing.interaction_count += 1
            existing.avg_duration_ms = (
                (existing.avg_duration_ms * (existing.interaction_count - 1) + data.get('duration', 0))
                / existing.interaction_count
            )
            existing.save()
            return existing
        
        return FormHeatmapData.objects.create(
            form_id=form_id,
            field_id=data.get('field_id', ''),
            interaction_type=data['type'],
            x_position=data['x'],
            y_position=data['y'],
            device_type=data.get('device_type', 'desktop'),
            avg_duration_ms=data.get('duration', 0),
            date=today,
        )
    
    @classmethod
    def get_heatmap_data(cls, form_id: str, interaction_type: str = None, 
                         device_type: str = None, days: int = 30):
        """Get aggregated heatmap data for visualization"""
        start_date = timezone.now().date() - timedelta(days=days)
        
        queryset = FormHeatmapData.objects.filter(
            form_id=form_id,
            date__gte=start_date
        )
        
        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        # Aggregate by position
        data = queryset.values(
            'x_position', 'y_position', 'field_id', 'interaction_type'
        ).annotate(
            count=Sum('interaction_count'),
            avg_duration=Avg('avg_duration_ms'),
        )
        
        return list(data)


class SessionRecordingService:
    """Service for session recordings"""
    
    @classmethod
    def start_recording(cls, form_id: str, session_data: dict):
        """Start a new session recording"""
        recording = SessionRecording.objects.create(
            form_id=form_id,
            session_id=session_data['session_id'],
            device_type=session_data.get('device_type', 'desktop'),
            browser=session_data.get('browser', ''),
            os=session_data.get('os', ''),
            screen_width=session_data.get('screen_width', 0),
            screen_height=session_data.get('screen_height', 0),
            country=session_data.get('country', ''),
            status='recording',
            started_at=timezone.now(),
        )
        return recording
    
    @classmethod
    def add_event(cls, session_id: str, event_data: dict):
        """Add an event to a session recording"""
        try:
            recording = SessionRecording.objects.get(session_id=session_id)
        except SessionRecording.DoesNotExist:
            return None
        
        event = SessionEvent.objects.create(
            session=recording,
            event_type=event_data['type'],
            timestamp=event_data['timestamp'],
            target_element=event_data.get('target', ''),
            field_id=event_data.get('field_id', ''),
            x_position=event_data.get('x', 0),
            y_position=event_data.get('y', 0),
            scroll_position=event_data.get('scroll', 0),
            data=event_data.get('data', {}),
        )
        
        recording.events_count = F('events_count') + 1
        
        # Detect rage clicks
        if event_data['type'] == 'click':
            recent_clicks = SessionEvent.objects.filter(
                session=recording,
                event_type='click',
                timestamp__gte=event_data['timestamp'] - 3000,  # Within 3 seconds
            ).count()
            
            if recent_clicks >= 3:
                recording.rage_clicks_count = F('rage_clicks_count') + 1
        
        recording.save()
        return event
    
    @classmethod
    def end_recording(cls, session_id: str, completed: bool = False, drop_off_field: str = ''):
        """End a session recording"""
        try:
            recording = SessionRecording.objects.get(session_id=session_id)
        except SessionRecording.DoesNotExist:
            return None
        
        recording.status = 'ready'
        recording.ended_at = timezone.now()
        recording.completed_form = completed
        recording.drop_off_field = drop_off_field
        
        # Calculate duration
        if recording.started_at:
            recording.duration_seconds = int(
                (recording.ended_at - recording.started_at).total_seconds()
            )
        
        recording.save()
        return recording
    
    @classmethod
    def get_recordings(cls, form_id: str, filters: dict = None):
        """Get session recordings for a form"""
        filters = filters or {}
        
        queryset = SessionRecording.objects.filter(
            form_id=form_id,
            status='ready'
        ).order_by('-started_at')
        
        if filters.get('completed_only'):
            queryset = queryset.filter(completed_form=True)
        if filters.get('abandoned_only'):
            queryset = queryset.filter(completed_form=False)
        if filters.get('has_rage_clicks'):
            queryset = queryset.filter(rage_clicks_count__gt=0)
        if filters.get('min_duration'):
            queryset = queryset.filter(duration_seconds__gte=filters['min_duration'])
        
        return queryset
    
    @classmethod
    def get_recording_playback(cls, recording_id: str):
        """Get recording data for playback"""
        try:
            recording = SessionRecording.objects.get(id=recording_id)
        except SessionRecording.DoesNotExist:
            return None
        
        events = SessionEvent.objects.filter(session=recording).order_by('timestamp')
        
        return {
            'recording': {
                'id': str(recording.id),
                'session_id': recording.session_id,
                'device_type': recording.device_type,
                'screen_width': recording.screen_width,
                'screen_height': recording.screen_height,
                'duration': recording.duration_seconds,
                'completed': recording.completed_form,
                'started_at': recording.started_at.isoformat(),
            },
            'events': [
                {
                    'type': e.event_type,
                    'timestamp': e.timestamp,
                    'target': e.target_element,
                    'field_id': e.field_id,
                    'x': e.x_position,
                    'y': e.y_position,
                    'scroll': e.scroll_position,
                    'data': e.data,
                }
                for e in events
            ],
        }


class DropOffAnalysisService:
    """Service for analyzing form drop-offs"""
    
    @classmethod
    def analyze_dropoffs(cls, form_id: str, days: int = 30):
        """Analyze drop-off patterns for a form"""
        start_date = timezone.now() - timedelta(days=days)
        
        # Get session data
        sessions = SessionRecording.objects.filter(
            form_id=form_id,
            started_at__gte=start_date,
            status='ready'
        )
        
        # Get form schema to identify fields
        try:
            form = Form.objects.get(id=form_id)
            fields = form.schema_json.get('fields', [])
        except Form.DoesNotExist:
            return []
        
        # Analyze each field
        analysis_date = timezone.now().date()
        results = []
        
        for i, field in enumerate(fields):
            field_id = field.get('id', '')
            
            # Count sessions that reached this field
            reached = sessions.filter(
                events__field_id=field_id,
                events__event_type='field_focus'
            ).distinct().count()
            
            # Count sessions that completed this field
            completed = sessions.filter(
                events__field_id=field_id,
                events__event_type='field_blur',
                events__data__has_value=True
            ).distinct().count()
            
            # Count drop-offs at this field
            dropped = sessions.filter(
                completed_form=False,
                drop_off_field=field_id
            ).count()
            
            drop_off_rate = (dropped / reached * 100) if reached > 0 else 0
            
            analysis, created = DropOffAnalysis.objects.update_or_create(
                form_id=form_id,
                field_id=field_id,
                analysis_date=analysis_date,
                defaults={
                    'field_label': field.get('label', ''),
                    'field_order': i,
                    'visitors_reached': reached,
                    'visitors_completed': completed,
                    'visitors_dropped': dropped,
                    'drop_off_rate': drop_off_rate,
                }
            )
            
            results.append(analysis)
        
        return results
    
    @classmethod
    def get_dropoff_insights(cls, form_id: str):
        """Get drop-off insights with AI-generated reasons"""
        latest = DropOffAnalysis.objects.filter(
            form_id=form_id
        ).order_by('-analysis_date', 'field_order')[:20]
        
        # Find problematic fields
        problem_fields = [
            a for a in latest
            if a.drop_off_rate > 10  # More than 10% drop-off
        ]
        
        insights = []
        for field in problem_fields:
            insight = {
                'field_id': field.field_id,
                'field_label': field.field_label,
                'drop_off_rate': field.drop_off_rate,
                'suspected_reasons': cls._analyze_reasons(field),
                'recommendations': cls._generate_recommendations(field),
            }
            insights.append(insight)
        
        return insights
    
    @classmethod
    def _analyze_reasons(cls, analysis):
        """Analyze potential reasons for drop-off"""
        reasons = []
        
        if analysis.validation_errors > 0:
            reasons.append({
                'reason': 'Validation errors',
                'detail': f'{analysis.validation_errors} validation errors detected',
                'confidence': 0.8,
            })
        
        if analysis.avg_time_on_field > 30:  # More than 30 seconds
            reasons.append({
                'reason': 'Complex field',
                'detail': 'Users spend a long time on this field',
                'confidence': 0.6,
            })
        
        return reasons
    
    @classmethod
    def _generate_recommendations(cls, analysis):
        """Generate recommendations to reduce drop-offs"""
        recommendations = []
        
        if analysis.validation_errors > 0:
            recommendations.append({
                'action': 'Improve validation messages',
                'priority': 'high',
            })
        
        if analysis.drop_off_rate > 20:
            recommendations.append({
                'action': 'Consider making field optional',
                'priority': 'medium',
            })
        
        return recommendations


class ABTestAnalysisService:
    """Service for A/B test statistical analysis"""
    
    @classmethod
    def calculate_results(cls, ab_test_id: str):
        """Calculate statistical results for an A/B test"""
        try:
            ab_test = ABTest.objects.get(id=ab_test_id)
        except ABTest.DoesNotExist:
            return None
        
        form = ab_test.form
        variants = FormVariant.objects.filter(form=form, is_active=True)
        
        results = []
        
        for variant in variants:
            # Control is the original form
            control_visitors = form.views_count
            control_conversions = form.submissions_count
            control_rate = (control_conversions / control_visitors * 100) if control_visitors > 0 else 0
            
            variant_visitors = variant.views_count
            variant_conversions = variant.submissions_count
            variant_rate = (variant_conversions / variant_visitors * 100) if variant_visitors > 0 else 0
            
            # Calculate relative improvement
            relative_improvement = (
                (variant_rate - control_rate) / control_rate * 100
            ) if control_rate > 0 else 0
            
            # Calculate statistical significance using chi-squared test
            p_value, is_significant = cls._calculate_significance(
                control_visitors, control_conversions,
                variant_visitors, variant_conversions
            )
            
            confidence_level = (1 - p_value) * 100 if p_value else 0
            
            result, created = ABTestResult.objects.update_or_create(
                ab_test=ab_test,
                variant=variant,
                defaults={
                    'control_visitors': control_visitors,
                    'control_conversions': control_conversions,
                    'control_conversion_rate': control_rate,
                    'variant_visitors': variant_visitors,
                    'variant_conversions': variant_conversions,
                    'variant_conversion_rate': variant_rate,
                    'relative_improvement': relative_improvement,
                    'p_value': p_value,
                    'confidence_level': confidence_level,
                    'is_significant': is_significant,
                    'sample_size_needed': cls._calculate_sample_size_needed(
                        control_rate, variant_rate
                    ),
                }
            )
            
            results.append(result)
        
        return results
    
    @classmethod
    def _calculate_significance(cls, control_n, control_conv, 
                                variant_n, variant_conv, alpha=0.05):
        """Calculate statistical significance using chi-squared test"""
        if control_n == 0 or variant_n == 0:
            return None, False
        
        # Create contingency table
        control_no_conv = control_n - control_conv
        variant_no_conv = variant_n - variant_conv
        
        observed = [
            [control_conv, control_no_conv],
            [variant_conv, variant_no_conv]
        ]
        
        try:
            chi2, p_value, dof, expected = scipy_stats.chi2_contingency(observed)
            is_significant = p_value < alpha
            return p_value, is_significant
        except Exception:
            return None, False
    
    @classmethod
    def _calculate_sample_size_needed(cls, baseline_rate, target_rate, 
                                       alpha=0.05, power=0.8):
        """Calculate sample size needed for statistical power"""
        if baseline_rate == 0 or target_rate == 0:
            return 0
        
        # Use simplified formula
        effect_size = abs(target_rate - baseline_rate) / 100
        if effect_size == 0:
            return float('inf')
        
        # Approximate sample size
        z_alpha = 1.96  # For 95% confidence
        z_beta = 0.84   # For 80% power
        
        p1 = baseline_rate / 100
        p2 = target_rate / 100
        p_avg = (p1 + p2) / 2
        
        n = (
            2 * p_avg * (1 - p_avg) * (z_alpha + z_beta) ** 2
        ) / (p1 - p2) ** 2
        
        return int(math.ceil(n))


class BehaviorInsightService:
    """Service for generating AI-powered behavior insights"""
    
    @classmethod
    def generate_insights(cls, form_id: str):
        """Generate behavior insights for a form"""
        insights = []
        
        # Analyze session patterns
        pattern_insights = cls._analyze_patterns(form_id)
        insights.extend(pattern_insights)
        
        # Detect anomalies
        anomaly_insights = cls._detect_anomalies(form_id)
        insights.extend(anomaly_insights)
        
        # Identify optimization opportunities
        optimization_insights = cls._find_optimizations(form_id)
        insights.extend(optimization_insights)
        
        # Save insights to database
        for insight_data in insights:
            BehaviorInsight.objects.create(
                form_id=form_id,
                **insight_data
            )
        
        return insights
    
    @classmethod
    def _analyze_patterns(cls, form_id: str):
        """Analyze user behavior patterns"""
        insights = []
        
        # Check for common patterns
        sessions = SessionRecording.objects.filter(
            form_id=form_id,
            status='ready'
        )
        
        # Pattern: High abandonment on specific devices
        mobile_sessions = sessions.filter(device_type='mobile')
        mobile_abandon_rate = (
            mobile_sessions.filter(completed_form=False).count() /
            mobile_sessions.count() * 100
        ) if mobile_sessions.count() > 0 else 0
        
        if mobile_abandon_rate > 50:
            insights.append({
                'insight_type': 'pattern',
                'priority': 'high',
                'title': 'High mobile abandonment rate',
                'description': f'{mobile_abandon_rate:.1f}% of mobile users abandon the form',
                'affected_fields': [],
                'recommendations': [
                    'Optimize form for mobile devices',
                    'Consider simplifying the form on mobile',
                ],
                'estimated_impact': 15.0,
            })
        
        return insights
    
    @classmethod
    def _detect_anomalies(cls, form_id: str):
        """Detect unusual behavior patterns"""
        return []  # Implement anomaly detection
    
    @classmethod
    def _find_optimizations(cls, form_id: str):
        """Find optimization opportunities"""
        return []  # Implement optimization finding
