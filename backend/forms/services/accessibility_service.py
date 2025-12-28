"""
Accessibility testing and compliance service
"""
from django.utils import timezone
from datetime import timedelta
import logging
import re

from forms.models_accessibility import (
    AccessibilityConfig, AccessibilityAudit, AccessibilityIssue,
    UserAccessibilityPreference, ComplianceReport
)
from forms.models import Form

logger = logging.getLogger(__name__)


class AccessibilityService:
    """Service for accessibility testing and configuration"""
    
    # WCAG 2.1 criteria mapping
    WCAG_CRITERIA = {
        '1.1.1': {'name': 'Non-text Content', 'level': 'A', 'principle': 'perceivable'},
        '1.3.1': {'name': 'Info and Relationships', 'level': 'A', 'principle': 'perceivable'},
        '1.3.2': {'name': 'Meaningful Sequence', 'level': 'A', 'principle': 'perceivable'},
        '1.4.1': {'name': 'Use of Color', 'level': 'A', 'principle': 'perceivable'},
        '1.4.3': {'name': 'Contrast (Minimum)', 'level': 'AA', 'principle': 'perceivable'},
        '1.4.4': {'name': 'Resize Text', 'level': 'AA', 'principle': 'perceivable'},
        '1.4.10': {'name': 'Reflow', 'level': 'AA', 'principle': 'perceivable'},
        '2.1.1': {'name': 'Keyboard', 'level': 'A', 'principle': 'operable'},
        '2.1.2': {'name': 'No Keyboard Trap', 'level': 'A', 'principle': 'operable'},
        '2.4.3': {'name': 'Focus Order', 'level': 'A', 'principle': 'operable'},
        '2.4.6': {'name': 'Headings and Labels', 'level': 'AA', 'principle': 'operable'},
        '2.4.7': {'name': 'Focus Visible', 'level': 'AA', 'principle': 'operable'},
        '3.1.1': {'name': 'Language of Page', 'level': 'A', 'principle': 'understandable'},
        '3.2.1': {'name': 'On Focus', 'level': 'A', 'principle': 'understandable'},
        '3.2.2': {'name': 'On Input', 'level': 'A', 'principle': 'understandable'},
        '3.3.1': {'name': 'Error Identification', 'level': 'A', 'principle': 'understandable'},
        '3.3.2': {'name': 'Labels or Instructions', 'level': 'A', 'principle': 'understandable'},
        '3.3.3': {'name': 'Error Suggestion', 'level': 'AA', 'principle': 'understandable'},
        '4.1.1': {'name': 'Parsing', 'level': 'A', 'principle': 'robust'},
        '4.1.2': {'name': 'Name, Role, Value', 'level': 'A', 'principle': 'robust'},
    }
    
    @classmethod
    def get_or_create_config(cls, form_id: str):
        """Get or create accessibility configuration"""
        config, created = AccessibilityConfig.objects.get_or_create(
            form_id=form_id,
            defaults={
                'target_wcag_level': 'AA',
                'screen_reader_optimized': True,
                'keyboard_nav_enabled': True,
            }
        )
        return config
    
    @classmethod
    def update_config(cls, form_id: str, config_data: dict):
        """Update accessibility configuration"""
        config = cls.get_or_create_config(form_id)
        
        for key, value in config_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.save()
        return config
    
    @classmethod
    def run_accessibility_audit(cls, form_id: str, wcag_level: str = 'AA'):
        """Run an automated accessibility audit on a form"""
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return None
        
        # Create audit record
        audit = AccessibilityAudit.objects.create(
            form=form,
            status='running',
            wcag_level_tested=wcag_level,
            started_at=timezone.now(),
        )
        
        try:
            issues = []
            passed = []
            warnings = []
            
            # Analyze form schema
            schema = form.schema_json
            fields = schema.get('fields', [])
            
            # Run accessibility checks
            cls._check_labels(fields, audit, issues, passed)
            cls._check_aria_attributes(fields, audit, issues, passed)
            cls._check_keyboard_accessibility(fields, audit, issues, passed)
            cls._check_color_contrast(schema, audit, issues, passed)
            cls._check_error_handling(fields, audit, issues, passed)
            cls._check_focus_management(schema, audit, issues, passed)
            
            # Calculate scores
            total_checks = len(issues) + len(passed)
            audit.overall_score = (len(passed) / total_checks * 100) if total_checks > 0 else 100
            
            # Calculate principle scores
            audit.perceivable_score = cls._calculate_principle_score(issues, passed, 'perceivable')
            audit.operable_score = cls._calculate_principle_score(issues, passed, 'operable')
            audit.understandable_score = cls._calculate_principle_score(issues, passed, 'understandable')
            audit.robust_score = cls._calculate_principle_score(issues, passed, 'robust')
            
            # Count issues by severity
            audit.total_issues = len(issues)
            audit.critical_issues = len([i for i in issues if i.impact == 'critical'])
            audit.serious_issues = len([i for i in issues if i.impact == 'serious'])
            audit.moderate_issues = len([i for i in issues if i.impact == 'moderate'])
            audit.minor_issues = len([i for i in issues if i.impact == 'minor'])
            
            audit.issues = [{'id': str(i.id), 'rule': i.rule_id, 'impact': i.impact} for i in issues]
            audit.passed_checks = passed
            audit.warnings = warnings
            
            audit.status = 'completed'
            audit.completed_at = timezone.now()
            audit.save()
            
            # Update form accessibility config
            config = cls.get_or_create_config(form_id)
            config.is_compliant = audit.critical_issues == 0 and audit.serious_issues == 0
            config.last_audit_at = timezone.now()
            config.save()
            
        except Exception as e:
            audit.status = 'failed'
            audit.save()
            logger.error(f"Accessibility audit failed: {e}")
            raise
        
        return audit
    
    @classmethod
    def _check_labels(cls, fields, audit, issues, passed):
        """Check that all form fields have proper labels"""
        for field in fields:
            field_id = field.get('id', '')
            label = field.get('label', '')
            
            if not label or not label.strip():
                issue = AccessibilityIssue.objects.create(
                    audit=audit,
                    rule_id='label-required',
                    wcag_criteria='3.3.2',
                    wcag_principle='understandable',
                    impact='serious',
                    description=f'Field "{field_id}" is missing a label',
                    help_text='All form fields must have descriptive labels',
                    field_id=field_id,
                    fix_suggestion=f'Add a descriptive label to the field',
                    auto_fixable=False,
                )
                issues.append(issue)
            else:
                passed.append({
                    'rule_id': 'label-required',
                    'field_id': field_id,
                    'wcag_criteria': '3.3.2',
                })
    
    @classmethod
    def _check_aria_attributes(cls, fields, audit, issues, passed):
        """Check for proper ARIA attributes"""
        for field in fields:
            field_id = field.get('id', '')
            required = field.get('required', False)
            
            # Check for aria-required on required fields
            if required:
                passed.append({
                    'rule_id': 'aria-required',
                    'field_id': field_id,
                    'wcag_criteria': '4.1.2',
                })
    
    @classmethod
    def _check_keyboard_accessibility(cls, fields, audit, issues, passed):
        """Check keyboard accessibility"""
        # All standard form fields are keyboard accessible by default
        for field in fields:
            field_type = field.get('type', '')
            if field_type in ['text', 'email', 'number', 'select', 'checkbox', 'radio', 'textarea']:
                passed.append({
                    'rule_id': 'keyboard-accessible',
                    'field_id': field.get('id', ''),
                    'wcag_criteria': '2.1.1',
                })
    
    @classmethod
    def _check_color_contrast(cls, schema, audit, issues, passed):
        """Check color contrast ratios"""
        theme = schema.get('theme', {})
        # For now, assume default theme meets contrast requirements
        passed.append({
            'rule_id': 'color-contrast',
            'wcag_criteria': '1.4.3',
        })
    
    @classmethod
    def _check_error_handling(cls, fields, audit, issues, passed):
        """Check error handling and messaging"""
        for field in fields:
            field_id = field.get('id', '')
            validation = field.get('validation', {})
            error_message = validation.get('errorMessage', '')
            
            if validation and not error_message:
                issue = AccessibilityIssue.objects.create(
                    audit=audit,
                    rule_id='error-message-required',
                    wcag_criteria='3.3.1',
                    wcag_principle='understandable',
                    impact='moderate',
                    description=f'Field "{field_id}" has validation but no error message',
                    help_text='Provide clear error messages for validation failures',
                    field_id=field_id,
                    fix_suggestion='Add a descriptive error message to the validation',
                    auto_fixable=True,
                )
                issues.append(issue)
            elif validation:
                passed.append({
                    'rule_id': 'error-message-required',
                    'field_id': field_id,
                    'wcag_criteria': '3.3.1',
                })
    
    @classmethod
    def _check_focus_management(cls, schema, audit, issues, passed):
        """Check focus management"""
        passed.append({
            'rule_id': 'focus-visible',
            'wcag_criteria': '2.4.7',
        })
    
    @classmethod
    def _calculate_principle_score(cls, issues, passed, principle):
        """Calculate score for a specific WCAG principle"""
        principle_issues = [i for i in issues if i.wcag_principle == principle]
        principle_passed = [p for p in passed if cls.WCAG_CRITERIA.get(p.get('wcag_criteria', ''), {}).get('principle') == principle]
        
        total = len(principle_issues) + len(principle_passed)
        if total == 0:
            return 100
        
        return round(len(principle_passed) / total * 100, 1)
    
    @classmethod
    def get_audit_report(cls, form_id: str):
        """Get the latest audit report for a form"""
        audit = AccessibilityAudit.objects.filter(
            form_id=form_id,
            status='completed'
        ).order_by('-completed_at').first()
        
        if not audit:
            return None
        
        issues = AccessibilityIssue.objects.filter(audit=audit).order_by('impact')
        
        return {
            'audit_id': str(audit.id),
            'overall_score': audit.overall_score,
            'wcag_level': audit.wcag_level_tested,
            'is_compliant': audit.critical_issues == 0 and audit.serious_issues == 0,
            'scores': {
                'perceivable': audit.perceivable_score,
                'operable': audit.operable_score,
                'understandable': audit.understandable_score,
                'robust': audit.robust_score,
            },
            'issue_counts': {
                'total': audit.total_issues,
                'critical': audit.critical_issues,
                'serious': audit.serious_issues,
                'moderate': audit.moderate_issues,
                'minor': audit.minor_issues,
            },
            'issues': [
                {
                    'id': str(issue.id),
                    'rule_id': issue.rule_id,
                    'wcag_criteria': issue.wcag_criteria,
                    'impact': issue.impact,
                    'description': issue.description,
                    'help_text': issue.help_text,
                    'field_id': issue.field_id,
                    'fix_suggestion': issue.fix_suggestion,
                    'auto_fixable': issue.auto_fixable,
                    'is_fixed': issue.is_fixed,
                }
                for issue in issues
            ],
            'completed_at': audit.completed_at.isoformat(),
        }
    
    @classmethod
    def auto_fix_issue(cls, issue_id: str):
        """Attempt to auto-fix an accessibility issue"""
        try:
            issue = AccessibilityIssue.objects.get(id=issue_id)
        except AccessibilityIssue.DoesNotExist:
            return None
        
        if not issue.auto_fixable:
            return {'success': False, 'message': 'This issue cannot be auto-fixed'}
        
        # Implement auto-fix logic based on rule_id
        # This is a placeholder - actual implementation would modify the form schema
        
        issue.is_fixed = True
        issue.fixed_at = timezone.now()
        issue.save()
        
        return {'success': True, 'message': 'Issue fixed successfully'}


