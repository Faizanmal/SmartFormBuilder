"""
Service for smart field dependencies and auto-population
"""
import requests
import logging
from django.core.cache import cache
from django.utils import timezone
from typing import Dict, Any, List, Optional
import re

from forms.models_new_features import (
    FieldDependency, FieldAutoPopulationLog
)

logger = logging.getLogger(__name__)


class FieldDependencyService:
    """Service for handling field dependencies and auto-population"""
    
    # Built-in API providers
    BUILTIN_PROVIDERS = {
        'us_postal': {
            'name': 'US Postal Service',
            'endpoint': 'https://api.zippopotam.us/us/{zipcode}',
            'type': 'postal'
        },
        'uk_postal': {
            'name': 'UK Postal Service',
            'endpoint': 'https://api.postcodes.io/postcodes/{postcode}',
            'type': 'postal'
        },
        'company_lookup': {
            'name': 'Company Data API',
            'endpoint': 'https://api.company-lookup.com/v1/company/{domain}',
            'type': 'business'
        }
    }
    
    @classmethod
    def execute_dependency(cls, dependency: FieldDependency, source_value: Any, 
                          submission_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a field dependency and return populated values
        
        Args:
            dependency: FieldDependency instance
            source_value: Value from the source field that triggers the dependency
            submission_id: Optional submission ID for logging
            
        Returns:
            Dict with populated field values
        """
        start_time = timezone.now()
        result = {
            'success': False,
            'populated_fields': {},
            'error': None,
            'cache_hit': False
        }
        
        try:
            if dependency.dependency_type == 'api':
                result = cls._execute_api_dependency(dependency, source_value)
            elif dependency.dependency_type == 'database':
                result = cls._execute_database_dependency(dependency, source_value)
            elif dependency.dependency_type == 'calculation':
                result = cls._execute_calculation_dependency(dependency, source_value)
            elif dependency.dependency_type == 'conditional':
                result = cls._execute_conditional_dependency(dependency, source_value)
                
        except Exception as e:
            logger.error(f"Error executing dependency {dependency.id}: {str(e)}")
            result['error'] = str(e)
        
        # Log the attempt
        response_time = (timezone.now() - start_time).total_seconds() * 1000
        FieldAutoPopulationLog.objects.create(
            dependency=dependency,
            submission_id=submission_id,
            source_value=source_value,
            populated_fields=result.get('populated_fields', {}),
            success=result.get('success', False),
            error_message=result.get('error', ''),
            response_time_ms=int(response_time),
            cache_hit=result.get('cache_hit', False)
        )
        
        return result
    
    @classmethod
    def _execute_api_dependency(cls, dependency: FieldDependency, source_value: Any) -> Dict[str, Any]:
        """Execute API-based dependency"""
        # Check cache first
        cache_key = f"field_dep_{dependency.id}_{source_value}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return {
                'success': True,
                'populated_fields': cached_result,
                'cache_hit': True
            }
        
        # Build API request
        endpoint = dependency.api_endpoint
        
        # Replace placeholders in endpoint
        if '{' in endpoint:
            endpoint = endpoint.format(**{dependency.source_field_id: source_value})
        
        # Prepare request parameters
        params = {}
        for key, value_template in dependency.api_params_template.items():
            if isinstance(value_template, str) and '{' in value_template:
                params[key] = value_template.format(**{dependency.source_field_id: source_value})
            else:
                params[key] = value_template
        
        # Make API request
        try:
            response = requests.request(
                method=dependency.api_method,
                url=endpoint,
                params=params if dependency.api_method == 'GET' else None,
                json=params if dependency.api_method == 'POST' else None,
                headers=dependency.api_headers,
                timeout=10
            )
            response.raise_for_status()
            
            api_data = response.json()
            
            # Map response to form fields
            populated_fields = cls._map_api_response(api_data, dependency.response_mapping)
            
            # Cache the result
            if dependency.cache_duration > 0:
                cache.set(cache_key, populated_fields, dependency.cache_duration)
            
            return {
                'success': True,
                'populated_fields': populated_fields,
                'cache_hit': False
            }
            
        except requests.RequestException as e:
            logger.error(f"API request failed for dependency {dependency.id}: {str(e)}")
            return {
                'success': False,
                'populated_fields': {},
                'error': f"API request failed: {str(e)}"
            }
    
    @classmethod
    def _map_api_response(cls, api_data: Dict, mapping: Dict) -> Dict[str, Any]:
        """
        Map API response data to form fields
        
        mapping format: {
            'field_id': 'response.path.to.value',
            'city': 'places[0].place_name',
            'state': 'places[0].state'
        }
        """
        result = {}
        
        for field_id, path in mapping.items():
            try:
                value = cls._extract_value_from_path(api_data, path)
                if value is not None:
                    result[field_id] = value
            except Exception as e:
                logger.warning(f"Could not extract value for field {field_id} from path {path}: {str(e)}")
        
        return result
    
    @classmethod
    def _extract_value_from_path(cls, data: Dict, path: str) -> Any:
        """Extract value from nested dict using dot notation path"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            # Handle array indexing like 'places[0]'
            match = re.match(r'(\w+)\[(\d+)\]', part)
            if match:
                key = match.group(1)
                index = int(match.group(2))
                current = current[key][index]
            else:
                current = current[part]
        
        return current
    
    @classmethod
    def _execute_database_dependency(cls, dependency: FieldDependency, source_value: Any) -> Dict[str, Any]:
        """Execute database lookup dependency"""
        # This would query internal database tables
        # Implementation depends on specific database schema
        return {
            'success': True,
            'populated_fields': {},
            'cache_hit': False
        }
    
    @classmethod
    def _execute_calculation_dependency(cls, dependency: FieldDependency, source_value: Any) -> Dict[str, Any]:
        """Execute calculation-based dependency"""
        try:
            # Safely evaluate calculation formula
            # WARNING: In production, use a safer evaluation method
            formula = dependency.calculation_formula
            
            # Create a safe namespace for evaluation
            safe_namespace = {
                'value': source_value,
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
            }
            
            result_value = eval(formula, {"__builtins__": {}}, safe_namespace)
            
            populated_fields = {}
            for field_id in dependency.target_field_ids:
                populated_fields[field_id] = result_value
            
            return {
                'success': True,
                'populated_fields': populated_fields,
                'cache_hit': False
            }
            
        except Exception as e:
            logger.error(f"Calculation error for dependency {dependency.id}: {str(e)}")
            return {
                'success': False,
                'populated_fields': {},
                'error': f"Calculation error: {str(e)}"
            }
    
    @classmethod
    def _execute_conditional_dependency(cls, dependency: FieldDependency, source_value: Any) -> Dict[str, Any]:
        """Execute conditional logic dependency"""
        # This would handle conditional field visibility/requirements
        return {
            'success': True,
            'populated_fields': {},
            'cache_hit': False
        }
    
    @classmethod
    def get_dependencies_for_field(cls, form_id: str, field_id: str) -> List[FieldDependency]:
        """Get all active dependencies triggered by a specific field"""
        return FieldDependency.objects.filter(
            form_id=form_id,
            source_field_id=field_id,
            is_active=True
        ).order_by('priority')
    
    @classmethod
    def populate_from_zipcode(cls, zipcode: str, country: str = 'US') -> Dict[str, Any]:
        """
        Built-in helper: Populate city/state from ZIP code
        
        Args:
            zipcode: ZIP or postal code
            country: Country code (US, UK, etc.)
            
        Returns:
            Dict with city, state, country data
        """
        if country == 'US':
            endpoint = f"https://api.zippopotam.us/us/{zipcode}"
        elif country == 'UK':
            endpoint = f"https://api.postcodes.io/postcodes/{zipcode}"
        else:
            return {'success': False, 'error': 'Unsupported country'}
        
        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if country == 'US':
                return {
                    'success': True,
                    'city': data['places'][0]['place name'],
                    'state': data['places'][0]['state'],
                    'state_abbr': data['places'][0]['state abbreviation'],
                    'country': 'United States'
                }
            elif country == 'UK':
                return {
                    'success': True,
                    'city': data['result']['admin_district'],
                    'region': data['result']['region'],
                    'country': data['result']['country']
                }
                
        except Exception as e:
            logger.error(f"ZIP code lookup failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def populate_from_email_domain(cls, email: str) -> Dict[str, Any]:
        """
        Built-in helper: Suggest company name from email domain
        
        Args:
            email: Email address
            
        Returns:
            Dict with company information
        """
        try:
            domain = email.split('@')[1]
            
            # Extract company name from domain (basic heuristic)
            company_name = domain.split('.')[0]
            company_name = company_name.replace('-', ' ').replace('_', ' ').title()
            
            return {
                'success': True,
                'company_name': company_name,
                'domain': domain
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
