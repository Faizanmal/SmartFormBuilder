"""
A/B Testing service for form optimization
"""
import random
from django.utils import timezone
from django.db.models import F


class ABTestingService:
    """Service for managing A/B tests"""
    
    @staticmethod
    def get_variant_for_user(form, session_id):
        """Determine which variant to show to a user"""
        from forms.models_advanced import FormABTest
        
        # Get active A/B test for this form
        try:
            ab_test = FormABTest.objects.get(
                form=form,
                status='running',
                start_date__lte=timezone.now()
            )
        except FormABTest.DoesNotExist:
            return None, None
        
        # Use session ID to deterministically assign variant
        # This ensures same user gets same variant across sessions
        hash_value = hash(f"{ab_test.id}{session_id}")
        random_value = abs(hash_value) % 100
        
        if random_value < ab_test.traffic_split:
            variant = 'b'
            schema = ab_test.variant_b_schema
            # Increment variant B views
            FormABTest.objects.filter(id=ab_test.id).update(
                variant_b_views=F('variant_b_views') + 1
            )
        else:
            variant = 'a'
            schema = ab_test.variant_a_schema
            # Increment variant A views
            FormABTest.objects.filter(id=ab_test.id).update(
                variant_a_views=F('variant_a_views') + 1
            )
        
        return variant, schema
    
    @staticmethod
    def record_conversion(form, variant):
        """Record a successful submission for a variant"""
        from forms.models_advanced import FormABTest
        
        try:
            ab_test = FormABTest.objects.get(
                form=form,
                status='running'
            )
            
            if variant == 'a':
                FormABTest.objects.filter(id=ab_test.id).update(
                    variant_a_submissions=F('variant_a_submissions') + 1
                )
            elif variant == 'b':
                FormABTest.objects.filter(id=ab_test.id).update(
                    variant_b_submissions=F('variant_b_submissions') + 1
                )
        except FormABTest.DoesNotExist:
            pass
    
    @staticmethod
    def calculate_statistical_significance(variant_a_conversions, variant_a_views,
                                          variant_b_conversions, variant_b_views):
        """
        Calculate statistical significance using chi-square test
        Returns: (is_significant, p_value, confidence_level)
        """
        try:
            from scipy import stats
            
            # Create contingency table
            observed = [
                [variant_a_conversions, variant_a_views - variant_a_conversions],
                [variant_b_conversions, variant_b_views - variant_b_conversions]
            ]
            
            chi2, p_value, dof, expected = stats.chi2_contingency(observed)
            
            # Typically use 95% confidence (p < 0.05)
            is_significant = p_value < 0.05
            confidence_level = (1 - p_value) * 100
            
            return is_significant, p_value, confidence_level
        except Exception:
            # If scipy not available or calculation fails
            return False, 1.0, 0.0
    
    @staticmethod
    def get_test_results(ab_test):
        """Get comprehensive results for an A/B test"""
        variant_a_rate = ab_test.variant_a_conversion_rate
        variant_b_rate = ab_test.variant_b_conversion_rate
        
        improvement = 0
        if variant_a_rate > 0:
            improvement = ((variant_b_rate - variant_a_rate) / variant_a_rate) * 100
        
        is_significant, p_value, confidence = ABTestingService.calculate_statistical_significance(
            ab_test.variant_a_submissions, ab_test.variant_a_views,
            ab_test.variant_b_submissions, ab_test.variant_b_views
        )
        
        return {
            'variant_a': {
                'views': ab_test.variant_a_views,
                'submissions': ab_test.variant_a_submissions,
                'conversion_rate': variant_a_rate,
            },
            'variant_b': {
                'views': ab_test.variant_b_views,
                'submissions': ab_test.variant_b_submissions,
                'conversion_rate': variant_b_rate,
            },
            'improvement': round(improvement, 2),
            'is_significant': is_significant,
            'p_value': p_value,
            'confidence_level': round(confidence, 2),
            'recommended_winner': 'b' if variant_b_rate > variant_a_rate and is_significant else 'a'
        }
    
    @staticmethod
    def auto_declare_winner(ab_test, min_conversions=100):
        """Automatically declare a winner if conditions are met"""
        if ab_test.variant_a_submissions < min_conversions or ab_test.variant_b_submissions < min_conversions:
            return None  # Not enough data
        
        results = ABTestingService.get_test_results(ab_test)
        
        if results['is_significant']:
            winner = results['recommended_winner']
            ab_test.winner = winner
            ab_test.status = 'completed'
            ab_test.end_date = timezone.now()
            ab_test.save()
            return winner
        
        return None
