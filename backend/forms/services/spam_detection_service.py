"""
Service for advanced bot and spam detection
"""
import logging
import re
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any

from forms.models_new_features import (
    SpamDetectionConfig, SpamDetectionLog, IPReputationCache
)

logger = logging.getLogger(__name__)


class SpamDetectionService:
    """Service for detecting and preventing spam submissions"""
    
    # Common spam patterns
    SPAM_PATTERNS = [
        r'(viagra|cialis|pharmacy)',
        r'(casino|poker|gambling)',
        r'(bitcoin|cryptocurrency|investment)',
        r'(click here|buy now|limited offer)',
        r'test@test\.com',
        r'123-?456-?7890',
        r'(aaaa|bbbb|cccc){4,}',  # Repeated characters
    ]
    
    @classmethod
    def analyze_submission(cls, form_id: str, submission_data: Dict[str, Any],
                          metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a submission for spam
        
        Args:
            form_id: Form ID
            submission_data: Form submission payload
            metadata: Request metadata (IP, user agent, timing, etc.)
            
        Returns:
            Dict with spam analysis results
        """
        try:
            config = SpamDetectionConfig.objects.get(form_id=form_id)
        except SpamDetectionConfig.DoesNotExist:
            # No spam detection configured
            return {
                'is_spam': False,
                'risk_score': 0,
                'action': 'allowed'
            }
        
        risk_score = 0
        detection_reasons = []
        checks = {
            'honeypot_triggered': False,
            'timing_suspicious': False,
            'pattern_matched': False,
            'ip_blacklisted': False,
            'behavioral_suspicious': False
        }
        
        # 1. Honeypot check
        if config.honeypot_enabled:
            honeypot_result = cls._check_honeypot(submission_data, config.honeypot_field_name)
            if honeypot_result:
                risk_score += 50
                checks['honeypot_triggered'] = True
                detection_reasons.append('Honeypot field filled')
        
        # 2. Timing analysis
        if config.timing_analysis_enabled:
            fill_time = metadata.get('fill_time_seconds', 0)
            if fill_time < config.min_fill_time_seconds:
                risk_score += 30
                checks['timing_suspicious'] = True
                detection_reasons.append(f'Too fast: {fill_time}s')
            elif fill_time > config.max_fill_time_seconds:
                risk_score += 10
                checks['timing_suspicious'] = True
                detection_reasons.append(f'Too slow: {fill_time}s')
        
        # 3. Pattern detection
        if config.pattern_detection_enabled:
            pattern_result = cls._check_patterns(submission_data, config)
            risk_score += pattern_result['score']
            if pattern_result['matched']:
                checks['pattern_matched'] = True
                detection_reasons.extend(pattern_result['reasons'])
        
        # 4. IP reputation
        if config.ip_reputation_enabled:
            ip_address = metadata.get('ip_address')
            if ip_address:
                ip_result = cls._check_ip_reputation(ip_address)
                risk_score += ip_result['score']
                if ip_result['is_bad']:
                    checks['ip_blacklisted'] = True
                    detection_reasons.extend(ip_result['reasons'])
        
        # 5. Behavioral analysis
        if config.behavioral_analysis_enabled:
            behavioral_result = cls._check_behavioral(metadata)
            risk_score += behavioral_result['score']
            if behavioral_result['suspicious']:
                checks['behavioral_suspicious'] = True
                detection_reasons.extend(behavioral_result['reasons'])
        
        # Determine action
        is_spam = risk_score >= config.risk_score_threshold
        
        if is_spam:
            action = config.action_on_detection
        else:
            action = 'allowed'
        
        # Log the detection
        SpamDetectionLog.objects.create(
            form_id=form_id,
            risk_score=min(risk_score, 100),
            is_spam=is_spam,
            detection_reasons=detection_reasons,
            honeypot_triggered=checks['honeypot_triggered'],
            timing_suspicious=checks['timing_suspicious'],
            pattern_matched=checks['pattern_matched'],
            ip_blacklisted=checks['ip_blacklisted'],
            behavioral_suspicious=checks['behavioral_suspicious'],
            ip_address=metadata.get('ip_address'),
            user_agent=metadata.get('user_agent', ''),
            fill_time_seconds=metadata.get('fill_time_seconds', 0),
            mouse_movements=metadata.get('mouse_movements', 0),
            keystrokes=metadata.get('keystrokes', 0),
            field_interactions=metadata.get('field_interactions', 0),
            action_taken=action
        )
        
        return {
            'is_spam': is_spam,
            'risk_score': min(risk_score, 100),
            'action': action,
            'reasons': detection_reasons,
            'checks': checks
        }
    
    @classmethod
    def _check_honeypot(cls, submission_data: Dict, honeypot_field: str) -> bool:
        """Check if honeypot field was filled (indicates bot)"""
        return honeypot_field in submission_data and submission_data[honeypot_field]
    
    @classmethod
    def _check_patterns(cls, submission_data: Dict, config: SpamDetectionConfig) -> Dict:
        """Check submission data against spam patterns"""
        score = 0
        reasons = []
        matched = False
        
        # Combine all text values
        all_text = ' '.join([str(v) for v in submission_data.values() if isinstance(v, str)])
        all_text = all_text.lower()
        
        # Check against built-in patterns
        for pattern in cls.SPAM_PATTERNS:
            if re.search(pattern, all_text, re.IGNORECASE):
                score += 15
                matched = True
                reasons.append(f'Spam pattern matched: {pattern}')
        
        # Check against custom patterns
        for pattern in config.suspicious_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                score += 20
                matched = True
                reasons.append('Custom pattern matched')
        
        # Check blacklisted emails
        for field_value in submission_data.values():
            if isinstance(field_value, str) and '@' in field_value:
                email = field_value.lower()
                if email in config.blacklisted_emails:
                    score += 40
                    matched = True
                    reasons.append('Blacklisted email')
                
                # Check domain
                domain = email.split('@')[1] if '@' in email else ''
                if domain in config.blacklisted_domains:
                    score += 40
                    matched = True
                    reasons.append('Blacklisted email domain')
        
        return {
            'score': score,
            'matched': matched,
            'reasons': reasons
        }
    
    @classmethod
    def _check_ip_reputation(cls, ip_address: str) -> Dict:
        """Check IP address reputation"""
        score = 0
        reasons = []
        is_bad = False
        
        # Check cache first
        try:
            ip_cache = IPReputationCache.objects.get(
                ip_address=ip_address,
                expires_at__gt=timezone.now()
            )
            
            if ip_cache.reputation_score < 30:
                score += 25
                is_bad = True
                reasons.append('Low IP reputation')
            
            if ip_cache.is_vpn or ip_cache.is_proxy:
                score += 15
                reasons.append('VPN/Proxy detected')
            
            if ip_cache.is_tor:
                score += 30
                is_bad = True
                reasons.append('Tor exit node')
            
            # Update usage stats
            ip_cache.total_submissions += 1
            ip_cache.save()
            
        except IPReputationCache.DoesNotExist:
            # Create new cache entry with default reputation
            ip_cache = IPReputationCache.objects.create(
                ip_address=ip_address,
                reputation_score=50,
                total_submissions=1,
                expires_at=timezone.now() + timedelta(days=7)
            )
        
        return {
            'score': score,
            'is_bad': is_bad,
            'reasons': reasons
        }
    
    @classmethod
    def _check_behavioral(cls, metadata: Dict) -> Dict:
        """Check behavioral patterns"""
        score = 0
        reasons = []
        suspicious = False
        
        mouse_movements = metadata.get('mouse_movements', 0)
        keystrokes = metadata.get('keystrokes', 0)
        field_interactions = metadata.get('field_interactions', 0)
        
        # Very low interaction indicates bot
        if mouse_movements < 10 and keystrokes < 20:
            score += 20
            suspicious = True
            reasons.append('Very low user interaction')
        
        # No field interactions is suspicious
        if field_interactions == 0:
            score += 15
            suspicious = True
            reasons.append('No field interactions detected')
        
        return {
            'score': score,
            'suspicious': suspicious,
            'reasons': reasons
        }
    
    @classmethod
    def mark_ip_as_spam(cls, ip_address: str):
        """Mark an IP address as spam source"""
        try:
            ip_cache = IPReputationCache.objects.get(ip_address=ip_address)
            ip_cache.spam_submissions += 1
            ip_cache.reputation_score = max(0, ip_cache.reputation_score - 10)
            ip_cache.save()
        except IPReputationCache.DoesNotExist:
            IPReputationCache.objects.create(
                ip_address=ip_address,
                reputation_score=20,
                spam_submissions=1,
                total_submissions=1,
                expires_at=timezone.now() + timedelta(days=7)
            )
    
    @classmethod
    def get_spam_statistics(cls, form_id: str, days: int = 30) -> Dict:
        """Get spam detection statistics for a form"""
        start_date = timezone.now() - timedelta(days=days)
        
        logs = SpamDetectionLog.objects.filter(
            form_id=form_id,
            created_at__gte=start_date
        )
        
        total = logs.count()
        spam_count = logs.filter(is_spam=True).count()
        blocked = logs.filter(action_taken='blocked').count()
        flagged = logs.filter(action_taken='flagged').count()
        
        return {
            'total_submissions': total,
            'spam_detected': spam_count,
            'spam_rate': (spam_count / total * 100) if total > 0 else 0,
            'blocked': blocked,
            'flagged': flagged,
            'allowed': total - blocked
        }
