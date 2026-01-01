"""
Service for smart external validation
"""
import logging
import requests
import re
from django.core.cache import cache
from django.utils import timezone
from typing import Dict, Any, Optional

from forms.models_new_features import ExternalValidationRule, ValidationLog

logger = logging.getLogger(__name__)


class ExternalValidationService:
    """Service for validating form fields against external services"""
    
    @classmethod
    def validate_field(cls, form_id: str, field_id: str, value: Any,
                      submission_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a field value using external service
        
        Args:
            form_id: Form ID
            field_id: Field ID to validate
            value: Field value
            submission_id: Optional submission ID for logging
            
        Returns:
            Dict with validation results
        """
        try:
            rule = ExternalValidationRule.objects.get(
                form_id=form_id,
                field_id=field_id,
                is_active=True
            )
        except ExternalValidationRule.DoesNotExist:
            return {
                'is_valid': True,
                'message': '',
                'details': {}
            }
        
        # Check cache if enabled
        if rule.cache_results:
            cache_key = f"validation_{rule.id}_{value}"
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        # Perform validation based on type
        start_time = timezone.now()
        
        if rule.validation_type == 'iban':
            result = cls._validate_iban(value)
        elif rule.validation_type == 'vat':
            result = cls._validate_vat(value)
        elif rule.validation_type == 'business_registry':
            result = cls._validate_business_registry(value, rule)
        elif rule.validation_type == 'address':
            result = cls._validate_address(value, rule)
        elif rule.validation_type == 'phone_carrier':
            result = cls._validate_phone_carrier(value)
        elif rule.validation_type == 'email_mx':
            result = cls._validate_email_mx(value)
        elif rule.validation_type == 'domain':
            result = cls._validate_domain(value)
        elif rule.validation_type == 'custom':
            result = cls._validate_custom(value, rule)
        else:
            result = {'is_valid': True, 'details': {}}
        
        response_time = (timezone.now() - start_time).total_seconds() * 1000
        
        # Log validation attempt
        ValidationLog.objects.create(
            validation_rule=rule,
            submission_id=submission_id,
            input_value=str(value),
            is_valid=result.get('is_valid', False),
            validation_details=result.get('details', {}),
            response_time_ms=int(response_time),
            cache_hit=False,
            success=result.get('success', True),
            error_message=result.get('error', '')
        )
        
        # Cache result
        if rule.cache_results and result.get('success'):
            cache.set(cache_key, result, rule.cache_duration)
        
        # Format response
        response = {
            'is_valid': result.get('is_valid', False),
            'message': rule.error_message_invalid if not result.get('is_valid') else 'Valid',
            'details': result.get('details', {})
        }
        
        if not result.get('success'):
            response['message'] = rule.error_message_service_error
        
        return response
    
    @classmethod
    def _validate_iban(cls, iban: str) -> Dict:
        """Validate IBAN (International Bank Account Number)"""
        # Remove spaces and convert to uppercase
        iban = iban.replace(' ', '').upper()
        
        # Basic format check
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
            return {'is_valid': False, 'success': True, 'details': {'error': 'Invalid IBAN format'}}
        
        # Length check (varies by country)
        country_lengths = {
            'GB': 22, 'FR': 27, 'DE': 22, 'IT': 27, 'ES': 24,
            'NL': 18, 'BE': 16, 'PT': 25, 'IE': 22, 'AT': 20
        }
        
        country_code = iban[:2]
        expected_length = country_lengths.get(country_code)
        
        if expected_length and len(iban) != expected_length:
            return {'is_valid': False, 'success': True, 'details': {'error': 'Invalid IBAN length'}}
        
        # MOD-97 checksum validation
        # Move first 4 chars to end
        rearranged = iban[4:] + iban[:4]
        
        # Replace letters with numbers (A=10, B=11, etc.)
        numeric = ''
        for char in rearranged:
            if char.isalpha():
                numeric += str(ord(char) - ord('A') + 10)
            else:
                numeric += char
        
        # Calculate checksum
        checksum = int(numeric) % 97
        
        is_valid = checksum == 1
        
        return {
            'is_valid': is_valid,
            'success': True,
            'details': {
                'country': country_code,
                'checksum_valid': is_valid
            }
        }
    
    @classmethod
    def _validate_vat(cls, vat_number: str) -> Dict:
        """Validate EU VAT number using VIES"""
        # Extract country code and number
        vat_number = vat_number.replace(' ', '').upper()
        
        if len(vat_number) < 3:
            return {'is_valid': False, 'success': True, 'details': {'error': 'Invalid VAT format'}}
        
        country_code = vat_number[:2]
        vat_num = vat_number[2:]
        
        try:
            # In production, use actual VIES API
            # response = requests.post('http://ec.europa.eu/taxation_customs/vies/services/checkVatService', ...)
            
            # Placeholder response
            is_valid = True
            
            return {
                'is_valid': is_valid,
                'success': True,
                'details': {
                    'country': country_code,
                    'number': vat_num
                }
            }
        except Exception as e:
            return {'is_valid': False, 'success': False, 'error': str(e)}
    
    @classmethod
    def _validate_business_registry(cls, business_number: str, rule: ExternalValidationRule) -> Dict:
        """Validate business registration number"""
        try:
            if rule.validation_endpoint:
                response = requests.get(
                    rule.validation_endpoint,
                    params={'number': business_number},
                    timeout=5
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    'is_valid': data.get('valid', False),
                    'success': True,
                    'details': data
                }
        except Exception as e:
            logger.error(f"Business registry validation failed: {str(e)}")
            return {'is_valid': False, 'success': False, 'error': str(e)}
        
        return {'is_valid': True, 'success': True, 'details': {}}
    
    @classmethod
    def _validate_address(cls, address: str, rule: ExternalValidationRule) -> Dict:
        """Validate address using postal service API"""
        # Implementation would use USPS, Royal Mail, or other postal APIs
        return {'is_valid': True, 'success': True, 'details': {}}
    
    @classmethod
    def _validate_phone_carrier(cls, phone: str) -> Dict:
        """Validate phone number and get carrier information"""
        # Remove non-digits
        phone_digits = re.sub(r'\D', '', phone)
        
        if len(phone_digits) < 10:
            return {'is_valid': False, 'success': True, 'details': {'error': 'Invalid phone number'}}
        
        # In production, use a service like Twilio Lookup API
        return {
            'is_valid': True,
            'success': True,
            'details': {
                'carrier': 'Unknown',
                'type': 'mobile'
            }
        }
    
    @classmethod
    def _validate_email_mx(cls, email: str) -> Dict:
        """Validate email by checking MX records"""
        import dns.resolver
        
        try:
            domain = email.split('@')[1]
            mx_records = dns.resolver.resolve(domain, 'MX')
            
            has_mx = len(list(mx_records)) > 0
            
            return {
                'is_valid': has_mx,
                'success': True,
                'details': {
                    'domain': domain,
                    'has_mx_records': has_mx
                }
            }
        except Exception:
            return {
                'is_valid': False,
                'success': True,
                'details': {'error': 'No MX records found'}
            }
    
    @classmethod
    def _validate_domain(cls, domain: str) -> Dict:
        """Validate domain ownership"""
        # This would use WHOIS or domain verification APIs
        return {'is_valid': True, 'success': True, 'details': {}}
    
    @classmethod
    def _validate_custom(cls, value: str, rule: ExternalValidationRule) -> Dict:
        """Custom validation using configured endpoint"""
        try:
            if rule.validation_endpoint:
                response = requests.post(
                    rule.validation_endpoint,
                    json=rule.validation_params,
                    data={'value': value},
                    timeout=5
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    'is_valid': data.get('valid', False),
                    'success': True,
                    'details': data
                }
        except Exception as e:
            return {'is_valid': False, 'success': False, 'error': str(e)}
        
        return {'is_valid': True, 'success': True, 'details': {}}
