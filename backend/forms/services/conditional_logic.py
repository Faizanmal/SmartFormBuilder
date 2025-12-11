"""
Conditional Logic Engine for Form Field Visibility
"""
from typing import Dict, List, Any


class ConditionalLogicEngine:
    """Evaluate conditional logic rules to determine field visibility"""
    
    @staticmethod
    def evaluate_condition(condition: Dict[str, Any], submission_data: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition against submission data
        
        Args:
            condition: Dict with 'field', 'operator', 'value'
            submission_data: Current form submission values
            
        Returns:
            Boolean result of the condition evaluation
        """
        field_id = condition.get('field')
        operator = condition.get('operator')
        expected_value = condition.get('value')
        
        if not field_id or not operator:
            return False
        
        actual_value = submission_data.get(field_id)
        
        # Handle different operators
        if operator == 'equals':
            return actual_value == expected_value
        
        elif operator == 'not_equals':
            return actual_value != expected_value
        
        elif operator == 'in':
            if not isinstance(expected_value, list):
                return False
            return actual_value in expected_value
        
        elif operator == 'contains':
            if isinstance(actual_value, list):
                return expected_value in actual_value
            elif isinstance(actual_value, str):
                return expected_value in actual_value
            return False
        
        elif operator == 'gte':
            try:
                return float(actual_value) >= float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == 'lte':
            try:
                return float(actual_value) <= float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == 'gt':
            try:
                return float(actual_value) > float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == 'lt':
            try:
                return float(actual_value) < float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == 'is_empty':
            return not actual_value or actual_value == '' or actual_value == []
        
        elif operator == 'is_not_empty':
            return bool(actual_value) and actual_value != '' and actual_value != []
        
        return False
    
    @staticmethod
    def get_visible_fields(
        schema: Dict[str, Any],
        submission_data: Dict[str, Any]
    ) -> List[str]:
        """
        Determine which fields should be visible based on logic rules
        
        Args:
            schema: Form schema with 'fields' and 'logic' arrays
            submission_data: Current submission values
            
        Returns:
            List of field IDs that should be visible
        """
        logic_rules = schema.get('logic', [])
        all_fields = [f['id'] for f in schema.get('fields', [])]
        
        # Start with all fields visible
        visible_fields = set(all_fields)
        hidden_fields = set()
        
        # Evaluate each logic rule
        for rule in logic_rules:
            condition = rule.get('if')
            if not condition:
                continue
            
            # Check if condition is met
            if ConditionalLogicEngine.evaluate_condition(condition, submission_data):
                # Show specified fields
                show_fields = rule.get('show', [])
                visible_fields.update(show_fields)
                
                # Hide specified fields
                hide_fields = rule.get('hide', [])
                hidden_fields.update(hide_fields)
        
        # Remove hidden fields from visible set
        visible_fields -= hidden_fields
        
        return list(visible_fields)
    
    @staticmethod
    def validate_submission(
        schema: Dict[str, Any],
        submission_data: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate submission against schema and conditional logic
        
        Args:
            schema: Form schema
            submission_data: Submitted data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        visible_fields = ConditionalLogicEngine.get_visible_fields(schema, submission_data)
        
        # Check required fields that are visible
        for field in schema.get('fields', []):
            field_id = field.get('id')
            
            # Skip validation for hidden fields
            if field_id not in visible_fields:
                continue
            
            is_required = field.get('required', False)
            field_value = submission_data.get(field_id)
            
            if is_required and not field_value:
                errors.append(f"Field '{field.get('label', field_id)}' is required")
        
        return len(errors) == 0, errors
