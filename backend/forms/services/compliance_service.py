"""
Automated Compliance and Accessibility Scanner Service
Scans forms for GDPR, WCAG, and industry compliance
"""
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
from django.conf import settings
from openai import OpenAI


class ComplianceService:
    """
    Service for automated compliance and accessibility scanning.
    Checks forms for GDPR, WCAG, HIPAA, and other standards.
    """
    
    # WCAG 2.1 color contrast requirements
    WCAG_AA_CONTRAST_NORMAL = 4.5
    WCAG_AA_CONTRAST_LARGE = 3.0
    WCAG_AAA_CONTRAST_NORMAL = 7.0
    WCAG_AAA_CONTRAST_LARGE = 4.5
    
    # Common compliance keywords
    GDPR_KEYWORDS = [
        'consent', 'privacy', 'data protection', 'personal data',
        'opt-in', 'opt-out', 'unsubscribe', 'right to be forgotten',
    ]
    
    HIPAA_KEYWORDS = [
        'health', 'medical', 'patient', 'diagnosis', 'treatment',
        'prescription', 'insurance', 'social security',
    ]
    
    PCI_KEYWORDS = [
        'credit card', 'card number', 'cvv', 'expiration', 'payment',
        'billing', 'cardholder',
    ]
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
    
    def scan_form(
        self,
        form,
        compliance_types: List[str] = None,
        wcag_level: str = 'AA',
    ) -> Dict[str, Any]:
        """
        Comprehensive compliance scan of a form
        
        Args:
            form: Form model instance
            compliance_types: List of compliance types to check ('gdpr', 'wcag', 'hipaa', 'pci')
            wcag_level: WCAG compliance level ('A', 'AA', 'AAA')
            
        Returns:
            Detailed compliance report
        """
        if compliance_types is None:
            compliance_types = ['gdpr', 'wcag']
        
        schema = form.schema_json
        results = {
            'form_id': str(form.id),
            'form_title': form.title,
            'scan_timestamp': datetime.now().isoformat(),
            'compliance_score': 0,
            'issues': [],
            'warnings': [],
            'passed': [],
            'recommendations': [],
            'auto_fixes': [],
        }
        
        # Run compliance checks
        if 'gdpr' in compliance_types:
            gdpr_results = self._check_gdpr_compliance(schema)
            results['gdpr'] = gdpr_results
            results['issues'].extend(gdpr_results.get('issues', []))
            results['warnings'].extend(gdpr_results.get('warnings', []))
            results['passed'].extend(gdpr_results.get('passed', []))
            results['recommendations'].extend(gdpr_results.get('recommendations', []))
            results['auto_fixes'].extend(gdpr_results.get('auto_fixes', []))
        
        if 'wcag' in compliance_types:
            wcag_results = self._check_wcag_compliance(schema, wcag_level)
            results['wcag'] = wcag_results
            results['issues'].extend(wcag_results.get('issues', []))
            results['warnings'].extend(wcag_results.get('warnings', []))
            results['passed'].extend(wcag_results.get('passed', []))
            results['recommendations'].extend(wcag_results.get('recommendations', []))
            results['auto_fixes'].extend(wcag_results.get('auto_fixes', []))
        
        if 'hipaa' in compliance_types:
            hipaa_results = self._check_hipaa_compliance(schema)
            results['hipaa'] = hipaa_results
            results['issues'].extend(hipaa_results.get('issues', []))
            results['warnings'].extend(hipaa_results.get('warnings', []))
            results['passed'].extend(hipaa_results.get('passed', []))
            results['recommendations'].extend(hipaa_results.get('recommendations', []))
        
        if 'pci' in compliance_types:
            pci_results = self._check_pci_compliance(schema)
            results['pci'] = pci_results
            results['issues'].extend(pci_results.get('issues', []))
            results['warnings'].extend(pci_results.get('warnings', []))
            results['passed'].extend(pci_results.get('passed', []))
            results['recommendations'].extend(pci_results.get('recommendations', []))
        
        # Calculate overall score
        total_checks = len(results['issues']) + len(results['warnings']) + len(results['passed'])
        if total_checks > 0:
            results['compliance_score'] = round(
                (len(results['passed']) / total_checks) * 100, 1
            )
        
        # Add grade
        results['grade'] = self._get_compliance_grade(results['compliance_score'])
        
        return results
    
    def _check_gdpr_compliance(self, schema: Dict) -> Dict[str, Any]:
        """Check GDPR compliance"""
        results = {
            'issues': [],
            'warnings': [],
            'passed': [],
            'recommendations': [],
            'auto_fixes': [],
        }
        
        fields = schema.get('fields', [])
        settings_config = schema.get('settings', {})
        
        # Check 1: Consent checkbox
        has_consent = any(
            f.get('type') == 'checkbox' and 
            any(kw in f.get('label', '').lower() for kw in ['consent', 'agree', 'privacy', 'terms'])
            for f in fields
        )
        
        if has_consent:
            results['passed'].append({
                'rule': 'gdpr_consent',
                'message': 'Form includes consent checkbox',
                'severity': 'info',
            })
        else:
            results['issues'].append({
                'rule': 'gdpr_consent',
                'message': 'Missing explicit consent checkbox for data collection',
                'severity': 'high',
                'recommendation': 'Add a required checkbox for consent to data processing',
            })
            results['auto_fixes'].append({
                'action': 'add_field',
                'field': {
                    'id': 'consent_gdpr',
                    'type': 'checkbox',
                    'label': 'I consent to the processing of my personal data',
                    'required': True,
                    'help': 'Required for GDPR compliance',
                },
            })
        
        # Check 2: Privacy policy link
        has_privacy_link = bool(settings_config.get('privacy_url')) or any(
            'privacy' in str(f.get('help', '')).lower() or 
            'privacy' in str(f.get('label', '')).lower()
            for f in fields
        )
        
        if has_privacy_link:
            results['passed'].append({
                'rule': 'gdpr_privacy_policy',
                'message': 'Privacy policy reference found',
                'severity': 'info',
            })
        else:
            results['warnings'].append({
                'rule': 'gdpr_privacy_policy',
                'message': 'No privacy policy link found',
                'severity': 'medium',
                'recommendation': 'Add a link to your privacy policy',
            })
        
        # Check 3: Data minimization - check for unnecessary fields
        sensitive_fields = []
        for field in fields:
            label = field.get('label', '').lower()
            field_type = field.get('type', '')
            
            # Check for potentially unnecessary sensitive data
            if any(kw in label for kw in ['social security', 'ssn', 'passport', 'driver']):
                if not field.get('required'):
                    results['passed'].append({
                        'rule': 'gdpr_data_minimization',
                        'message': f'Sensitive field "{field.get("label")}" is optional',
                        'severity': 'info',
                    })
                else:
                    sensitive_fields.append(field.get('label'))
        
        if sensitive_fields:
            results['warnings'].append({
                'rule': 'gdpr_data_minimization',
                'message': f'Sensitive required fields: {", ".join(sensitive_fields)}',
                'severity': 'medium',
                'recommendation': 'Consider if all sensitive data is necessary',
            })
        
        # Check 4: Purpose specification
        has_description = bool(schema.get('description'))
        if has_description:
            results['passed'].append({
                'rule': 'gdpr_purpose_specification',
                'message': 'Form includes description explaining data use',
                'severity': 'info',
            })
        else:
            results['warnings'].append({
                'rule': 'gdpr_purpose_specification',
                'message': 'Form lacks description explaining purpose of data collection',
                'severity': 'low',
                'recommendation': 'Add a description explaining why data is collected',
            })
        
        # Check 5: Right to withdraw
        has_withdraw_info = 'withdraw' in str(schema).lower() or 'unsubscribe' in str(schema).lower()
        if not has_withdraw_info:
            results['recommendations'].append({
                'rule': 'gdpr_withdrawal',
                'message': 'Consider adding information about right to withdraw consent',
                'severity': 'low',
            })
        
        return results
    
    def _check_wcag_compliance(
        self, schema: Dict, level: str = 'AA'
    ) -> Dict[str, Any]:
        """Check WCAG accessibility compliance"""
        results = {
            'issues': [],
            'warnings': [],
            'passed': [],
            'recommendations': [],
            'auto_fixes': [],
        }
        
        fields = schema.get('fields', [])
        
        for field in fields:
            field_id = field.get('id')
            field_label = field.get('label', '')
            field_type = field.get('type')
            
            # Check 1: Labels (WCAG 1.3.1, 3.3.2)
            if not field_label:
                results['issues'].append({
                    'rule': 'wcag_1.3.1',
                    'field_id': field_id,
                    'message': f'Field "{field_id}" missing label',
                    'severity': 'high',
                    'wcag_criterion': '1.3.1 Info and Relationships',
                })
                results['auto_fixes'].append({
                    'action': 'update_field',
                    'field_id': field_id,
                    'updates': {'label': self._generate_label_from_id(field_id)},
                })
            elif len(field_label) < 2:
                results['warnings'].append({
                    'rule': 'wcag_3.3.2',
                    'field_id': field_id,
                    'message': f'Field "{field_id}" has very short label',
                    'severity': 'medium',
                    'wcag_criterion': '3.3.2 Labels or Instructions',
                })
            else:
                results['passed'].append({
                    'rule': 'wcag_1.3.1',
                    'field_id': field_id,
                    'message': f'Field "{field_id}" has proper label',
                    'severity': 'info',
                })
            
            # Check 2: Placeholders should not replace labels (WCAG 3.3.2)
            if field.get('placeholder') and not field_label:
                results['issues'].append({
                    'rule': 'wcag_3.3.2',
                    'field_id': field_id,
                    'message': f'Field "{field_id}" uses placeholder instead of label',
                    'severity': 'high',
                    'wcag_criterion': '3.3.2 Labels or Instructions',
                    'recommendation': 'Placeholders disappear when typing; use labels instead',
                })
            
            # Check 3: Required field indication (WCAG 3.3.2)
            if field.get('required'):
                if 'required' not in field_label.lower() and '*' not in field_label:
                    results['warnings'].append({
                        'rule': 'wcag_3.3.2',
                        'field_id': field_id,
                        'message': f'Required field "{field_label}" not clearly indicated',
                        'severity': 'low',
                        'wcag_criterion': '3.3.2 Labels or Instructions',
                        'recommendation': 'Add asterisk or "required" text to label',
                    })
            
            # Check 4: Error identification (WCAG 3.3.1)
            if field.get('validation'):
                validation = field['validation']
                if not validation.get('error_message'):
                    results['warnings'].append({
                        'rule': 'wcag_3.3.1',
                        'field_id': field_id,
                        'message': f'Field "{field_label}" lacks custom error message',
                        'severity': 'low',
                        'wcag_criterion': '3.3.1 Error Identification',
                        'recommendation': 'Add descriptive error messages',
                    })
            
            # Check 5: Help text for complex fields (WCAG 3.3.5)
            complex_types = ['file', 'payment', 'date', 'phone']
            if field_type in complex_types and not field.get('help'):
                results['recommendations'].append({
                    'rule': 'wcag_3.3.5',
                    'field_id': field_id,
                    'message': f'Complex field "{field_label}" could benefit from help text',
                    'severity': 'low',
                    'wcag_criterion': '3.3.5 Help',
                })
            
            # Check 6: Image alternatives (WCAG 1.1.1)
            if field_type == 'file':
                if not field.get('alt_text_required'):
                    results['recommendations'].append({
                        'rule': 'wcag_1.1.1',
                        'field_id': field_id,
                        'message': 'Consider requiring alt text for image uploads',
                        'severity': 'low',
                        'wcag_criterion': '1.1.1 Non-text Content',
                    })
            
            # Check 7: Select/Radio options (WCAG 1.3.1)
            if field_type in ['select', 'radio', 'checkbox'] and field.get('options'):
                options = field['options']
                if any(len(str(opt)) < 2 for opt in options):
                    results['warnings'].append({
                        'rule': 'wcag_1.3.1',
                        'field_id': field_id,
                        'message': f'Field "{field_label}" has unclear option labels',
                        'severity': 'medium',
                        'wcag_criterion': '1.3.1 Info and Relationships',
                    })
        
        # Check 8: Form structure (WCAG 1.3.1)
        if len(fields) > 10 and not schema.get('steps'):
            results['recommendations'].append({
                'rule': 'wcag_1.3.1',
                'message': 'Long form could benefit from step-by-step structure',
                'severity': 'low',
                'wcag_criterion': '1.3.1 Info and Relationships',
            })
        
        # Check 9: Color contrast (WCAG 1.4.3)
        if schema.get('styling'):
            styling = schema['styling']
            contrast_issues = self._check_color_contrast(styling, level)
            results['issues'].extend(contrast_issues.get('issues', []))
            results['passed'].extend(contrast_issues.get('passed', []))
        
        # Check 10: Timeout (WCAG 2.2.1)
        if schema.get('timeout'):
            timeout = schema['timeout']
            if timeout < 20 * 60:  # Less than 20 minutes
                results['warnings'].append({
                    'rule': 'wcag_2.2.1',
                    'message': f'Form timeout ({timeout}s) may be too short',
                    'severity': 'medium',
                    'wcag_criterion': '2.2.1 Timing Adjustable',
                    'recommendation': 'Allow at least 20 minutes or provide extension option',
                })
        
        return results
    
    def _check_hipaa_compliance(self, schema: Dict) -> Dict[str, Any]:
        """Check HIPAA compliance for health-related forms"""
        results = {
            'issues': [],
            'warnings': [],
            'passed': [],
            'recommendations': [],
        }
        
        fields = schema.get('fields', [])
        
        # Check if form collects PHI
        phi_fields = []
        for field in fields:
            label = field.get('label', '').lower()
            if any(kw in label for kw in self.HIPAA_KEYWORDS):
                phi_fields.append(field)
        
        if not phi_fields:
            results['passed'].append({
                'rule': 'hipaa_phi_detection',
                'message': 'No obvious PHI fields detected',
                'severity': 'info',
            })
            return results
        
        # PHI detected - check requirements
        results['warnings'].append({
            'rule': 'hipaa_phi_detected',
            'message': f'Form appears to collect PHI: {[f.get("label") for f in phi_fields]}',
            'severity': 'high',
            'recommendation': 'Ensure HIPAA compliance measures are in place',
        })
        
        # Check 1: BAA requirement notice
        has_baa_notice = 'baa' in str(schema).lower() or 'business associate' in str(schema).lower()
        if not has_baa_notice:
            results['issues'].append({
                'rule': 'hipaa_baa',
                'message': 'No Business Associate Agreement notice found',
                'severity': 'high',
                'recommendation': 'Add BAA information for PHI handling',
            })
        
        # Check 2: Encryption notice
        has_encryption = schema.get('settings', {}).get('encryption')
        if not has_encryption:
            results['issues'].append({
                'rule': 'hipaa_encryption',
                'message': 'No encryption configuration found for PHI',
                'severity': 'high',
                'recommendation': 'Enable encryption for PHI fields',
            })
        
        # Check 3: Authorization
        has_authorization = any(
            'authorization' in f.get('label', '').lower() or 
            'hipaa' in f.get('label', '').lower()
            for f in fields if f.get('type') == 'checkbox'
        )
        if not has_authorization:
            results['issues'].append({
                'rule': 'hipaa_authorization',
                'message': 'Missing HIPAA authorization checkbox',
                'severity': 'high',
                'recommendation': 'Add explicit HIPAA authorization checkbox',
            })
        
        # Check 4: Minimum necessary
        optional_phi = [f for f in phi_fields if not f.get('required')]
        if optional_phi:
            results['passed'].append({
                'rule': 'hipaa_minimum_necessary',
                'message': f'{len(optional_phi)} PHI fields are optional (good for minimum necessary)',
                'severity': 'info',
            })
        else:
            results['warnings'].append({
                'rule': 'hipaa_minimum_necessary',
                'message': 'All PHI fields are required',
                'severity': 'medium',
                'recommendation': 'Consider making some PHI fields optional (minimum necessary principle)',
            })
        
        return results
    
    def _check_pci_compliance(self, schema: Dict) -> Dict[str, Any]:
        """Check PCI-DSS compliance for payment forms"""
        results = {
            'issues': [],
            'warnings': [],
            'passed': [],
            'recommendations': [],
        }
        
        fields = schema.get('fields', [])
        
        # Check if form collects payment data
        payment_fields = []
        for field in fields:
            label = field.get('label', '').lower()
            field_type = field.get('type', '')
            
            if field_type == 'payment' or any(kw in label for kw in self.PCI_KEYWORDS):
                payment_fields.append(field)
        
        if not payment_fields:
            results['passed'].append({
                'rule': 'pci_detection',
                'message': 'No payment data fields detected',
                'severity': 'info',
            })
            return results
        
        # Payment fields detected
        results['warnings'].append({
            'rule': 'pci_detected',
            'message': f'Form collects payment data: {[f.get("label") for f in payment_fields]}',
            'severity': 'high',
            'recommendation': 'Ensure PCI-DSS compliance',
        })
        
        # Check 1: Use of tokenization
        uses_stripe = schema.get('settings', {}).get('stripe_enabled') or \
                     any(f.get('type') == 'payment' for f in fields)
        
        if uses_stripe:
            results['passed'].append({
                'rule': 'pci_tokenization',
                'message': 'Using payment provider tokenization (Stripe)',
                'severity': 'info',
            })
        else:
            results['issues'].append({
                'rule': 'pci_tokenization',
                'message': 'Direct card data collection detected without tokenization',
                'severity': 'critical',
                'recommendation': 'Use Stripe or similar payment provider for tokenization',
            })
        
        # Check 2: CVV handling
        cvv_field = next((f for f in fields if 'cvv' in f.get('label', '').lower()), None)
        if cvv_field:
            results['issues'].append({
                'rule': 'pci_cvv',
                'message': 'CVV field detected - CVV should never be stored',
                'severity': 'critical',
                'recommendation': 'Remove CVV field; use payment provider that handles CVV securely',
            })
        
        # Check 3: Card number format
        card_field = next(
            (f for f in fields if 'card number' in f.get('label', '').lower()), 
            None
        )
        if card_field and not card_field.get('validation', {}).get('pattern'):
            results['warnings'].append({
                'rule': 'pci_card_validation',
                'message': 'Card number field lacks format validation',
                'severity': 'medium',
                'recommendation': 'Add Luhn validation for card numbers',
            })
        
        return results
    
    def _check_color_contrast(
        self, styling: Dict, level: str
    ) -> Dict[str, Any]:
        """Check color contrast ratios"""
        results = {'issues': [], 'passed': []}
        
        if not styling:
            return results
        
        text_color = styling.get('text_color', '#000000')
        bg_color = styling.get('background_color', '#FFFFFF')
        
        try:
            ratio = self._calculate_contrast_ratio(text_color, bg_color)
            
            required_ratio = self.WCAG_AA_CONTRAST_NORMAL
            if level == 'AAA':
                required_ratio = self.WCAG_AAA_CONTRAST_NORMAL
            
            if ratio >= required_ratio:
                results['passed'].append({
                    'rule': 'wcag_1.4.3',
                    'message': f'Color contrast ratio {ratio:.2f}:1 meets {level} requirements',
                    'severity': 'info',
                    'wcag_criterion': '1.4.3 Contrast (Minimum)',
                })
            else:
                results['issues'].append({
                    'rule': 'wcag_1.4.3',
                    'message': f'Color contrast ratio {ratio:.2f}:1 below {level} requirement ({required_ratio}:1)',
                    'severity': 'high',
                    'wcag_criterion': '1.4.3 Contrast (Minimum)',
                    'recommendation': f'Increase contrast to at least {required_ratio}:1',
                })
        except:
            pass
        
        return results
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def relative_luminance(rgb: Tuple[int, int, int]) -> float:
            def channel_luminance(value: int) -> float:
                srgb = value / 255
                if srgb <= 0.03928:
                    return srgb / 12.92
                return ((srgb + 0.055) / 1.055) ** 2.4
            
            r, g, b = rgb
            return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)
        
        l1 = relative_luminance(hex_to_rgb(color1))
        l2 = relative_luminance(hex_to_rgb(color2))
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def _generate_label_from_id(self, field_id: str) -> str:
        """Generate readable label from field ID"""
        # Remove common prefixes
        label = re.sub(r'^(f_|field_|input_)', '', field_id)
        # Convert camelCase/snake_case to Title Case
        label = re.sub(r'([a-z])([A-Z])', r'\1 \2', label)
        label = label.replace('_', ' ').replace('-', ' ')
        return label.title()
    
    def _get_compliance_grade(self, score: float) -> str:
        """Convert compliance score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'B+'
        elif score >= 80:
            return 'B'
        elif score >= 75:
            return 'C+'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def apply_auto_fixes(self, form, fixes: List[Dict]) -> Dict[str, Any]:
        """Apply automatic compliance fixes to form"""
        schema = form.schema_json.copy()
        applied = []
        failed = []
        
        for fix in fixes:
            try:
                action = fix.get('action')
                
                if action == 'add_field':
                    field = fix.get('field')
                    schema['fields'].append(field)
                    applied.append({'action': 'add_field', 'field_id': field.get('id')})
                
                elif action == 'update_field':
                    field_id = fix.get('field_id')
                    updates = fix.get('updates', {})
                    
                    for field in schema['fields']:
                        if field.get('id') == field_id:
                            field.update(updates)
                            applied.append({'action': 'update_field', 'field_id': field_id})
                            break
                
                elif action == 'remove_field':
                    field_id = fix.get('field_id')
                    schema['fields'] = [f for f in schema['fields'] if f.get('id') != field_id]
                    applied.append({'action': 'remove_field', 'field_id': field_id})
                
            except Exception as e:
                failed.append({'fix': fix, 'error': str(e)})
        
        # Save updated schema
        form.schema_json = schema
        form.save()
        
        return {
            'applied': applied,
            'failed': failed,
            'total_applied': len(applied),
            'total_failed': len(failed),
        }
    
    def generate_privacy_policy(
        self,
        form,
        company_name: str,
        company_email: str,
        data_retention_days: int = 365,
    ) -> str:
        """Generate privacy policy for form using AI"""
        schema = form.schema_json
        fields = schema.get('fields', [])
        
        # Identify data types collected
        data_types = []
        for field in fields:
            label = field.get('label', '').lower()
            field_type = field.get('type')
            
            if field_type == 'email' or 'email' in label:
                data_types.append('email addresses')
            elif field_type == 'phone' or 'phone' in label:
                data_types.append('phone numbers')
            elif 'name' in label:
                data_types.append('names')
            elif 'address' in label:
                data_types.append('addresses')
            elif field_type == 'payment':
                data_types.append('payment information (processed via secure third-party)')
        
        prompt = f"""Generate a GDPR-compliant privacy policy for a web form.

