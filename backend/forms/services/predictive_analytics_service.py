"""
Predictive Analytics Service with Auto-Alerts
Forecast form performance and send proactive alerts
"""
import json
import statistics
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from openai import OpenAI


class PredictiveAnalyticsService:
    """
    Service for predictive analytics with forecasting and auto-alerts.
    Uses time-series analysis to predict trends and detect anomalies.
    """
    
    # Alert thresholds
    ALERT_THRESHOLDS = {
        'conversion_drop': 20,  # Alert if conversion drops by 20%
        'abandonment_spike': 30,  # Alert if abandonment increases by 30%
        'traffic_drop': 25,  # Alert if traffic drops by 25%
        'error_rate': 15,  # Alert if error rate exceeds 15%
    }
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
    
    def get_predictive_dashboard(
        self,
        form,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get comprehensive predictive analytics dashboard
        
        Args:
            form: Form model instance
            days: Number of days to analyze
            
        Returns:
            Dashboard data with predictions and insights
        """
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get historical data
        daily_stats = self._get_daily_stats(form, start_date, end_date)
        
        # Generate predictions
        predictions = self._generate_predictions(daily_stats, days=7)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(daily_stats)
        
        # Generate insights
        insights = self._generate_ai_insights(form, daily_stats, predictions, anomalies)
        
        # Check for alerts
        alerts = self._check_alert_conditions(form, daily_stats)
        
        return {
            'form_id': str(form.id),
            'form_title': form.title,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days,
            },
            'current_metrics': self._get_current_metrics(daily_stats),
            'historical_data': daily_stats,
            'predictions': predictions,
            'anomalies': anomalies,
            'insights': insights,
            'alerts': alerts,
            'generated_at': timezone.now().isoformat(),
        }
    
    def _get_daily_stats(
        self,
        form,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Get daily statistics for analysis"""
        from forms.models import Submission
        from forms.models_advanced import FormAnalytics
        
        # Get views by day
        views_by_day = FormAnalytics.objects.filter(
            form=form,
            event_type='view',
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Get submissions by day
        submissions_by_day = Submission.objects.filter(
            form=form,
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Get starts (form_start events)
        starts_by_day = FormAnalytics.objects.filter(
            form=form,
            event_type='start',
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Get abandonments
        abandons_by_day = FormAnalytics.objects.filter(
            form=form,
            event_type='abandon',
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Combine into daily stats
        views_dict = {v['date']: v['count'] for v in views_by_day}
        submissions_dict = {s['date']: s['count'] for s in submissions_by_day}
        starts_dict = {s['date']: s['count'] for s in starts_by_day}
        abandons_dict = {a['date']: a['count'] for a in abandons_by_day}
        
        # Generate all dates in range
        daily_stats = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            views = views_dict.get(current_date, 0)
            submissions = submissions_dict.get(current_date, 0)
            starts = starts_dict.get(current_date, 0)
            abandons = abandons_dict.get(current_date, 0)
            
            conversion_rate = (submissions / views * 100) if views > 0 else 0
            abandonment_rate = (abandons / starts * 100) if starts > 0 else 0
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'views': views,
                'starts': starts,
                'submissions': submissions,
                'abandons': abandons,
                'conversion_rate': round(conversion_rate, 2),
                'abandonment_rate': round(abandonment_rate, 2),
            })
            
            current_date += timedelta(days=1)
        
        return daily_stats
    
    def _get_current_metrics(self, daily_stats: List[Dict]) -> Dict[str, Any]:
        """Calculate current metrics from historical data"""
        if not daily_stats:
            return {}
        
        # Last 7 days
        recent = daily_stats[-7:] if len(daily_stats) >= 7 else daily_stats
        
        total_views = sum(d['views'] for d in recent)
        total_submissions = sum(d['submissions'] for d in recent)
        total_starts = sum(d['starts'] for d in recent)
        total_abandons = sum(d['abandons'] for d in recent)
        
        # Previous 7 days for comparison
        if len(daily_stats) >= 14:
            previous = daily_stats[-14:-7]
            prev_views = sum(d['views'] for d in previous)
            prev_submissions = sum(d['submissions'] for d in previous)
            
            views_change = ((total_views - prev_views) / prev_views * 100) if prev_views > 0 else 0
            submissions_change = ((total_submissions - prev_submissions) / prev_submissions * 100) if prev_submissions > 0 else 0
        else:
            views_change = 0
            submissions_change = 0
        
        return {
            'total_views': total_views,
            'total_submissions': total_submissions,
            'total_starts': total_starts,
            'total_abandons': total_abandons,
            'conversion_rate': round((total_submissions / total_views * 100) if total_views > 0 else 0, 2),
            'abandonment_rate': round((total_abandons / total_starts * 100) if total_starts > 0 else 0, 2),
            'views_change': round(views_change, 1),
            'submissions_change': round(submissions_change, 1),
            'trend': 'up' if submissions_change > 0 else 'down' if submissions_change < 0 else 'stable',
        }
    
    def _generate_predictions(
        self,
        daily_stats: List[Dict],
        days: int = 7,
    ) -> Dict[str, Any]:
        """Generate predictions using time-series analysis"""
        if len(daily_stats) < 7:
            return {'error': 'Insufficient data for predictions'}
        
        predictions = {
            'views': [],
            'submissions': [],
            'conversion_rate': [],
        }
        
        # Simple moving average + trend for prediction
        for metric in ['views', 'submissions', 'conversion_rate']:
            values = [d[metric] for d in daily_stats]
            
            # Calculate trend
            trend = self._calculate_trend(values)
            
            # Calculate moving average
            window = min(7, len(values))
            ma = sum(values[-window:]) / window
            
            # Generate predictions
            last_date = datetime.fromisoformat(daily_stats[-1]['date'])
            
            for i in range(1, days + 1):
                pred_date = last_date + timedelta(days=i)
                pred_value = ma + (trend * i)
                
                # Don't predict negative values
                pred_value = max(0, pred_value)
                
                # Calculate confidence interval
                std_dev = statistics.stdev(values[-window:]) if len(values) >= 2 else 0
                lower = max(0, pred_value - 1.96 * std_dev)
                upper = pred_value + 1.96 * std_dev
                
                predictions[metric].append({
                    'date': pred_date.date().isoformat(),
                    'predicted': round(pred_value, 2),
                    'lower_bound': round(lower, 2),
                    'upper_bound': round(upper, 2),
                    'confidence': 0.95,
                })
        
        # Summary predictions
        predictions['summary'] = {
            'next_week_views': sum(p['predicted'] for p in predictions['views']),
            'next_week_submissions': sum(p['predicted'] for p in predictions['submissions']),
            'avg_conversion_rate': statistics.mean(p['predicted'] for p in predictions['conversion_rate']),
            'trend_direction': 'increasing' if self._calculate_trend([d['submissions'] for d in daily_stats]) > 0 else 'decreasing',
        }
        
        return predictions
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend using least squares"""
        n = len(values)
        if n < 2:
            return 0
        
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def _detect_anomalies(
        self,
        daily_stats: List[Dict],
        threshold: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods"""
        anomalies = []
        
        for metric in ['views', 'submissions', 'conversion_rate', 'abandonment_rate']:
            values = [d[metric] for d in daily_stats]
            
            if len(values) < 7:
                continue
            
            # Calculate rolling mean and std
            window = 7
            for i in range(window, len(values)):
                window_values = values[i-window:i]
                mean = statistics.mean(window_values)
                std = statistics.stdev(window_values) if len(window_values) >= 2 else 0
                
                if std == 0:
                    continue
                
                # Z-score
                z_score = (values[i] - mean) / std
                
                if abs(z_score) > threshold:
                    anomalies.append({
                        'date': daily_stats[i]['date'],
                        'metric': metric,
                        'value': values[i],
                        'expected': round(mean, 2),
                        'z_score': round(z_score, 2),
                        'type': 'spike' if z_score > 0 else 'drop',
                        'severity': 'high' if abs(z_score) > 3 else 'medium',
                    })
        
        return anomalies
    
    def _generate_ai_insights(
        self,
        form,
        daily_stats: List[Dict],
        predictions: Dict,
        anomalies: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered insights from analytics data"""
        
        # Prepare context for AI
        context = {
            'form_title': form.title,
            'total_days': len(daily_stats),
            'avg_daily_views': statistics.mean(d['views'] for d in daily_stats) if daily_stats else 0,
            'avg_daily_submissions': statistics.mean(d['submissions'] for d in daily_stats) if daily_stats else 0,
            'avg_conversion_rate': statistics.mean(d['conversion_rate'] for d in daily_stats) if daily_stats else 0,
            'trend': predictions.get('summary', {}).get('trend_direction', 'stable'),
            'anomalies_count': len(anomalies),
            'recent_anomalies': anomalies[-3:] if anomalies else [],
        }
        
        prompt = f"""Analyze this form's performance data and provide 3-5 actionable insights.

Form: {context['form_title']}
Analysis Period: {context['total_days']} days
Average Daily Views: {context['avg_daily_views']:.0f}
Average Daily Submissions: {context['avg_daily_submissions']:.0f}
Average Conversion Rate: {context['avg_conversion_rate']:.1f}%
Trend: {context['trend']}
Anomalies Detected: {context['anomalies_count']}

Recent anomalies:
{json.dumps(context['recent_anomalies'], indent=2)}

Return JSON array of insights:
[
    {{
        "title": "Insight title",
        "description": "Detailed explanation",
        "impact": "high|medium|low",
        "recommendation": "Specific action to take",
        "category": "conversion|traffic|engagement|timing|anomaly"
    }}
]

Focus on actionable insights that can improve form performance.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a form analytics expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception:
            # Fallback to rule-based insights
            return self._generate_rule_based_insights(context, anomalies)
    
    def _generate_rule_based_insights(
        self,
        context: Dict,
        anomalies: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Generate insights based on rules"""
        insights = []
        
        # Low conversion rate
        if context['avg_conversion_rate'] < 20:
            insights.append({
                'title': 'Low Conversion Rate',
                'description': f'Average conversion rate is {context["avg_conversion_rate"]:.1f}%, which is below industry average.',
                'impact': 'high',
                'recommendation': 'Review form length, required fields, and user experience.',
                'category': 'conversion',
            })
        
        # Declining trend
        if context['trend'] == 'decreasing':
            insights.append({
                'title': 'Declining Submissions',
                'description': 'Form submissions are trending downward.',
                'impact': 'high',
                'recommendation': 'Investigate traffic sources and form visibility.',
                'category': 'traffic',
            })
        
        # Anomalies detected
        if context['anomalies_count'] > 0:
            insights.append({
                'title': 'Unusual Activity Detected',
                'description': f'{context["anomalies_count"]} anomalies detected in the analysis period.',
                'impact': 'medium',
                'recommendation': 'Review anomaly dates for potential issues or opportunities.',
                'category': 'anomaly',
            })
        
        return insights
    
    def _check_alert_conditions(
        self,
        form,
        daily_stats: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Check if any alert conditions are met"""
        alerts = []
        
        if len(daily_stats) < 14:
            return alerts
        
        # Compare last 7 days to previous 7 days
        recent = daily_stats[-7:]
        previous = daily_stats[-14:-7]
        
        # Conversion drop
        recent_conversion = statistics.mean(d['conversion_rate'] for d in recent)
        prev_conversion = statistics.mean(d['conversion_rate'] for d in previous)
        
        if prev_conversion > 0:
            conversion_change = ((recent_conversion - prev_conversion) / prev_conversion) * 100
            
            if conversion_change < -self.ALERT_THRESHOLDS['conversion_drop']:
                alerts.append({
                    'type': 'conversion_drop',
                    'severity': 'high',
                    'message': f'Conversion rate dropped by {abs(conversion_change):.1f}%',
                    'current': round(recent_conversion, 2),
                    'previous': round(prev_conversion, 2),
                    'change': round(conversion_change, 1),
                    'threshold': self.ALERT_THRESHOLDS['conversion_drop'],
                })
        
        # Traffic drop
        recent_views = sum(d['views'] for d in recent)
        prev_views = sum(d['views'] for d in previous)
        
        if prev_views > 0:
            views_change = ((recent_views - prev_views) / prev_views) * 100
            
            if views_change < -self.ALERT_THRESHOLDS['traffic_drop']:
                alerts.append({
                    'type': 'traffic_drop',
                    'severity': 'high',
                    'message': f'Form views dropped by {abs(views_change):.1f}%',
                    'current': recent_views,
                    'previous': prev_views,
                    'change': round(views_change, 1),
                    'threshold': self.ALERT_THRESHOLDS['traffic_drop'],
                })
        
        # Abandonment spike
        recent_abandon = statistics.mean(d['abandonment_rate'] for d in recent)
        prev_abandon = statistics.mean(d['abandonment_rate'] for d in previous)
        
        if prev_abandon > 0:
            abandon_change = ((recent_abandon - prev_abandon) / prev_abandon) * 100
            
            if abandon_change > self.ALERT_THRESHOLDS['abandonment_spike']:
                alerts.append({
                    'type': 'abandonment_spike',
                    'severity': 'medium',
                    'message': f'Abandonment rate increased by {abandon_change:.1f}%',
                    'current': round(recent_abandon, 2),
                    'previous': round(prev_abandon, 2),
                    'change': round(abandon_change, 1),
                    'threshold': self.ALERT_THRESHOLDS['abandonment_spike'],
                })
        
        return alerts
    
    def send_alert_email(
        self,
        form,
        alerts: List[Dict],
        recipients: List[str],
    ) -> bool:
        """Send alert email to recipients"""
        if not alerts:
            return False
        
        subject = f'[Alert] {form.title} - Performance Issues Detected'
        
        body = f"""
Performance alerts for form: {form.title}

{len(alerts)} alert(s) detected:

"""
        
        for i, alert in enumerate(alerts, 1):
            body += f"""
{i}. {alert['type'].replace('_', ' ').title()}
   Severity: {alert['severity'].upper()}
   {alert['message']}
   Current: {alert['current']}
   Previous: {alert['previous']}
   Change: {alert['change']}%
"""
        
        body += f"""
---
Review your form analytics: {settings.FRONTEND_URL}/forms/{form.id}/analytics

This is an automated alert from SmartFormBuilder.
"""
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Alert email failed: {e}")
            return False


class AlertConfiguration:
    """Manage alert configurations for forms"""
    
    @staticmethod
    def create_alert_config(
        form,
        alert_type: str,
        threshold: float,
        recipients: List[str],
        enabled: bool = True,
    ) -> 'AlertConfig':
        """Create alert configuration"""
        from forms.models_advanced import AlertConfig
        
        config, created = AlertConfig.objects.update_or_create(
            form=form,
            alert_type=alert_type,
            defaults={
                'threshold': threshold,
                'recipients': recipients,
                'is_enabled': enabled,
            }
        )
        
        return config
    
    @staticmethod
    def check_and_send_alerts(form) -> List[Dict]:
        """Check alert conditions and send notifications"""
        from forms.models_advanced import AlertConfig
        
        service = PredictiveAnalyticsService()
        
        # Get recent stats
        end_date = timezone.now()
        start_date = end_date - timedelta(days=14)
        daily_stats = service._get_daily_stats(form, start_date, end_date)
        
        # Check conditions
        alerts = service._check_alert_conditions(form, daily_stats)
        
        # Get configured recipients
        configs = AlertConfig.objects.filter(form=form, is_enabled=True)
        
        sent_alerts = []
        for alert in alerts:
            matching_configs = configs.filter(alert_type=alert['type'])
            
            for config in matching_configs:
                if abs(alert['change']) >= config.threshold:
                    service.send_alert_email(form, [alert], config.recipients)
                    sent_alerts.append(alert)
        
        return sent_alerts


class ForecastService:
    """Advanced forecasting using multiple methods"""
    
    @staticmethod
    def forecast_with_seasonality(
        daily_stats: List[Dict],
        metric: str,
        days_ahead: int = 14,
    ) -> List[Dict]:
        """Forecast with weekly seasonality"""
        values = [d[metric] for d in daily_stats]
        
        if len(values) < 14:
            return []
        
        # Calculate day-of-week factors
        dow_factors = defaultdict(list)
        for i, d in enumerate(daily_stats):
            dow = datetime.fromisoformat(d['date']).weekday()
            dow_factors[dow].append(d[metric])
        
        dow_avg = {
            dow: statistics.mean(vals) if vals else 0
            for dow, vals in dow_factors.items()
        }
        overall_avg = statistics.mean(values) if values else 0
        
        # Seasonal factors
        seasonal_factors = {
            dow: (avg / overall_avg) if overall_avg > 0 else 1
            for dow, avg in dow_avg.items()
        }
        
        # Base forecast (trend + average)
        trend = PredictiveAnalyticsService()._calculate_trend(values)
        base = statistics.mean(values[-7:])
        
        # Generate forecasts
        forecasts = []
        last_date = datetime.fromisoformat(daily_stats[-1]['date'])
        
        for i in range(1, days_ahead + 1):
            forecast_date = last_date + timedelta(days=i)
            dow = forecast_date.weekday()
            
            # Apply trend and seasonality
            forecast_value = (base + trend * i) * seasonal_factors.get(dow, 1)
            
            forecasts.append({
                'date': forecast_date.date().isoformat(),
                'predicted': round(max(0, forecast_value), 2),
                'day_of_week': forecast_date.strftime('%A'),
                'seasonal_factor': round(seasonal_factors.get(dow, 1), 2),
            })
        
        return forecasts