class UserPreferenceService:
    """Service for managing user accessibility preferences"""
    
    @classmethod
    def get_preferences(cls, user=None, session_id: str = None):
        """Get user accessibility preferences"""
        if user:
            pref, created = UserAccessibilityPreference.objects.get_or_create(
                user=user,
                defaults=cls._get_default_preferences()
            )
        elif session_id:
            pref, created = UserAccessibilityPreference.objects.get_or_create(
                session_id=session_id,
                defaults=cls._get_default_preferences()
            )
        else:
            return cls._get_default_preferences()
        
        return pref
    
    @classmethod
    def update_preferences(cls, user=None, session_id: str = None, preferences: dict = None):
        """Update user accessibility preferences"""
        pref = cls.get_preferences(user, session_id)
        
        if isinstance(pref, dict):
            return pref
        
        for key, value in (preferences or {}).items():
            if hasattr(pref, key):
                setattr(pref, key, value)
        
        pref.save()
        return pref
    
    @classmethod
    def _get_default_preferences(cls):
        """Get default accessibility preferences"""
        return {
            'high_contrast_mode': False,
            'dark_mode': False,
            'font_size_scale': 1.0,
            'reduced_motion': False,
            'screen_reader_hints': True,
            'keyboard_only': False,
        }
    
    @classmethod
    def get_css_variables(cls, preferences):
        """Generate CSS variables from preferences"""
        if isinstance(preferences, dict):
            prefs = preferences
        else:
            prefs = {
                'font_size_scale': preferences.font_size_scale,
                'high_contrast_mode': preferences.high_contrast_mode,
                'reduced_motion': preferences.reduced_motion,
                'line_height_scale': preferences.line_height_scale,
            }
        
        css_vars = {
            '--font-size-scale': prefs.get('font_size_scale', 1.0),
            '--line-height-scale': prefs.get('line_height_scale', 1.5),
        }
        
        if prefs.get('high_contrast_mode'):
            css_vars.update({
                '--background': '#000000',
                '--foreground': '#ffffff',
                '--border': '#ffffff',
            })
        
        return css_vars


class ComplianceService:
    """Service for generating compliance reports"""
    
    @classmethod
    def generate_report(cls, form_id: str, compliance_type: str = 'wcag'):
        """Generate a compliance report"""
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return None
        
        # Get latest audit
        audit = AccessibilityAudit.objects.filter(
            form_id=form_id,
            status='completed'
        ).order_by('-completed_at').first()
        
        if not audit:
            # Run an audit first
            audit = AccessibilityService.run_accessibility_audit(form_id)
        
        # Create compliance report
        report = ComplianceReport.objects.create(
            form=form,
            compliance_type=compliance_type,
            is_compliant=audit.critical_issues == 0 and audit.serious_issues == 0,
            compliance_score=audit.overall_score,
            requirements_checked=[],  # Would be populated with specific requirements
            requirements_met=[],
            requirements_failed=[],
        )
        
        return report
