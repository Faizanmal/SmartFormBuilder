"""
Data quality, validation, and duplicate detection service
"""
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
import re
import logging
from difflib import SequenceMatcher

from forms.models_data_quality import (
    DataQualityScore, DuplicateDetection, ExternalValidation,
    DataCleansingRule, DataCleansingLog, ExportWithQuality
)
from forms.models import Submission

logger = logging.getLogger(__name__)


class DataQualityService:
    """Service for data quality scoring and analysis"""
    
    @classmethod
    def calculate_quality_score(cls, submission_id: str):
        """Calculate data quality score for a submission"""
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return None
        
        form = submission.form
        schema = form.schema_json
        fields = schema.get('fields', [])
        payload = submission.payload_json
        
        # Initialize scores
        completeness_issues = []
        accuracy_issues = []
        validity_issues = []
        field_scores = {}
        
        for field in fields:
            field_id = field.get('id', '')
            field_type = field.get('type', '')
            required = field.get('required', False)
            value = payload.get(field_id)
            
            field_score = 100
            issues = []
            
            # Check completeness
            if required and (value is None or value == ''):
                field_score -= 50
                issues.append({'type': 'completeness', 'message': 'Required field is empty'})
                completeness_issues.append(field_id)
            
            # Check accuracy based on field type
            if value:
                accuracy_result = cls._check_field_accuracy(field_type, value)
                if not accuracy_result['valid']:
                    field_score -= 30
                    issues.append({'type': 'accuracy', 'message': accuracy_result['message']})
                    accuracy_issues.append(field_id)
            
            field_scores[field_id] = {
                'score': max(0, field_score),
                'issues': issues,
            }
        
        # Calculate overall scores
        total_fields = len(fields)
        required_fields = len([f for f in fields if f.get('required', False)])
        
        completeness_score = (
            (required_fields - len(completeness_issues)) / required_fields * 100
        ) if required_fields > 0 else 100
        
        accuracy_score = (
            (total_fields - len(accuracy_issues)) / total_fields * 100
        ) if total_fields > 0 else 100
        
        # Get external validation results
        validations = ExternalValidation.objects.filter(submission=submission)
        valid_count = validations.filter(is_valid=True).count()
        validity_score = (valid_count / validations.count() * 100) if validations.count() > 0 else 100
        
        # Calculate overall score
        overall_score = (
            completeness_score * 0.4 +
            accuracy_score * 0.4 +
            validity_score * 0.2
        )
        
        # Create or update quality score
        quality_score, created = DataQualityScore.objects.update_or_create(
            submission=submission,
            defaults={
                'overall_score': round(overall_score, 2),
                'completeness_score': round(completeness_score, 2),
                'accuracy_score': round(accuracy_score, 2),
                'validity_score': round(validity_score, 2),
                'total_issues': len(completeness_issues) + len(accuracy_issues),
                'issues': completeness_issues + accuracy_issues,
                'field_scores': field_scores,
            }
        )
        
        return quality_score
    
    @classmethod
    def _check_field_accuracy(cls, field_type: str, value) -> dict:
        """Check field value accuracy based on type"""
        if field_type == 'email':
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, str(value)):
                return {'valid': False, 'message': 'Invalid email format'}
        
        elif field_type == 'phone':
            # Basic phone validation
            cleaned = re.sub(r'[\s\-\(\)]', '', str(value))
            if not re.match(r'^\+?[0-9]{10,15}$', cleaned):
                return {'valid': False, 'message': 'Invalid phone format'}
        
        elif field_type == 'url':
            pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(pattern, str(value)):
                return {'valid': False, 'message': 'Invalid URL format'}
        
        return {'valid': True, 'message': ''}
    
    @classmethod
    def get_form_quality_summary(cls, form_id: str, days: int = 30):
        """Get quality summary for all submissions of a form"""
        start_date = timezone.now() - timedelta(days=days)
        
        scores = DataQualityScore.objects.filter(
            submission__form_id=form_id,
            submission__created_at__gte=start_date
        )
        
        if not scores.exists():
            return {
                'avg_quality_score': 0,
                'total_submissions': 0,
                'quality_distribution': {},
            }
        
        avg_scores = scores.aggregate(
            avg_overall=Avg('overall_score'),
            avg_completeness=Avg('completeness_score'),
            avg_accuracy=Avg('accuracy_score'),
            avg_validity=Avg('validity_score'),
        )
        
        # Calculate distribution
        excellent = scores.filter(overall_score__gte=90).count()
        good = scores.filter(overall_score__gte=70, overall_score__lt=90).count()
        fair = scores.filter(overall_score__gte=50, overall_score__lt=70).count()
        poor = scores.filter(overall_score__lt=50).count()
        
        return {
            'avg_quality_score': round(avg_scores['avg_overall'] or 0, 2),
            'avg_completeness': round(avg_scores['avg_completeness'] or 0, 2),
            'avg_accuracy': round(avg_scores['avg_accuracy'] or 0, 2),
            'avg_validity': round(avg_scores['avg_validity'] or 0, 2),
            'total_submissions': scores.count(),
            'quality_distribution': {
                'excellent': excellent,
                'good': good,
                'fair': fair,
                'poor': poor,
            },
        }