Company: {company_name}
Contact Email: {company_email}
Form Title: {form.title}
Data Collected: {', '.join(set(data_types))}
Data Retention: {data_retention_days} days

Include:
1. What data is collected
2. How data is used
3. Data retention period
4. User rights (access, rectification, deletion)
5. Data security measures
6. Contact information
7. Cookie policy (if applicable)
8. Third-party sharing policy

Format as clean HTML suitable for embedding.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal document specialist. Generate professional, compliant privacy policies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating privacy policy: {e}"
    
    def generate_compliance_report(
        self,
        form,
        compliance_types: List[str] = None,
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        scan_results = self.scan_form(form, compliance_types)
        
        report = {
            'summary': {
                'form_title': form.title,
                'scan_date': datetime.now().isoformat(),
                'compliance_score': scan_results['compliance_score'],
                'grade': scan_results['grade'],
                'issues_count': len(scan_results['issues']),
                'warnings_count': len(scan_results['warnings']),
                'passed_count': len(scan_results['passed']),
            },
            'details': scan_results,
            'action_items': [],
        }
        
        # Prioritize action items
        for issue in scan_results['issues']:
            report['action_items'].append({
                'priority': 'high',
                'type': 'issue',
                'rule': issue.get('rule'),
                'message': issue.get('message'),
                'recommendation': issue.get('recommendation'),
            })
        
        for warning in scan_results['warnings']:
            report['action_items'].append({
                'priority': 'medium',
                'type': 'warning',
                'rule': warning.get('rule'),
                'message': warning.get('message'),
                'recommendation': warning.get('recommendation'),
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        report['action_items'].sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return report
