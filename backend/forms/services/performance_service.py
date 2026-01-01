"""
Performance monitoring and optimization service
"""
from django.db.models import Avg, Count, Min, Max, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import logging

from forms.models_performance import (
    PerformanceMetric, FieldCompletionMetric, FormCacheConfig,
    PerformanceAlert, AssetOptimization
)

logger = logging.getLogger(__name__)


class PerformanceService:
    """Service for tracking and analyzing form performance"""
    
    # Performance thresholds
    THRESHOLDS = {
        'load_time': {'good': 2000, 'warning': 4000},  # ms
        'fcp': {'good': 1800, 'warning': 3000},
        'lcp': {'good': 2500, 'warning': 4000},
        'fid': {'good': 100, 'warning': 300},
        'cls': {'good': 0.1, 'warning': 0.25},
        'tti': {'good': 3800, 'warning': 7300},
    }
    
    @classmethod
    def record_metric(cls, form_id: str, metric_type: str, value: float, metadata: dict = None):
        """Record a performance metric"""
        metadata = metadata or {}
        
        metric = PerformanceMetric.objects.create(
            form_id=form_id,
            metric_type=metric_type,
            value=value,
            device_type=metadata.get('device_type', 'desktop'),
            connection_type=metadata.get('connection_type', 'wifi'),
            user_agent=metadata.get('user_agent', ''),
            browser=metadata.get('browser', ''),
            browser_version=metadata.get('browser_version', ''),
            os=metadata.get('os', ''),
            country=metadata.get('country', ''),
            region=metadata.get('region', ''),
        )
        
        # Check for performance alerts
        cls._check_alert(form_id, metric_type, value)
        
        return metric
    
    @classmethod
    def _check_alert(cls, form_id: str, metric_type: str, value: float):
        """Check if metric triggers an alert"""
        thresholds = cls.THRESHOLDS.get(metric_type)
        if not thresholds:
            return
        
        if value > thresholds['warning']:
            PerformanceAlert.objects.create(
                form_id=form_id,
                alert_type='slow_load',
                severity='warning' if value <= thresholds['warning'] * 1.5 else 'critical',
                message=f"{metric_type} is {value}ms, exceeding threshold of {thresholds['warning']}ms",
                metric_value=value,
                threshold_value=thresholds['warning'],
            )
    
    @classmethod
    def get_performance_dashboard(cls, form_id: str, days: int = 30):
        """Get comprehensive performance dashboard data"""
        start_date = timezone.now() - timedelta(days=days)
        
        metrics = PerformanceMetric.objects.filter(
            form_id=form_id,
            created_at__gte=start_date
        )
        
        # Aggregate by metric type
        aggregated = metrics.values('metric_type').annotate(
            avg_value=Avg('value'),
            min_value=Min('value'),
            max_value=Max('value'),
            count=Count('id'),
        )
        
        # Time series data
        time_series = metrics.annotate(
            date=TruncDate('created_at')
        ).values('date', 'metric_type').annotate(
            avg_value=Avg('value'),
            count=Count('id'),
        ).order_by('date')
        
        # Device breakdown
        device_breakdown = metrics.values('device_type').annotate(
            avg_load_time=Avg('value'),
            count=Count('id'),
        )
        
        # Calculate performance score
        performance_score = cls._calculate_performance_score(aggregated)
        
        # Get active alerts
        alerts = PerformanceAlert.objects.filter(
            form_id=form_id,
            is_acknowledged=False,
            created_at__gte=start_date
        ).order_by('-created_at')[:10]
        
        return {
            'performance_score': performance_score,
            'metrics': list(aggregated),
            'time_series': list(time_series),
            'device_breakdown': list(device_breakdown),
            'alerts': [
                {
                    'id': str(a.id),
                    'type': a.alert_type,
                    'severity': a.severity,
                    'message': a.message,
                    'created_at': a.created_at.isoformat(),
                }
                for a in alerts
            ],
            'recommendations': cls._generate_recommendations(aggregated),
        }
    
    @classmethod
    def _calculate_performance_score(cls, aggregated):
        """Calculate overall performance score (0-100)"""
        scores = []
        
        metric_dict = {m['metric_type']: m['avg_value'] for m in aggregated}
        
        for metric_type, thresholds in cls.THRESHOLDS.items():
            if metric_type in metric_dict:
                value = metric_dict[metric_type]
                if value <= thresholds['good']:
                    scores.append(100)
                elif value <= thresholds['warning']:
                    # Linear interpolation between good and warning
                    ratio = (thresholds['warning'] - value) / (thresholds['warning'] - thresholds['good'])
                    scores.append(50 + (ratio * 50))
                else:
                    # Below warning threshold
                    scores.append(max(0, 50 - ((value - thresholds['warning']) / thresholds['warning'] * 50)))
        
        return round(sum(scores) / len(scores), 1) if scores else 0
    
    @classmethod
    def _generate_recommendations(cls, aggregated):
        """Generate performance improvement recommendations"""
        recommendations = []
        metric_dict = {m['metric_type']: m['avg_value'] for m in aggregated}
        
        if metric_dict.get('lcp', 0) > cls.THRESHOLDS['lcp']['warning']:
            recommendations.append({
                'priority': 'high',
                'category': 'loading',
                'title': 'Optimize Largest Contentful Paint',
                'description': 'Your LCP is slow. Consider lazy loading images, optimizing images, or using a CDN.',
                'expected_impact': '15-30% faster page load',
            })
        
        if metric_dict.get('fid', 0) > cls.THRESHOLDS['fid']['warning']:
            recommendations.append({
                'priority': 'high',
                'category': 'interactivity',
                'title': 'Improve First Input Delay',
                'description': 'Users experience delay when interacting. Consider code splitting and reducing JavaScript.',
                'expected_impact': 'Better user experience',
            })
        
        if metric_dict.get('cls', 0) > cls.THRESHOLDS['cls']['warning']:
            recommendations.append({
                'priority': 'medium',
                'category': 'visual_stability',
                'title': 'Reduce Cumulative Layout Shift',
                'description': 'Layout is shifting during load. Set explicit dimensions for images and embeds.',
                'expected_impact': 'Improved visual stability',
            })
        
        return recommendations
    
    @classmethod
    def update_field_metrics(cls, form_id: str, field_data: list):
        """Update field completion metrics from batch data"""
        today = timezone.now().date()
        
        for field in field_data:
            metric, created = FieldCompletionMetric.objects.update_or_create(
                form_id=form_id,
                field_id=field['field_id'],
                date=today,
                defaults={
                    'field_label': field.get('label', ''),
                    'field_type': field.get('type', ''),
                    'avg_completion_time': field.get('avg_time', 0),
                    'min_completion_time': field.get('min_time', 0),
                    'max_completion_time': field.get('max_time', 0),
                    'total_interactions': F('total_interactions') + field.get('interactions', 0),
                    'total_completions': F('total_completions') + field.get('completions', 0),
                    'drop_off_count': F('drop_off_count') + field.get('drop_offs', 0),
                    'error_count': F('error_count') + field.get('errors', 0),
                }
            )
        
        return True
    
    @classmethod
    def get_field_performance(cls, form_id: str, days: int = 30):
        """Get field-level performance data"""
        start_date = timezone.now().date() - timedelta(days=days)
        
        metrics = FieldCompletionMetric.objects.filter(
            form_id=form_id,
            date__gte=start_date
        ).values('field_id', 'field_label', 'field_type').annotate(
            avg_time=Avg('avg_completion_time'),
            total_completions=Count('total_completions'),
            total_errors=Count('error_count'),
            avg_drop_off=Avg('drop_off_count'),
        ).order_by('avg_time')
        
        return list(metrics)