class DuplicateDetectionService:
    """Service for detecting and managing duplicate submissions"""
    
    # Similarity threshold for duplicate detection
    SIMILARITY_THRESHOLD = 0.85
    
    @classmethod
    def check_for_duplicates(cls, submission_id: str):
        """Check if a submission is a duplicate of existing submissions"""
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return []
        
        form = submission.form
        payload = submission.payload_json
        
        # Get recent submissions for the same form
        recent_submissions = Submission.objects.filter(
            form=form,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).exclude(id=submission_id)
        
        duplicates = []
        
        for other in recent_submissions:
            similarity = cls._calculate_similarity(payload, other.payload_json)
            
            if similarity >= cls.SIMILARITY_THRESHOLD:
                # Create duplicate detection record
                detection, created = DuplicateDetection.objects.get_or_create(
                    submission_a=submission,
                    submission_b=other,
                    defaults={
                        'form': form,
                        'similarity_score': round(similarity * 100, 2),
                        'matching_fields': cls._get_matching_fields(payload, other.payload_json),
                        'differing_fields': cls._get_differing_fields(payload, other.payload_json),
                    }
                )
                
                duplicates.append({
                    'detection_id': str(detection.id),
                    'other_submission_id': str(other.id),
                    'similarity_score': detection.similarity_score,
                    'matching_fields': detection.matching_fields,
                })
        
        return duplicates
    
    @classmethod
    def _calculate_similarity(cls, payload1: dict, payload2: dict) -> float:
        """Calculate similarity between two payloads"""
        if not payload1 or not payload2:
            return 0
        
        all_keys = set(payload1.keys()) | set(payload2.keys())
        if not all_keys:
            return 0
        
        matching = 0
        total_weight = 0
        
        for key in all_keys:
            val1 = str(payload1.get(key, '')).lower().strip()
            val2 = str(payload2.get(key, '')).lower().strip()
            
            # Weight important fields higher
            weight = 2 if key in ['email', 'phone', 'name'] else 1
            total_weight += weight
            
            if val1 and val2:
                similarity = SequenceMatcher(None, val1, val2).ratio()
                matching += similarity * weight
        
        return matching / total_weight if total_weight > 0 else 0
    
    @classmethod
    def _get_matching_fields(cls, payload1: dict, payload2: dict) -> list:
        """Get list of fields that match between payloads"""
        matching = []
        for key in payload1.keys():
            if key in payload2:
                val1 = str(payload1.get(key, '')).lower().strip()
                val2 = str(payload2.get(key, '')).lower().strip()
                if val1 == val2 and val1:
                    matching.append(key)
        return matching
    
    @classmethod
    def _get_differing_fields(cls, payload1: dict, payload2: dict) -> list:
        """Get list of fields that differ between payloads"""
        differing = []
        all_keys = set(payload1.keys()) | set(payload2.keys())
        
        for key in all_keys:
            val1 = str(payload1.get(key, '')).lower().strip()
            val2 = str(payload2.get(key, '')).lower().strip()
            if val1 != val2:
                differing.append({
                    'field': key,
                    'value_a': payload1.get(key),
                    'value_b': payload2.get(key),
                })
        return differing
    
    @classmethod
    def merge_duplicates(cls, detection_id: str, keep_submission_id: str, user):
        """Merge duplicate submissions"""
        try:
            detection = DuplicateDetection.objects.get(id=detection_id)
        except DuplicateDetection.DoesNotExist:
            return None
        
        # Determine which submission to keep
        if str(detection.submission_a.id) == keep_submission_id:
            keep = detection.submission_a
            discard = detection.submission_b
        else:
            keep = detection.submission_b
            discard = detection.submission_a
        
        # Merge any unique data from discarded submission
        for key, value in discard.payload_json.items():
            if key not in keep.payload_json or not keep.payload_json[key]:
                keep.payload_json[key] = value
        
        keep.save()
        
        # Update detection status
        detection.status = 'merged'
        detection.resolved_by = user
        detection.merged_into = keep
        detection.resolved_at = timezone.now()
        detection.save()
        
        return detection


