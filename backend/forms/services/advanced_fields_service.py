"""
Advanced field types and validation service
"""
import re
import os
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings


class AdvancedFieldService:
    """Service for handling advanced field types"""
    
    @staticmethod
    def calculate_field(formula, payload):
        """
        Calculate field value based on formula
        
        Formula examples:
        - "field1 + field2"
        - "field1 * field2 * 0.1"
        - "SUM(field1, field2, field3)"
        - "IF(field1 > 100, field1 * 0.9, field1)"
        """
        try:
            # Replace field IDs with actual values
            expression = formula
            for field_id, value in payload.items():
                if isinstance(value, (int, float)):
                    expression = expression.replace(field_id, str(value))
            
            # Handle SUM function
            if 'SUM(' in expression:
                sum_match = re.search(r'SUM\((.*?)\)', expression)
                if sum_match:
                    fields = sum_match.group(1).split(',')
                    total = sum(float(payload.get(f.strip(), 0)) for f in fields)
                    expression = expression.replace(sum_match.group(0), str(total))
            
            # Handle IF function (simplified)
            if 'IF(' in expression:
                if_match = re.search(r'IF\((.*?),\s*(.*?),\s*(.*?)\)', expression)
                if if_match:
                    condition = if_match.group(1)
                    true_val = if_match.group(2)
                    false_val = if_match.group(3)
                    
                    # Evaluate condition (simplified, production should use safer eval)
                    try:
                        result = true_val if eval(condition) else false_val
                        expression = expression.replace(if_match.group(0), str(result))
                    except:
                        pass
            
            # Evaluate final expression
            # WARNING: In production, use a safer expression evaluator
            result = eval(expression)
            return round(float(result), 2)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Calculation error: {e}")
            return 0
    
    @staticmethod
    def validate_custom_regex(value, pattern, error_message=None):
        """Validate field value against custom regex pattern"""
        if not re.match(pattern, str(value)):
            raise ValidationError(
                error_message or f"Value does not match required pattern: {pattern}"
            )
        return True
    
    @staticmethod
    def cross_field_validation(payload, rules):
        """
        Validate across multiple fields
        
        Rules example:
        {
            'type': 'comparison',
            'field1': 'start_date',
            'operator': '<',
            'field2': 'end_date',
            'error': 'Start date must be before end date'
        }
        """
        errors = {}
        
        for rule in rules:
            rule_type = rule.get('type')
            
            if rule_type == 'comparison':
                field1_value = payload.get(rule['field1'])
                field2_value = payload.get(rule['field2'])
                operator = rule['operator']
                
                try:
                    if operator == '<':
                        valid = field1_value < field2_value
                    elif operator == '>':
                        valid = field1_value > field2_value
                    elif operator == '==':
                        valid = field1_value == field2_value
                    elif operator == '!=':
                        valid = field1_value != field2_value
                    elif operator == '<=':
                        valid = field1_value <= field2_value
                    elif operator == '>=':
                        valid = field1_value >= field2_value
                    else:
                        valid = True
                    
                    if not valid:
                        errors[rule['field1']] = rule.get('error', 'Validation failed')
                except (TypeError, KeyError):
                    pass
            
            elif rule_type == 'required_if':
                # Require field if another field has specific value
                condition_field = rule['condition_field']
                condition_value = rule['condition_value']
                required_field = rule['required_field']
                
                if payload.get(condition_field) == condition_value:
                    if not payload.get(required_field):
                        errors[required_field] = rule.get('error', 'This field is required')
            
            elif rule_type == 'match':
                # Two fields must match (e.g., password confirmation)
                field1 = rule['field1']
                field2 = rule['field2']
                
                if payload.get(field1) != payload.get(field2):
                    errors[field2] = rule.get('error', 'Fields do not match')
        
        return errors
    
    @staticmethod
    def handle_file_upload(file, form_id, field_id, allowed_extensions=None):
        """
        Handle file upload with validation and cloud storage
        
        Returns: {
            'url': 'https://...',
            'filename': 'original_name.pdf',
            'size': 12345,
            'content_type': 'application/pdf'
        }
        """
        if allowed_extensions is None:
            allowed_extensions = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif']
        
        # Validate file extension
        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(f"File type .{ext} not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        # Validate file size (10MB default limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise ValidationError(f"File size exceeds maximum of {max_size / (1024*1024)}MB")
        
        # Generate unique filename
        import uuid
        unique_filename = f"uploads/{form_id}/{field_id}/{uuid.uuid4()}_{file.name}"
        
        # Save file
        file_path = default_storage.save(unique_filename, file)
        file_url = default_storage.url(file_path)
        
        return {
            'url': file_url,
            'path': file_path,
            'filename': file.name,
            'size': file.size,
            'content_type': file.content_type,
        }
    
    @staticmethod
    def validate_signature(signature_data):
        """
        Validate signature capture data
        
        signature_data: Base64 encoded image data
        Returns: True if valid, raises ValidationError otherwise
        """
        if not signature_data:
            raise ValidationError("Signature is required")
        
        # Check if it's base64 encoded
        if not signature_data.startswith('data:image'):
            raise ValidationError("Invalid signature format")
        
        # Extract base64 data
        try:
            header, encoded = signature_data.split(',', 1)
            import base64
            decoded = base64.b64decode(encoded)
            
            # Check minimum size (empty signatures are usually very small)
            if len(decoded) < 1000:  # Minimum 1KB
                raise ValidationError("Signature appears to be empty")
            
            return True
        except Exception as e:
            raise ValidationError(f"Invalid signature data: {str(e)}")
    
    @staticmethod
    def populate_dynamic_dropdown(source_type, source_config, previous_responses=None):
        """
        Populate dropdown options dynamically
        
        source_type: 'api', 'previous_field', 'database'
        source_config: Configuration for the source
        previous_responses: Data from previous fields
        
        Returns: List of options
        """
        if source_type == 'previous_field':
            # Get options from a previous field's response
            field_id = source_config.get('field_id')
            if previous_responses and field_id in previous_responses:
                value = previous_responses[field_id]
                
                # Map values to options
                mapping = source_config.get('mapping', {})
                return mapping.get(value, [])
        
        elif source_type == 'api':
            # Fetch options from external API
            import requests
            
            api_url = source_config.get('url')
            method = source_config.get('method', 'GET')
            headers = source_config.get('headers', {})
            
            try:
                if method == 'GET':
                    response = requests.get(api_url, headers=headers, timeout=5)
                else:
                    response = requests.post(api_url, headers=headers, timeout=5)
                
                response.raise_for_status()
                data = response.json()
                
                # Extract options using configured path
                options_path = source_config.get('options_path', 'data')
                options = data
                for key in options_path.split('.'):
                    options = options.get(key, [])
                
                return options
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to fetch dynamic options: {e}")
                return []
        
        return []
    
    @staticmethod
    def calculate_dynamic_pricing(base_price, payload, pricing_rules):
        """
        Calculate dynamic pricing based on form responses
        
        pricing_rules: List of rules that modify the price
        Example:
        [
            {'field': 'quantity', 'type': 'multiply'},
            {'field': 'rush_delivery', 'type': 'add', 'amount': 50},
            {'field': 'discount_code', 'type': 'percentage', 'values': {'SAVE10': -10}}
        ]
        """
        final_price = Decimal(str(base_price))
        
        for rule in pricing_rules:
            field_id = rule['field']
            rule_type = rule['type']
            field_value = payload.get(field_id)
            
            if field_value is None:
                continue
            
            if rule_type == 'multiply':
                try:
                    multiplier = Decimal(str(field_value))
                    final_price = final_price * multiplier
                except (ValueError, TypeError):
                    pass
            
            elif rule_type == 'add':
                amount = Decimal(str(rule.get('amount', 0)))
                final_price = final_price + amount
            
            elif rule_type == 'percentage':
                values_map = rule.get('values', {})
                if field_value in values_map:
                    percentage = Decimal(str(values_map[field_value]))
                    adjustment = final_price * (percentage / 100)
                    final_price = final_price + adjustment
        
        return float(final_price)
