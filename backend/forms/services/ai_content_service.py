"""
AI Content Generation Service
Generate form content, descriptions, emails, and more using AI
"""
import json
from typing import Dict, List
from django.conf import settings
from openai import OpenAI


class AIContentService:
    """
    Service for AI-powered content generation.
    Generates form text, email templates, and communications.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
    
    def generate_form_description(
        self,
        form_title: str,
        fields: List[Dict],
        context: str = None,
        tone: str = 'professional',
    ) -> str:
        """Generate a compelling form description"""
        
        field_summary = ', '.join([f.get('label', '') for f in fields[:5]])
        
        prompt = f"""Write a brief, engaging description for a form.

Form Title: {form_title}
Fields include: {field_summary}
Context: {context or 'General business form'}
Tone: {tone}

Requirements:
- 1-2 sentences
- Explain the purpose
- Encourage completion
- Don't mention specific fields

Return only the description text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write concise, professional form descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            
            return response.choices[0].message.content.strip()
        except Exception:
            return f"Please fill out this {form_title.lower()}."
    
    def generate_field_placeholders(
        self,
        fields: List[Dict],
    ) -> List[Dict]:
        """Generate helpful placeholder text for fields"""
        
        prompt = f"""Generate helpful placeholder text for these form fields.

Fields:
{json.dumps(fields, indent=2)}

For each field, provide a helpful placeholder that:
- Shows the expected format (email, phone)
- Gives an example value
- Is concise (under 40 characters)
- Doesn't repeat the label

Return JSON array with field_id and placeholder:
[{{"field_id": "f_1", "placeholder": "example placeholder"}}]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You generate helpful form field placeholders. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return []
    
    def generate_field_help_text(
        self,
        field: Dict,
        context: str = None,
    ) -> str:
        """Generate contextual help text for a field"""
        
        prompt = f"""Write brief help text for this form field.

Field Label: {field.get('label')}
Field Type: {field.get('type')}
Required: {field.get('required', False)}
Context: {context or 'General form'}

Requirements:
- 1 sentence
- Explain what's expected or why it's needed
- Be helpful, not redundant with label

Return only the help text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write helpful form field descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=100,
            )
            
            return response.choices[0].message.content.strip()
        except Exception:
            return ""
    
    def generate_thank_you_message(
        self,
        form_title: str,
        form_type: str = 'contact',
        brand_name: str = None,
        next_steps: List[str] = None,
    ) -> Dict[str, str]:
        """Generate thank you page content"""
        
        prompt = f"""Create thank you page content for a form submission.

Form: {form_title}
Type: {form_type}
Brand: {brand_name or 'Our team'}
Next Steps: {next_steps or ['We will review your submission', 'You will hear from us soon']}

Return JSON with:
{{
    "headline": "Thank you headline",
    "message": "Thank you message (2-3 sentences)",
    "next_steps": ["Step 1", "Step 2"],
    "cta_text": "Call to action button text",
    "cta_url": "Suggested URL path"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You create engaging thank you page content. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {
                'headline': 'Thank You!',
                'message': 'Your submission has been received.',
                'next_steps': ['We will review your submission'],
                'cta_text': 'Return Home',
                'cta_url': '/',
            }
    
    def generate_email_template(
        self,
        template_type: str,
        form_title: str,
        brand_name: str = None,
        fields: List[Dict] = None,
    ) -> Dict[str, str]:
        """Generate email template for various purposes"""
        
        template_contexts = {
            'confirmation': 'Email to confirm form submission to the user',
            'notification': 'Email to notify admin of new submission',
            'follow_up': 'Follow-up email to user after submission',
            'reminder': 'Reminder email for abandoned form',
            'welcome': 'Welcome email after signup form',
        }
        
        context = template_contexts.get(template_type, 'General notification email')
        
        prompt = f"""Create an email template for: {context}

Form: {form_title}
Brand: {brand_name or 'Our Team'}
Available Fields: {[f.get('label') for f in (fields or [])]}

Use {{{{field_name}}}} placeholders for dynamic content.

