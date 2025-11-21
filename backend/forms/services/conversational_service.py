"""
Conversational form service with AI-powered interactions
"""
import json
from openai import OpenAI
from django.conf import settings


class ConversationalFormService:
    """Service for managing conversational/chatbot-style forms"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_next_question(self, form_schema, conversation_history, current_data):
        """
        Generate the next question based on conversation context
        
        Args:
            form_schema: The form structure
            conversation_history: Previous Q&A pairs
            current_data: Data collected so far
            
        Returns:
            dict with next question, field info, and suggestions
        """
        # Identify next field to ask about
        next_field = self._get_next_field(form_schema, current_data)
        
        if not next_field:
            return {
                'complete': True,
                'message': 'Thank you! We have all the information we need.',
                'data': current_data
            }
        
        # Generate conversational question using AI
        question = self._generate_natural_question(
            next_field, 
            conversation_history,
            current_data
        )
        
        return {
            'complete': False,
            'field_id': next_field['id'],
            'field_type': next_field['type'],
            'question': question,
            'suggestions': next_field.get('options', []),
            'validation': next_field.get('validation', {})
        }
    
    def _get_next_field(self, form_schema, current_data):
        """Find the next unanswered field"""
        fields = form_schema.get('fields', [])
        
        for field in fields:
            field_id = field['id']
            
            # Check if field already has a value
            if field_id not in current_data:
                # Check conditional logic
                if self._should_show_field(field, current_data):
                    return field
        
        return None
    
    def _should_show_field(self, field, current_data):
        """Check if field should be shown based on conditional logic"""
        conditions = field.get('show_if', {})
        
        if not conditions:
            return True
        
        condition_type = conditions.get('type', 'all')  # 'all' or 'any'
        rules = conditions.get('rules', [])
        
        results = []
        for rule in rules:
            field_id = rule.get('field')
            operator = rule.get('operator')
            value = rule.get('value')
            
            current_value = current_data.get(field_id)
            
            if operator == 'equals':
                results.append(current_value == value)
            elif operator == 'not_equals':
                results.append(current_value != value)
            elif operator == 'contains':
                results.append(value in str(current_value))
            elif operator == 'greater_than':
                try:
                    results.append(float(current_value) > float(value))
                except:
                    results.append(False)
        
        if condition_type == 'all':
            return all(results) if results else True
        else:
            return any(results) if results else True
    
    def _generate_natural_question(self, field, history, current_data):
        """Use AI to generate natural conversational question"""
        
        # Build context for AI
        context = {
            'field_label': field['label'],
            'field_type': field['type'],
            'field_help': field.get('help', ''),
            'required': field.get('required', False),
            'previous_answers': current_data
        }
        
        # Create prompt
        prompt = f"""You are a friendly form assistant. Generate a natural, conversational question to ask for this information:

Field: {context['field_label']}
Type: {context['field_type']}
Help text: {context['field_help']}
Required: {context['required']}

Previous answers: {json.dumps(current_data, indent=2)}

Generate a warm, conversational question (1-2 sentences) that feels natural and friendly. Don't use formal language like "Please provide" - instead use casual language like "What's", "Can you tell me", etc.

Question:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful form assistant that asks questions naturally."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            question = response.choices[0].message.content.strip()
            return question
            
        except Exception as e:
            # Fallback to default question
            return self._default_question(field)
    
    def _default_question(self, field):
        """Generate default question without AI"""
        label = field['label']
        field_type = field['type']
        
        templates = {
            'text': f"What's your {label.lower()}?",
            'email': f"What's your {label.lower()}?",
            'phone': f"Can you share your {label.lower()}?",
            'number': f"What {label.lower()} would you like?",
            'date': f"When is your {label.lower()}?",
            'select': f"Which {label.lower()} works best for you?",
            'textarea': f"Can you tell me about your {label.lower()}?"
        }
        
        return templates.get(field_type, f"Please provide your {label.lower()}")
    
    def parse_user_response(self, user_input, field_type, field_options=None):
        """
        Parse and validate user's natural language response
        
        Args:
            user_input: User's text response
            field_type: Expected field type
            field_options: Valid options (for select/radio)
            
        Returns:
            Parsed and validated value
        """
        user_input = user_input.strip()
        
        if field_type in ['text', 'textarea']:
            return user_input
        
        elif field_type == 'email':
            # Basic email validation
            if '@' in user_input and '.' in user_input:
                return user_input.lower()
            raise ValueError("Please provide a valid email address")
        
        elif field_type == 'phone':
            # Extract digits
            digits = ''.join(filter(str.isdigit, user_input))
            if len(digits) >= 10:
                return digits
            raise ValueError("Please provide a valid phone number")
        
        elif field_type == 'number':
            # Extract number from text
            try:
                # Try to find a number in the text
                import re
                numbers = re.findall(r'-?\d+\.?\d*', user_input)
                if numbers:
                    return float(numbers[0])
                raise ValueError("Please provide a number")
            except:
                raise ValueError("Please provide a valid number")
        
        elif field_type in ['select', 'radio']:
            # Try to match option using AI
            if field_options:
                return self._match_option(user_input, field_options)
            return user_input
        
        elif field_type == 'checkbox':
            # Parse yes/no or list
            positive = ['yes', 'yeah', 'sure', 'definitely', 'true', '1']
            negative = ['no', 'nope', 'nah', 'false', '0']
            
            lower_input = user_input.lower()
            if any(word in lower_input for word in positive):
                return True
            elif any(word in lower_input for word in negative):
                return False
            return user_input
        
        return user_input
    
    def _match_option(self, user_input, options):
        """Match user input to closest option using fuzzy matching"""
        user_input = user_input.lower()
        
        # Exact match
        for option in options:
            if user_input == option.lower():
                return option
        
        # Contains match
        for option in options:
            if user_input in option.lower() or option.lower() in user_input:
                return option
        
        # Fuzzy match using AI
        try:
            prompt = f"""Match the user's response to the closest option:

User said: "{user_input}"

Valid options:
{json.dumps(options, indent=2)}

Return only the exact matching option from the list above, nothing else."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            matched = response.choices[0].message.content.strip()
            
            # Verify it's a valid option
            for option in options:
                if matched.lower() == option.lower():
                    return option
            
        except:
            pass
        
        # Default to first option if no match
        return options[0] if options else user_input
    
    def generate_summary(self, form_schema, collected_data):
        """Generate a friendly summary of collected information"""
        
        prompt = f"""Generate a friendly, conversational summary of the information collected:

Form: {form_schema.get('title', 'Form')}
Data collected:
{json.dumps(collected_data, indent=2)}

Create a warm, 2-3 sentence summary that confirms what was collected. Use casual language.

Summary:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except:
            return "Thanks for providing all the information! We'll review it and get back to you soon."
    
    def auto_complete_field(self, field, conversation_context):
        """
        AI-powered field completion suggestions
        
        Args:
            field: Field to complete
            conversation_context: Previous conversation data
            
        Returns:
            Suggested completion
        """
        prompt = f"""Based on the conversation context, suggest a value for this field:

Field: {field['label']}
Type: {field['type']}
Context: {json.dumps(conversation_context, indent=2)}

Provide a smart suggestion based on the context. Return only the suggested value.

Suggestion:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except:
            return None
