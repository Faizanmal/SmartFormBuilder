"""
AI-Powered Form Optimization Engine
Analyzes form performance and suggests optimizations automatically
"""
import json
import statistics
from typing import Dict, Any, List, Tuple
from datetime import timedelta
from django.db.models import Count
from django.utils import timezone
from openai import OpenAI
from django.conf import settings


class FormOptimizationService:
    """
    ML-based form analysis and auto-suggestions for optimization.
    Analyzes submission data, heat maps, and abandonment patterns.
    """
    
    OPTIMIZATION_WEIGHTS = {
        'field_order': 0.25,
        'field_complexity': 0.20,
        'required_fields': 0.15,
        'field_labels': 0.15,
        'form_length': 0.15,
        'mobile_friendliness': 0.10,
    }
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
    
    def analyze_form_performance(self, form) -> Dict[str, Any]:
        """
        Comprehensive form performance analysis
        Returns optimization score and detailed metrics
        """
        from forms.models import Submission
        from forms.models_advanced import FormAnalytics, PartialSubmission
        
        # Get date range (last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Get analytics data
        analytics = FormAnalytics.objects.filter(
            form=form,
            created_at__gte=start_date
        )
        
        submissions = Submission.objects.filter(
            form=form,
            created_at__gte=start_date
        )
        
        partial_submissions = PartialSubmission.objects.filter(
            form=form,
            created_at__gte=start_date
        )
        
        # Calculate metrics
        total_views = analytics.filter(event_type='view').count()
        total_starts = analytics.filter(event_type='start').count()
        total_submissions = submissions.count()
        total_abandons = partial_submissions.filter(is_abandoned=True).count()
        
        # Conversion rates
        view_to_start_rate = (total_starts / total_views * 100) if total_views > 0 else 0
        start_to_submit_rate = (total_submissions / total_starts * 100) if total_starts > 0 else 0
        overall_conversion = (total_submissions / total_views * 100) if total_views > 0 else 0
        abandonment_rate = (total_abandons / total_starts * 100) if total_starts > 0 else 0
        
        # Field-level analysis
        field_analytics = self._analyze_fields(form, analytics)
        
        # Device breakdown
        device_stats = self._analyze_devices(analytics)
        
        # Time-based patterns
        time_patterns = self._analyze_time_patterns(analytics, submissions)
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            form, field_analytics, overall_conversion, abandonment_rate
        )
        
        return {
            'form_id': str(form.id),
            'form_title': form.title,
            'period': {
                'from': start_date.isoformat(),
                'to': end_date.isoformat(),
            },
            'metrics': {
                'total_views': total_views,
                'total_starts': total_starts,
                'total_submissions': total_submissions,
                'total_abandons': total_abandons,
                'view_to_start_rate': round(view_to_start_rate, 2),
                'start_to_submit_rate': round(start_to_submit_rate, 2),
                'overall_conversion': round(overall_conversion, 2),
                'abandonment_rate': round(abandonment_rate, 2),
            },
            'optimization_score': optimization_score,
            'field_analytics': field_analytics,
            'device_stats': device_stats,
            'time_patterns': time_patterns,
            'generated_at': timezone.now().isoformat(),
        }
    
    def _analyze_fields(self, form, analytics) -> List[Dict[str, Any]]:
        """Analyze individual field performance"""
        schema = form.schema_json
        fields = schema.get('fields', [])
        
        field_metrics = []
        for field in fields:
            field_id = field.get('id')
            
            # Get field-specific analytics
            focus_events = analytics.filter(
                event_type='field_focus',
                field_id=field_id
            ).count()
            
            blur_events = analytics.filter(
                event_type='field_blur',
                field_id=field_id
            ).count()
            
            error_events = analytics.filter(
                event_type='field_error',
                field_id=field_id
            ).count()
            
            # Calculate drop-off rate at this field
            drop_off_rate = (error_events / focus_events * 100) if focus_events > 0 else 0
            completion_rate = (blur_events / focus_events * 100) if focus_events > 0 else 0
            
            # Calculate average time spent (if available)
            avg_time = self._calculate_avg_field_time(analytics, field_id)
            
            field_metrics.append({
                'field_id': field_id,
                'field_label': field.get('label', ''),
                'field_type': field.get('type', ''),
                'required': field.get('required', False),
                'focus_count': focus_events,
                'completion_rate': round(completion_rate, 2),
                'error_rate': round(drop_off_rate, 2),
                'avg_time_seconds': avg_time,
                'is_problematic': drop_off_rate > 15 or completion_rate < 70,
            })
        
        return field_metrics
    
    def _calculate_avg_field_time(self, analytics, field_id: str) -> float:
        """Calculate average time spent on a field"""
        # Get pairs of focus and blur events
        focus_events = analytics.filter(
            event_type='field_focus',
            field_id=field_id
        ).values('session_id', 'created_at')
        
        blur_events = analytics.filter(
            event_type='field_blur',
            field_id=field_id
        ).values('session_id', 'created_at')
        
        times = []
        for focus in focus_events:
            blur = blur_events.filter(
                session_id=focus['session_id'],
                created_at__gt=focus['created_at']
            ).first()
            
            if blur:
                time_diff = (blur['created_at'] - focus['created_at']).total_seconds()
                if 0 < time_diff < 300:  # Ignore if > 5 minutes
                    times.append(time_diff)
        
        return round(statistics.mean(times), 2) if times else 0
    
    def _analyze_devices(self, analytics) -> Dict[str, Any]:
        """Analyze device type distribution"""
        device_counts = analytics.values('device_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        total = sum(d['count'] for d in device_counts)
        
        return {
            'breakdown': [
                {
                    'device': d['device_type'] or 'unknown',
                    'count': d['count'],
                    'percentage': round(d['count'] / total * 100, 2) if total > 0 else 0
                }
                for d in device_counts
            ],
            'total': total,
        }
    
    def _analyze_time_patterns(self, analytics, submissions) -> Dict[str, Any]:
        """Analyze when users are most active"""
        from django.db.models.functions import ExtractHour, ExtractDow
        
        # Hour of day analysis
        hourly = analytics.filter(event_type='submit').annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        # Day of week analysis
        daily = submissions.annotate(
            day=ExtractDow('created_at')
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        return {
            'hourly_distribution': list(hourly),
            'daily_distribution': [
                {'day': day_names[d['day']], 'count': d['count']}
                for d in daily
            ],
            'peak_hour': max(hourly, key=lambda x: x['count'])['hour'] if hourly else None,
            'peak_day': day_names[max(daily, key=lambda x: x['count'])['day']] if daily else None,
        }
    
    def _calculate_optimization_score(
        self, form, field_analytics: List[Dict], 
        conversion_rate: float, abandonment_rate: float
    ) -> Dict[str, Any]:
        """Calculate overall optimization score (0-100)"""
        schema = form.schema_json
        fields = schema.get('fields', [])
        
        scores = {}
        
        # Field order score (based on problematic fields position)
        problematic_positions = [
            i for i, f in enumerate(field_analytics) 
            if f.get('is_problematic')
        ]
        scores['field_order'] = 100 - (len(problematic_positions) * 10)
        
        # Field complexity score
        complex_types = ['file', 'payment', 'signature']
        complex_count = sum(1 for f in fields if f.get('type') in complex_types)
        scores['field_complexity'] = max(0, 100 - (complex_count * 15))
        
        # Required fields score (penalize too many required fields)
        required_count = sum(1 for f in fields if f.get('required'))
        required_ratio = required_count / len(fields) if fields else 0
        scores['required_fields'] = max(0, 100 - (required_ratio * 50)) if required_ratio > 0.7 else 100
        
        # Form length score
        field_count = len(fields)
        if field_count <= 5:
            scores['form_length'] = 100
        elif field_count <= 10:
            scores['form_length'] = 85
        elif field_count <= 15:
            scores['form_length'] = 70
        else:
            scores['form_length'] = max(0, 100 - (field_count - 15) * 5)
        
        # Mobile friendliness (based on device conversion rates)
        scores['mobile_friendliness'] = 80  # Default, would need more data
        
        # Label quality score (check for clear labels)
        label_issues = sum(1 for f in fields if len(f.get('label', '')) < 3)
        scores['field_labels'] = max(0, 100 - (label_issues * 20))
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * weight 
            for key, weight in self.OPTIMIZATION_WEIGHTS.items()
        )
        
        # Adjust based on actual conversion
        if conversion_rate > 50:
            total_score = min(100, total_score + 10)
        elif conversion_rate < 20:
            total_score = max(0, total_score - 10)
        
        return {
            'total': round(total_score, 1),
            'grade': self._get_grade(total_score),
            'breakdown': scores,
            'conversion_impact': round(conversion_rate, 2),
            'abandonment_impact': round(abandonment_rate, 2),
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def generate_optimization_suggestions(self, form) -> List[Dict[str, Any]]:
        """
        Generate AI-powered optimization suggestions
        Uses GPT to analyze form and suggest improvements
        """
        # Get performance data
        performance = self.analyze_form_performance(form)
        schema = form.schema_json
        
        # Build context for AI
        context = {
            'form_title': form.title,
            'field_count': len(schema.get('fields', [])),
            'fields': schema.get('fields', []),
            'conversion_rate': performance['metrics']['overall_conversion'],
            'abandonment_rate': performance['metrics']['abandonment_rate'],
            'problematic_fields': [
                f for f in performance['field_analytics']
                if f.get('is_problematic')
            ],
            'optimization_score': performance['optimization_score']['total'],
        }
        
        # Generate AI suggestions
        suggestions = self._generate_ai_suggestions(context)
        
        # Add rule-based suggestions
        rule_suggestions = self._generate_rule_based_suggestions(form, performance)
        
        # Combine and deduplicate
        all_suggestions = suggestions + rule_suggestions
        
        # Sort by priority
        all_suggestions.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return all_suggestions[:10]  # Return top 10 suggestions
    
    def _generate_ai_suggestions(self, context: Dict) -> List[Dict[str, Any]]:
        """Generate suggestions using GPT"""
        try:
            prompt = f"""Analyze this form and suggest optimizations to improve conversion rate.

Form: {context['form_title']}
Current conversion rate: {context['conversion_rate']}%
Abandonment rate: {context['abandonment_rate']}%
Optimization score: {context['optimization_score']}/100

Fields ({context['field_count']} total):
{json.dumps(context['fields'], indent=2)}

Problematic fields (high error/drop-off rates):
{json.dumps(context['problematic_fields'], indent=2)}

Provide 5 specific, actionable suggestions in JSON format:
[
  {{
    "title": "Short title",
    "description": "Detailed explanation",
    "impact": "high|medium|low",
    "priority": 1-10,
    "category": "field_order|field_removal|label_improvement|validation|ux|mobile",
    "affected_fields": ["field_ids"],
    "auto_applicable": true/false,
    "suggested_change": {{}} // Optional: specific schema changes
  }}
]

Focus on:
1. Field ordering (move problematic fields later)
2. Reducing required fields
3. Improving labels and placeholders
4. Mobile optimization
5. Reducing form length
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a form optimization expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            result = response.choices[0].message.content
            suggestions = json.loads(result)
            return suggestions
            
        except Exception as e:
            print(f"AI suggestion generation failed: {e}")
            return []
    
    def _generate_rule_based_suggestions(
        self, form, performance: Dict
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on predefined rules"""
        suggestions = []
        schema = form.schema_json
        fields = schema.get('fields', [])
        metrics = performance['metrics']
        field_analytics = performance['field_analytics']
        
        # Rule 1: Too many fields
        if len(fields) > 10:
            suggestions.append({
                'title': 'Reduce form length',
                'description': f'Your form has {len(fields)} fields. Forms with fewer than 10 fields typically have 20% higher completion rates.',
                'impact': 'high',
                'priority': 9,
                'category': 'form_length',
                'affected_fields': [],
                'auto_applicable': False,
            })
        
        # Rule 2: High abandonment rate
        if metrics['abandonment_rate'] > 30:
            suggestions.append({
                'title': 'Address high abandonment rate',
                'description': f'Your form has a {metrics["abandonment_rate"]}% abandonment rate. Consider adding progress indicators or save & resume functionality.',
                'impact': 'high',
                'priority': 10,
                'category': 'ux',
                'affected_fields': [],
                'auto_applicable': False,
            })
        
        # Rule 3: Problematic fields early in form
        for i, fa in enumerate(field_analytics[:3]):
            if fa.get('is_problematic'):
                field = next((f for f in fields if f['id'] == fa['field_id']), None)
                if field:
                    suggestions.append({
                        'title': f'Move "{fa["field_label"]}" later in form',
                        'description': f'This field has a {fa["error_rate"]}% error rate and is causing early drop-offs. Moving it later can improve completion.',
                        'impact': 'medium',
                        'priority': 7,
                        'category': 'field_order',
                        'affected_fields': [fa['field_id']],
                        'auto_applicable': True,
                        'suggested_change': {
                            'action': 'move_field',
                            'field_id': fa['field_id'],
                            'new_position': len(fields) - 2,
                        }
                    })
        
        # Rule 4: Too many required fields
        required_count = sum(1 for f in fields if f.get('required'))
        if required_count > len(fields) * 0.7:
            non_essential = [
                f for f in fields 
                if f.get('required') and f.get('type') not in ['email', 'name', 'phone']
            ]
            if non_essential:
                suggestions.append({
                    'title': 'Make some fields optional',
                    'description': f'{required_count} of {len(fields)} fields are required. Consider making non-essential fields optional.',
                    'impact': 'medium',
                    'priority': 6,
                    'category': 'validation',
                    'affected_fields': [f['id'] for f in non_essential[:3]],
                    'auto_applicable': True,
                })
        
        # Rule 5: Missing placeholders
        missing_placeholders = [
            f for f in fields 
            if f.get('type') in ['text', 'email', 'phone', 'textarea'] 
            and not f.get('placeholder')
        ]
        if missing_placeholders:
            suggestions.append({
                'title': 'Add helpful placeholders',
                'description': f'{len(missing_placeholders)} fields are missing placeholder text. Placeholders help users understand expected input.',
                'impact': 'low',
                'priority': 4,
                'category': 'label_improvement',
                'affected_fields': [f['id'] for f in missing_placeholders],
                'auto_applicable': True,
            })
        
        # Rule 6: Mobile optimization
        file_fields = [f for f in fields if f.get('type') == 'file']
        if file_fields and performance.get('device_stats', {}).get('breakdown'):
            mobile_pct = next(
                (d['percentage'] for d in performance['device_stats']['breakdown'] 
                 if d['device'] == 'mobile'), 0
            )
            if mobile_pct > 30:
                suggestions.append({
                    'title': 'Optimize file upload for mobile',
                    'description': f'{mobile_pct}% of users are on mobile. Consider camera capture options for file uploads.',
                    'impact': 'medium',
                    'priority': 5,
                    'category': 'mobile',
                    'affected_fields': [f['id'] for f in file_fields],
                    'auto_applicable': False,
                })
        
        return suggestions
    
    def apply_optimization(
        self, form, suggestion: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Apply a single optimization suggestion to a form
        Returns (success, updated_schema)
        """
        if not suggestion.get('auto_applicable'):
            return False, {'error': 'This suggestion requires manual review'}
        
        schema = form.schema_json.copy()
        fields = schema.get('fields', [])
        change = suggestion.get('suggested_change', {})
        action = change.get('action')
        
        try:
            if action == 'move_field':
                field_id = change.get('field_id')
                new_position = change.get('new_position', len(fields) - 1)
                
                # Find and move field
                field_idx = next(
                    (i for i, f in enumerate(fields) if f['id'] == field_id), 
                    None
                )
                if field_idx is not None:
                    field = fields.pop(field_idx)
                    fields.insert(new_position, field)
                    schema['fields'] = fields
            
            elif action == 'make_optional':
                field_ids = change.get('field_ids', [])
                for field in fields:
                    if field['id'] in field_ids:
                        field['required'] = False
                schema['fields'] = fields
            
            elif action == 'add_placeholder':
                field_id = change.get('field_id')
                placeholder = change.get('placeholder')
                for field in fields:
                    if field['id'] == field_id:
                        field['placeholder'] = placeholder
                        break
                schema['fields'] = fields
            
            else:
                return False, {'error': f'Unknown action: {action}'}
            
            # Update form schema
            form.schema_json = schema
            form.save()
            
            return True, schema
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def auto_optimize_form(self, form) -> Dict[str, Any]:
        """
        Automatically apply all safe optimizations
        Returns summary of changes made
        """
        suggestions = self.generate_optimization_suggestions(form)
        
        applied = []
        skipped = []
        
        for suggestion in suggestions:
            if suggestion.get('auto_applicable') and suggestion.get('impact') != 'high':
                success, result = self.apply_optimization(form, suggestion)
                if success:
                    applied.append({
                        'title': suggestion['title'],
                        'category': suggestion['category'],
                    })
                else:
                    skipped.append({
                        'title': suggestion['title'],
                        'reason': result.get('error', 'Unknown error'),
                    })
            else:
                skipped.append({
                    'title': suggestion['title'],
                    'reason': 'Requires manual review',
                })
        
        return {
            'form_id': str(form.id),
            'applied_count': len(applied),
            'skipped_count': len(skipped),
            'applied': applied,
            'skipped': skipped,
            'new_optimization_score': self.analyze_form_performance(form)['optimization_score'],
        }


class FormOptimizationAlert:
    """
    Monitor forms and send alerts when optimization opportunities arise
    """
    
    ALERT_THRESHOLDS = {
        'conversion_drop': 20,  # Alert if conversion drops by 20%
        'abandonment_spike': 15,  # Alert if abandonment increases by 15%
        'error_rate': 25,  # Alert if field error rate exceeds 25%
    }
    
    @classmethod
    def check_form_health(cls, form) -> List[Dict[str, Any]]:
        """Check form health and return any alerts"""
        service = FormOptimizationService()
        performance = service.analyze_form_performance(form)
        
        alerts = []
        metrics = performance['metrics']
        
        # Check conversion rate
        if metrics['overall_conversion'] < 20:
            alerts.append({
                'type': 'low_conversion',
                'severity': 'high',
                'message': f'Form conversion rate is only {metrics["overall_conversion"]}%',
                'recommendation': 'Review optimization suggestions',
            })
        
        # Check abandonment rate
        if metrics['abandonment_rate'] > cls.ALERT_THRESHOLDS['abandonment_spike']:
            alerts.append({
                'type': 'high_abandonment',
                'severity': 'high',
                'message': f'Form abandonment rate is {metrics["abandonment_rate"]}%',
                'recommendation': 'Enable save & resume or simplify form',
            })
        
        # Check problematic fields
        problematic = [
            f for f in performance['field_analytics']
            if f.get('is_problematic')
        ]
        if problematic:
            alerts.append({
                'type': 'problematic_fields',
                'severity': 'medium',
                'message': f'{len(problematic)} fields have high error/drop-off rates',
                'fields': [f['field_label'] for f in problematic],
                'recommendation': 'Review and simplify problematic fields',
            })
        
        # Check optimization score
        if performance['optimization_score']['total'] < 60:
            alerts.append({
                'type': 'low_optimization_score',
                'severity': 'medium',
                'message': f'Form optimization score is {performance["optimization_score"]["total"]}/100',
                'recommendation': 'Apply suggested optimizations',
            })
        
        return alerts