Return JSON with:
{{
    "subject": "Email subject line",
    "preview_text": "Preview text (under 100 chars)",
    "headline": "Email headline",
    "body": "Main email body (markdown supported)",
    "cta_text": "Call to action text",
    "cta_url": "CTA URL with placeholder if needed",
    "footer": "Footer text"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You create professional email templates. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {
                'subject': f'Thank you for your {form_title} submission',
                'preview_text': 'We received your submission',
                'headline': 'Thank You',
                'body': 'We have received your submission and will be in touch soon.',
                'cta_text': 'Visit Our Website',
                'cta_url': '/',
                'footer': f'© {brand_name or "Our Team"}',
            }
    
    def generate_form_questions(
        self,
        topic: str,
        question_count: int = 5,
        question_type: str = 'open',
        context: str = None,
    ) -> List[Dict]:
        """Generate form questions for surveys, quizzes, etc."""
        
        prompt = f"""Generate {question_count} form questions about: {topic}

Question Type: {question_type} (open = text answers, choice = multiple choice)
Context: {context or 'General survey'}

For each question, return:
{{
    "id": "q_1",
    "type": "text|textarea|select|radio|checkbox",
    "label": "Question text",
    "options": ["Option 1", "Option 2"] // if applicable
    "required": true/false
}}

Make questions:
- Clear and unambiguous
- Relevant to the topic
- Progressively more detailed
- Include a mix of types

Return JSON array of questions.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You design effective survey questions. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return []
    
    def generate_validation_messages(
        self,
        field: Dict,
    ) -> Dict[str, str]:
        """Generate user-friendly validation error messages"""
        
        field_type = field.get('type')
        label = field.get('label')
        validation = field.get('validation', {})
        
        prompt = f"""Create user-friendly validation error messages for this form field.

Field: {label}
Type: {field_type}
Validation Rules: {json.dumps(validation)}

Return JSON with error messages for each possible validation failure:
{{
    "required": "Message when field is empty",
    "format": "Message when format is wrong (email, phone, etc.)",
    "min_length": "Message when too short",
    "max_length": "Message when too long",
    "pattern": "Message when pattern doesn't match",
    "min": "Message when value too low",
    "max": "Message when value too high"
}}

Messages should be:
- Friendly and helpful
- Specific to the field
- Suggest the correct format
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write helpful validation messages. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300,
            )
            
            return json.loads(response.choices[0].message.content)
        except:
            return {
                'required': f'{label} is required',
                'format': f'Please enter a valid {label.lower()}',
            }
    
    def generate_select_options(
        self,
        label: str,
        context: str = None,
        count: int = 5,
    ) -> List[str]:
        """Generate options for select/radio fields"""
        
        prompt = f"""Generate {count} options for a form dropdown/radio field.

Field Label: {label}
Context: {context or 'General form'}

Requirements:
- Relevant to the field label
- Common/expected choices
- Include "Other" if appropriate
- Clear and concise

Return JSON array of strings.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You generate relevant dropdown options. Return only valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=200,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return ['Option 1', 'Option 2', 'Option 3', 'Other']
    
    def improve_form_copy(
        self,
        schema: Dict,
        improvements: List[str] = None,
    ) -> Dict:
        """Improve all text content in a form"""
        
        if improvements is None:
            improvements = ['clarity', 'engagement', 'brevity']
        
        prompt = f"""Improve the text content in this form schema.

Current Schema:
{json.dumps(schema, indent=2)}

Improvements to make:
{', '.join(improvements)}

For each text element (title, description, labels, placeholders, help text):
- Make it clearer and more engaging
- Keep it concise
- Maintain professional tone
- Don't change field types or IDs

Return the improved schema as JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You improve form copy while maintaining structure. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return schema
    
    def generate_consent_text(
        self,
        purposes: List[str],
        company_name: str,
        privacy_url: str = None,
    ) -> Dict[str, str]:
        """Generate GDPR-compliant consent text"""
        
        prompt = f"""Generate GDPR-compliant consent text for a form.

Company: {company_name}
Purposes: {', '.join(purposes)}
Privacy Policy URL: {privacy_url or '/privacy'}

Return JSON with:
{{
    "data_processing": "Consent text for data processing",
    "marketing": "Consent text for marketing communications",
    "third_party": "Consent text for third-party sharing",
    "privacy_link_text": "Text for privacy policy link"
}}

Requirements:
- Clear and specific about data use
- GDPR compliant language
- Not overly legal/complex
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write GDPR-compliant consent text. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {
                'data_processing': f'I consent to {company_name} processing my data for the stated purposes.',
                'marketing': f'I agree to receive marketing communications from {company_name}.',
                'third_party': 'I consent to sharing my data with trusted partners.',
                'privacy_link_text': 'View our Privacy Policy',
            }
    
    def translate_form(
        self,
        schema: Dict,
        target_language: str,
    ) -> Dict:
        """Translate form content to another language"""
        
        prompt = f"""Translate all text content in this form schema to {target_language}.

Schema:
{json.dumps(schema, indent=2)}

Translate:
- Title and description
- Field labels
- Placeholders
- Help text
- Options for select/radio fields
- Validation messages

Keep:
- Field IDs unchanged
- Field types unchanged
- Structure unchanged

Return the translated schema as JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You translate form content to {target_language}. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            
            translated = json.loads(response.choices[0].message.content)
            translated['_language'] = target_language
            return translated
        except Exception as e:
            schema['_translation_error'] = str(e)
            return schema
    
    def generate_sms_template(
        self,
        purpose: str,
        form_title: str,
        fields: List[Dict] = None,
    ) -> str:
        """Generate SMS template (under 160 chars)"""
        
        prompt = f"""Write an SMS message for: {purpose}

Form: {form_title}
Available Fields: {[f.get('label') for f in (fields or [])]}

Use {{{{field_name}}}} for placeholders.

Requirements:
- Under 160 characters
- Clear and actionable
- Professional but friendly

Return only the SMS text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write concise SMS messages under 160 characters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=50,
            )
            
            return response.choices[0].message.content.strip()[:160]
        except Exception:
            return f"Thank you for submitting {form_title}. We'll be in touch soon."
    
    def generate_form_intro_script(
        self,
        form_title: str,
        purpose: str,
        estimated_time: int = 5,
    ) -> str:
        """Generate intro script for conversational forms"""
        
        prompt = f"""Write a friendly intro script for starting a conversational form.

Form: {form_title}
Purpose: {purpose}
Estimated Time: {estimated_time} minutes

The script should:
- Greet the user
- Explain what the form is for
- Set expectations (time, what info needed)
- Be conversational and warm
- Be 2-3 sentences

Return only the intro script.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write friendly conversational scripts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            
            return response.choices[0].message.content.strip()
        except Exception:
            return f"Hi there! I'll help you complete this {form_title}. It should only take about {estimated_time} minutes. Let's get started!"
    
    def suggest_form_improvements(
        self,
        schema: Dict,
        analytics: Dict = None,
    ) -> List[Dict[str, str]]:
        """Suggest content improvements based on schema and analytics"""
        
        context = {
            'field_count': len(schema.get('fields', [])),
            'has_description': bool(schema.get('description')),
            'fields_with_help': sum(1 for f in schema.get('fields', []) if f.get('help')),
            'fields_with_placeholder': sum(1 for f in schema.get('fields', []) if f.get('placeholder')),
        }
        
        if analytics:
            context['abandonment_rate'] = analytics.get('abandonment_rate', 0)
            context['conversion_rate'] = analytics.get('conversion_rate', 0)
        
        prompt = f"""Suggest content improvements for this form.

Schema Summary:
- Fields: {context['field_count']}
- Has Description: {context['has_description']}
- Fields with Help Text: {context['fields_with_help']}
- Fields with Placeholders: {context['fields_with_placeholder']}
{'- Abandonment Rate: ' + str(context.get('abandonment_rate')) + '%' if 'abandonment_rate' in context else ''}
{'- Conversion Rate: ' + str(context.get('conversion_rate')) + '%' if 'conversion_rate' in context else ''}

Fields:
{json.dumps(schema.get('fields', []), indent=2)}

Suggest 3-5 specific content improvements.

Return JSON array:
[
    {{
        "type": "description|placeholder|help_text|label|option",
        "field_id": "f_1 or null for form-level",
        "current": "Current text",
        "suggested": "Improved text",
        "reason": "Why this improves the form"
    }}
]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You suggest specific form copy improvements. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception:
            return []