class ExternalValidationService:
    """Service for external API validations (email, phone, address)"""
    
    @classmethod
    def validate_email(cls, submission_id: str, field_id: str, email: str):
        """Validate an email address using external service"""
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return None
        
        # Basic validation (in production, integrate with email verification API)
        is_valid = cls._basic_email_validation(email)
        
        validation = ExternalValidation.objects.create(
            submission=submission,
            field_id=field_id,
            field_value=email,
            validation_type='email',
            status='valid' if is_valid else 'invalid',
            is_valid=is_valid,
            confidence_score=95 if is_valid else 10,
            validation_result={
                'format_valid': is_valid,
                'domain_exists': is_valid,
                'is_disposable': False,
            },
            provider='internal',
            validated_at=timezone.now(),
        )
        
        return validation
    
    @classmethod
    def _basic_email_validation(cls, email: str) -> bool:
        """Basic email format validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_phone(cls, submission_id: str, field_id: str, phone: str):
        """Validate a phone number using external service"""
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return None
        
        # Basic validation
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        is_valid = bool(re.match(r'^\+?[0-9]{10,15}$', cleaned))
        
        validation = ExternalValidation.objects.create(
            submission=submission,
            field_id=field_id,
            field_value=phone,
            validation_type='phone',
            status='valid' if is_valid else 'invalid',
            is_valid=is_valid,
            confidence_score=90 if is_valid else 10,
            validation_result={
                'format_valid': is_valid,
                'country_code': cleaned[:2] if cleaned.startswith('+') else None,
            },
            corrected_value=cleaned if is_valid else '',
            provider='internal',
            validated_at=timezone.now(),
        )
        
        return validation
    
    @classmethod
    def validate_address(cls, submission_id: str, field_id: str, address: dict):
        """Validate an address using external service"""
        # In production, integrate with address validation API (Google, SmartyStreets, etc.)
        pass


class DataCleansingService:
    """Service for data cleansing and standardization"""
    
    @classmethod
    def apply_cleansing_rules(cls, submission_id: str):
        """Apply all active cleansing rules to a submission"""
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return None
        
        form = submission.form
        rules = DataCleansingRule.objects.filter(
            form=form,
            is_active=True,
            apply_on_submit=True
        ).order_by('order')
        
        payload = submission.payload_json.copy()
        logs = []
        
        for rule in rules:
            target_fields = rule.target_field_ids if not rule.apply_to_all else list(payload.keys())
            
            for field_id in target_fields:
                if field_id in payload and payload[field_id]:
                    original_value = payload[field_id]
                    cleansed_value = cls._apply_rule(rule.rule_type, original_value, rule.config)
                    
                    if cleansed_value != original_value:
                        payload[field_id] = cleansed_value
                        
                        log = DataCleansingLog.objects.create(
                            submission=submission,
                            rule=rule,
                            field_id=field_id,
                            original_value=str(original_value),
                            cleansed_value=str(cleansed_value),
                        )
                        logs.append(log)
        
        # Update submission with cleansed data
        if logs:
            submission.payload_json = payload
            submission.save()
        
        return logs
    
    @classmethod
    def _apply_rule(cls, rule_type: str, value, config: dict):
        """Apply a specific cleansing rule to a value"""
        if not isinstance(value, str):
            value = str(value)
        
        if rule_type == 'trim':
            return value.strip()
        
        elif rule_type == 'lowercase':
            return value.lower()
        
        elif rule_type == 'uppercase':
            return value.upper()
        
        elif rule_type == 'titlecase':
            return value.title()
        
        elif rule_type == 'phone_format':
            # Format phone numbers consistently
            cleaned = re.sub(r'[\s\-\(\)]', '', value)
            if len(cleaned) == 10:
                return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
            return value
        
        elif rule_type == 'remove_special':
            return re.sub(r'[^a-zA-Z0-9\s]', '', value)
        
        elif rule_type == 'regex_replace':
            pattern = config.get('pattern', '')
            replacement = config.get('replacement', '')
            if pattern:
                return re.sub(pattern, replacement, value)
        
        return value
    
    @classmethod
    def create_rule(cls, form_id: str, rule_data: dict):
        """Create a new cleansing rule"""
        return DataCleansingRule.objects.create(
            form_id=form_id,
            name=rule_data['name'],
            rule_type=rule_data['rule_type'],
            target_field_ids=rule_data.get('target_field_ids', []),
            apply_to_all=rule_data.get('apply_to_all', False),
            config=rule_data.get('config', {}),
        )


class QualityExportService:
    """Service for exporting data with quality scores"""
    
    @classmethod
    def create_export(cls, form_id: str, user, export_config: dict):
        """Create an export job with quality filtering"""
        export = ExportWithQuality.objects.create(
            form_id=form_id,
            user=user,
            format=export_config.get('format', 'csv'),
            include_quality_scores=export_config.get('include_quality_scores', True),
            include_validation_results=export_config.get('include_validation_results', True),
            min_quality_score=export_config.get('min_quality_score', 0),
            date_from=export_config.get('date_from'),
            date_to=export_config.get('date_to'),
            status='pending',
        )
        
        # In production, this would be handled by Celery
        cls._process_export(export)
        
        return export
    
    @classmethod
    def _process_export(cls, export):
        """Process the export job"""
        export.status = 'processing'
        export.started_at = timezone.now()
        export.save()
        
        try:
            # Get submissions
            queryset = Submission.objects.filter(form=export.form)
            
            if export.date_from:
                queryset = queryset.filter(created_at__gte=export.date_from)
            if export.date_to:
                queryset = queryset.filter(created_at__lte=export.date_to)
            
            export.total_records = queryset.count()
            
            # Filter by quality score
            if export.min_quality_score > 0:
                # Get submissions with quality scores above threshold
                quality_submission_ids = DataQualityScore.objects.filter(
                    overall_score__gte=export.min_quality_score
                ).values_list('submission_id', flat=True)
                
                queryset = queryset.filter(id__in=quality_submission_ids)
            
            export.exported_records = queryset.count()
            export.excluded_records = export.total_records - export.exported_records
            
            # Calculate average quality
            avg_quality = DataQualityScore.objects.filter(
                submission__in=queryset
            ).aggregate(avg=Avg('overall_score'))
            export.avg_quality_score = avg_quality['avg'] or 0
            
            # Generate export file (simplified - in production would create actual file)
            export.file_url = f"/exports/{export.id}.{export.format}"
            
            export.status = 'completed'
            export.completed_at = timezone.now()
            
        except Exception as e:
            export.status = 'failed'
            export.error_message = str(e)
            logger.error(f"Export failed: {e}")
        
        export.save()