class CacheService:
    """Service for managing form caching"""
    
    @classmethod
    def get_or_create_config(cls, form_id: str):
        """Get or create cache configuration for a form"""
        config, created = FormCacheConfig.objects.get_or_create(
            form_id=form_id,
            defaults={
                'strategy': 'balanced',
                'cache_ttl': 3600,
            }
        )
        return config
    
    @classmethod
    def update_cache_config(cls, form_id: str, config_data: dict):
        """Update cache configuration"""
        config = cls.get_or_create_config(form_id)
        
        for key, value in config_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.save()
        return config
    
    @classmethod
    def purge_cache(cls, form_id: str):
        """Purge cache for a form"""
        config = cls.get_or_create_config(form_id)
        config.last_cache_purge = timezone.now()
        config.save()
        
        # Here you would integrate with your actual caching layer
        # e.g., Redis, CDN, etc.
        
        return True
    
    @classmethod
    def get_cache_stats(cls, form_id: str):
        """Get cache statistics for a form"""
        config = cls.get_or_create_config(form_id)
        
        # Get optimized assets
        assets = AssetOptimization.objects.filter(form_id=form_id)
        
        total_original_size = sum(a.original_size for a in assets)
        total_optimized_size = sum(a.optimized_size for a in assets)
        
        return {
            'strategy': config.strategy,
            'cache_ttl': config.cache_ttl,
            'last_purge': config.last_cache_purge,
            'lazy_loading_enabled': config.lazy_load_images and config.lazy_load_fields,
            'assets_optimized': assets.count(),
            'total_savings_bytes': total_original_size - total_optimized_size,
            'avg_compression_ratio': round(
                (1 - total_optimized_size / total_original_size) * 100, 2
            ) if total_original_size > 0 else 0,
        }


class ImageOptimizationService:
    """Service for optimizing uploaded images"""
    
    @classmethod
    def optimize_image(cls, form_id: str, original_url: str, image_data: bytes, config: dict = None):
        """Optimize an image and record the optimization"""
        config = config or {}
        
        # Here you would integrate with actual image optimization
        # e.g., Pillow, ImageMagick, or a cloud service
        
        original_size = len(image_data)
        
        # Simulated optimization result
        optimized_size = int(original_size * 0.7)  # Assume 30% reduction
        optimized_url = original_url.replace('/uploads/', '/optimized/')
        
        optimization = AssetOptimization.objects.create(
            form_id=form_id,
            original_url=original_url,
            optimized_url=optimized_url,
            original_size=original_size,
            optimized_size=optimized_size,
            compression_ratio=round((1 - optimized_size / original_size) * 100, 2),
            asset_type='image',
            format=config.get('format', 'webp'),
        )
        
        return optimization
