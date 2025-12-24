"""
AI Service for generating form schemas using OpenAI
"""
import json
import re
from typing import Dict, Any, Optional
from django.conf import settings


class FormGeneratorService:
    """Service to generate form schemas from natural language descriptions"""
    
    SYSTEM_PROMPT = """You are FormForge Assistant — an expert form designer that outputs precise JSON form schemas. Return ONLY JSON. Follow this JSON schema structure:
{
 "title": string,
 "description": string,
 "fields": [ { "id": string, "type": string, "label": string, "placeholder": string, "required": bool, "validation": {...}, "options": [...], "help": string } ],
 "logic": [ { "if": { "field": string, "operator": "equals|in|contains|gte|lte" ,"value": any }, "show": [field_ids], "hide": [field_ids] } ],
 "settings": { "consent_text": string, "redirect": string, "integrations": { "google_sheets": bool, "webhook": bool } }
}
Do not include explanatory text. Generate helpful, short placeholders and id values like f_1, f_2. Keep field types to: text, email, phone, textarea, number, date, time, select, multiselect, checkbox, radio, file, url, payment. Validate emails and phone format where appropriate."""

    FEW_SHOT_EXAMPLES = [
        {
            "role": "user",
            "content": "Create a client intake for wedding photographer — ask about event date, location, estimated guest count, package interest, deposit payment option, and space for questions"
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "title": "Wedding Photography Client Intake",
                "description": "Collect event details and payment preferences.",
                "fields": [
                    {"id":"f_1","type":"text","label":"Full name","placeholder":"Jane and John","required":True},
                    {"id":"f_2","type":"email","label":"Email address","placeholder":"you@example.com","required":True},
                    {"id":"f_3","type":"phone","label":"Phone number","placeholder":"+1 555 555 5555","required":True},
                    {"id":"f_4","type":"date","label":"Event date","required":True},
                    {"id":"f_5","type":"text","label":"Event location","placeholder":"City, venue, or address","required":True},
                    {"id":"f_6","type":"number","label":"Estimated guest count","placeholder":"e.g. 120"},
                    {"id":"f_7","type":"select","label":"Package interested","options":["Basic","Premium","Deluxe"],"required":True},
                    {"id":"f_8","type":"checkbox","label":"Would you like to pay deposit now?"},
                    {"id":"f_9","type":"payment","label":"Deposit amount"}
                ],
                "logic": [
                    {"if":{"field":"f_8","operator":"equals","value":True},"show":["f_9"],"hide":[]}
                ],
                "settings":{"consent_text":"By submitting you agree to be contacted...","redirect":"/thank-you","integrations":{"google_sheets":True,"webhook":True}}
            })
        },
        {
            "role": "user",
            "content": "Create a client intake form for a nutritionist. Must collect: full name, email, phone, date of birth, primary health goals (weight loss, muscle gain, improve digestion, other), dietary restrictions (multi-select), current medications, preferred consultation type (in-person/virtual), budget per month, and a short 'tell me about your goals' textarea. If 'other' selected in health goals, show a text field 'Please describe'. Include GDPR consent."
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "title":"Nutritionist Client Intake",
                "description":"Tell us about your health goals so we can plan your program.",
                "fields":[
                    {"id":"f_1","type":"text","label":"Full name","placeholder":"Jane Doe","required":True},
                    {"id":"f_2","type":"email","label":"Email address","placeholder":"you@example.com","required":True},
                    {"id":"f_3","type":"phone","label":"Phone","required":True},
                    {"id":"f_4","type":"date","label":"Date of birth","required":True},
                    {"id":"f_5","type":"multiselect","label":"Primary health goals","options":["Weight loss","Muscle gain","Improve digestion","Other"],"required":True},
                    {"id":"f_6","type":"text","label":"If Other, please describe","placeholder":"Describe your goal"},
                    {"id":"f_7","type":"multiselect","label":"Dietary restrictions","options":["Vegan","Vegetarian","Gluten-free","Dairy-free","Nut allergy","None","Other"]},
                    {"id":"f_8","type":"textarea","label":"Current medications","placeholder":"List any medications you're taking"},
                    {"id":"f_9","type":"textarea","label":"Tell us about your goals","placeholder":"What do you want to achieve?"},
                    {"id":"f_10","type":"select","label":"Consultation type","options":["In-person","Virtual"],"required":True},
                    {"id":"f_11","type":"number","label":"Budget per month (USD)","placeholder":"e.g. 150"},
                    {"id":"f_12","type":"checkbox","label":"I consent to the processing of my data for service delivery","required":True}
                ],
                "logic":[
                    {"if":{"field":"f_5","operator":"contains","value":"Other"},"show":["f_6"],"hide":[]}
                ],
                "settings":{
                    "consent_text":"I agree to receive emails related to my consultation and accept the privacy policy.",
                    "redirect":"/thank-you",
                    "integrations":{"google_sheets":True,"webhook":True}
                }
            })
        }
    ]
    
    def __init__(self):
        self.openai_available = False
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if api_key and api_key != 'your-openai-api-key' and len(api_key) > 20:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.openai_available = True
            except Exception:
                self.openai_available = False
    
    def generate_form_schema(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a form schema from a natural language description
        
        Args:
            prompt: Natural language description of the form
            context: Optional context about business type or tags
            
        Returns:
            Dictionary containing the generated form schema
        """
        # If OpenAI is not available, use template-based generation
        if not self.openai_available:
            return self._generate_fallback_schema(prompt, context)
        
        user_message = f"Create a form for: {prompt}"
        if context:
            user_message += f"\nContext: {context}"
        user_message += "\nReturn JSON only."
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            *self.FEW_SHOT_EXAMPLES,
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            schema = json.loads(response.choices[0].message.content)
            return schema
            
        except Exception as e:
            raise ValueError(f"Failed to generate form schema: {str(e)}")
    
    def _generate_fallback_schema(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a form schema using template-based approach when OpenAI is not available.
        Analyzes the prompt to determine form type and generates appropriate fields.
        """
        prompt_lower = prompt.lower()
        
        # Detect form type based on keywords
        form_types = {
            'contact': ['contact', 'inquiry', 'message', 'get in touch', 'reach out'],
            'registration': ['registration', 'register', 'signup', 'sign up', 'enrollment', 'enroll'],
            'feedback': ['feedback', 'survey', 'review', 'satisfaction', 'opinion'],
            'booking': ['booking', 'appointment', 'schedule', 'reservation', 'book'],
            'application': ['application', 'apply', 'job', 'career', 'position'],
            'order': ['order', 'purchase', 'buy', 'product', 'shop'],
            'intake': ['intake', 'client', 'patient', 'consultation', 'assessment'],
            'event': ['event', 'rsvp', 'wedding', 'party', 'conference'],
            'quote': ['quote', 'estimate', 'pricing', 'cost', 'request'],
        }
        
        detected_type = 'contact'  # Default
        for form_type, keywords in form_types.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_type = form_type
                break
        
        # Template schemas
        templates = {
            'contact': {
                "title": "Contact Form",
                "description": "Get in touch with us.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Full Name", "placeholder": "John Doe", "required": True},
                    {"id": "f_2", "type": "email", "label": "Email Address", "placeholder": "you@example.com", "required": True},
                    {"id": "f_3", "type": "phone", "label": "Phone Number", "placeholder": "+1 555 555 5555", "required": False},
                    {"id": "f_4", "type": "select", "label": "Subject", "options": ["General Inquiry", "Support", "Sales", "Partnership", "Other"], "required": True},
                    {"id": "f_5", "type": "textarea", "label": "Message", "placeholder": "How can we help you?", "required": True}
                ],
                "logic": [],
                "settings": {"consent_text": "By submitting, you agree to our privacy policy.", "redirect": "/thank-you", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'registration': {
                "title": "Registration Form",
                "description": "Sign up to get started.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "First Name", "placeholder": "John", "required": True},
                    {"id": "f_2", "type": "text", "label": "Last Name", "placeholder": "Doe", "required": True},
                    {"id": "f_3", "type": "email", "label": "Email Address", "placeholder": "you@example.com", "required": True},
                    {"id": "f_4", "type": "phone", "label": "Phone Number", "placeholder": "+1 555 555 5555", "required": False},
                    {"id": "f_5", "type": "text", "label": "Company/Organization", "placeholder": "Your company name", "required": False},
                    {"id": "f_6", "type": "select", "label": "How did you hear about us?", "options": ["Google", "Social Media", "Friend/Referral", "Advertisement", "Other"], "required": False},
                    {"id": "f_7", "type": "checkbox", "label": "I agree to the terms and conditions", "required": True}
                ],
                "logic": [],
                "settings": {"consent_text": "By registering, you agree to receive updates and communications.", "redirect": "/welcome", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'feedback': {
                "title": "Feedback Form",
                "description": "We value your feedback.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Name", "placeholder": "Your name", "required": False},
                    {"id": "f_2", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": False},
                    {"id": "f_3", "type": "rating", "label": "Overall Satisfaction", "maxRating": 5, "required": True},
                    {"id": "f_4", "type": "select", "label": "What are you providing feedback about?", "options": ["Product", "Service", "Website", "Customer Support", "Other"], "required": True},
                    {"id": "f_5", "type": "textarea", "label": "Your Feedback", "placeholder": "Please share your thoughts...", "required": True},
                    {"id": "f_6", "type": "checkbox", "label": "You may contact me about my feedback", "required": False}
                ],
                "logic": [],
                "settings": {"consent_text": "Thank you for helping us improve.", "redirect": "/thank-you", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'booking': {
                "title": "Booking Request",
                "description": "Schedule an appointment with us.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Full Name", "placeholder": "John Doe", "required": True},
                    {"id": "f_2", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": True},
                    {"id": "f_3", "type": "phone", "label": "Phone", "placeholder": "+1 555 555 5555", "required": True},
                    {"id": "f_4", "type": "date", "label": "Preferred Date", "required": True},
                    {"id": "f_5", "type": "time", "label": "Preferred Time", "required": True},
                    {"id": "f_6", "type": "select", "label": "Service Type", "options": ["Consultation", "Meeting", "Demo", "Other"], "required": True},
                    {"id": "f_7", "type": "textarea", "label": "Additional Notes", "placeholder": "Any special requests or information...", "required": False}
                ],
                "logic": [],
                "settings": {"consent_text": "We'll confirm your booking via email.", "redirect": "/booking-confirmed", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'intake': {
                "title": "Client Intake Form",
                "description": "Help us understand your needs.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Full Name", "placeholder": "Jane Doe", "required": True},
                    {"id": "f_2", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": True},
                    {"id": "f_3", "type": "phone", "label": "Phone", "placeholder": "+1 555 555 5555", "required": True},
                    {"id": "f_4", "type": "date", "label": "Date of Birth", "required": False},
                    {"id": "f_5", "type": "text", "label": "Address", "placeholder": "Your address", "required": False},
                    {"id": "f_6", "type": "select", "label": "Preferred Contact Method", "options": ["Email", "Phone", "Text Message"], "required": True},
                    {"id": "f_7", "type": "textarea", "label": "What brings you here today?", "placeholder": "Please describe your goals or concerns...", "required": True},
                    {"id": "f_8", "type": "textarea", "label": "Additional Information", "placeholder": "Anything else we should know?", "required": False},
                    {"id": "f_9", "type": "checkbox", "label": "I consent to the collection and processing of my data", "required": True}
                ],
                "logic": [],
                "settings": {"consent_text": "Your information is kept confidential.", "redirect": "/thank-you", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'event': {
                "title": "Event Registration",
                "description": "Register for our upcoming event.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Full Name", "placeholder": "John Doe", "required": True},
                    {"id": "f_2", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": True},
                    {"id": "f_3", "type": "phone", "label": "Phone", "placeholder": "+1 555 555 5555", "required": False},
                    {"id": "f_4", "type": "text", "label": "Company/Organization", "placeholder": "Your company", "required": False},
                    {"id": "f_5", "type": "number", "label": "Number of Attendees", "placeholder": "1", "required": True},
                    {"id": "f_6", "type": "multiselect", "label": "Dietary Requirements", "options": ["None", "Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher", "Other"], "required": False},
                    {"id": "f_7", "type": "text", "label": "Special Requirements", "placeholder": "Accessibility needs, etc.", "required": False},
                    {"id": "f_8", "type": "checkbox", "label": "I agree to the event terms and conditions", "required": True}
                ],
                "logic": [],
                "settings": {"consent_text": "We'll send event details to your email.", "redirect": "/registration-complete", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'quote': {
                "title": "Request a Quote",
                "description": "Get a personalized quote for our services.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Full Name", "placeholder": "John Doe", "required": True},
                    {"id": "f_2", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": True},
                    {"id": "f_3", "type": "phone", "label": "Phone", "placeholder": "+1 555 555 5555", "required": True},
                    {"id": "f_4", "type": "text", "label": "Company", "placeholder": "Your company name", "required": False},
                    {"id": "f_5", "type": "select", "label": "Service Interested In", "options": ["Basic Package", "Standard Package", "Premium Package", "Custom Solution"], "required": True},
                    {"id": "f_6", "type": "number", "label": "Budget (USD)", "placeholder": "Estimated budget", "required": False},
                    {"id": "f_7", "type": "textarea", "label": "Project Details", "placeholder": "Tell us about your project...", "required": True},
                    {"id": "f_8", "type": "select", "label": "Timeline", "options": ["ASAP", "Within 1 month", "1-3 months", "3+ months", "Flexible"], "required": True}
                ],
                "logic": [],
                "settings": {"consent_text": "We'll get back to you within 24 hours.", "redirect": "/quote-requested", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'application': {
                "title": "Application Form",
                "description": "Apply to join our team.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Full Name", "placeholder": "John Doe", "required": True},
                    {"id": "f_2", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": True},
                    {"id": "f_3", "type": "phone", "label": "Phone", "placeholder": "+1 555 555 5555", "required": True},
                    {"id": "f_4", "type": "url", "label": "LinkedIn Profile", "placeholder": "https://linkedin.com/in/...", "required": False},
                    {"id": "f_5", "type": "select", "label": "Position Applied For", "options": ["Developer", "Designer", "Marketing", "Sales", "Operations", "Other"], "required": True},
                    {"id": "f_6", "type": "number", "label": "Years of Experience", "placeholder": "5", "required": True},
                    {"id": "f_7", "type": "file", "label": "Resume/CV", "required": True},
                    {"id": "f_8", "type": "textarea", "label": "Why do you want to join us?", "placeholder": "Tell us about yourself...", "required": True},
                    {"id": "f_9", "type": "checkbox", "label": "I confirm that all information provided is accurate", "required": True}
                ],
                "logic": [],
                "settings": {"consent_text": "Your application will be reviewed within 5 business days.", "redirect": "/application-submitted", "integrations": {"google_sheets": True, "webhook": True}}
            },
            'order': {
                "title": "Order Form",
                "description": "Place your order with us.",
                "fields": [
                    {"id": "f_1", "type": "text", "label": "Full Name", "placeholder": "John Doe", "required": True},
                    {"id": "f_2", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": True},
                    {"id": "f_3", "type": "phone", "label": "Phone", "placeholder": "+1 555 555 5555", "required": True},
                    {"id": "f_4", "type": "address", "label": "Shipping Address", "includeCountry": True, "includeZip": True, "required": True},
                    {"id": "f_5", "type": "select", "label": "Product", "options": ["Product A", "Product B", "Product C", "Bundle Deal"], "required": True},
                    {"id": "f_6", "type": "number", "label": "Quantity", "placeholder": "1", "required": True},
                    {"id": "f_7", "type": "textarea", "label": "Special Instructions", "placeholder": "Any special requests...", "required": False},
                    {"id": "f_8", "type": "checkbox", "label": "I agree to the terms of sale", "required": True}
                ],
                "logic": [],
                "settings": {"consent_text": "Order confirmation will be sent to your email.", "redirect": "/order-complete", "integrations": {"google_sheets": True, "webhook": True}}
            }
        }
        
        schema = templates.get(detected_type, templates['contact'])
        
        # Try to extract a title from the prompt
        title_patterns = [
            r'(?:create|make|build|generate)\s+(?:a|an)?\s*(.+?)(?:\s+form|\s+for|\.|$)',
            r'(?:form|intake)\s+for\s+(.+?)(?:\s+—|\s+-|\.|$)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                title_base = match.group(1).strip().title()
                if len(title_base) > 5 and len(title_base) < 50:
                    schema['title'] = f"{title_base} Form"
                    break
        
        return schema

    def generate_validation_rules(self, schema_json: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation rules for form fields"""
        if not self.openai_available:
            # Return basic validation rules
            rules = {}
            for field in schema_json.get('fields', []):
                field_id = field.get('id')
                field_type = field.get('type')
                if field_type == 'email':
                    rules[field_id] = {'pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$', 'required': field.get('required', False)}
                elif field_type == 'phone':
                    rules[field_id] = {'pattern': r'^\+?[\d\s\-\(\)]{7,}$', 'required': field.get('required', False)}
                elif field_type == 'url':
                    rules[field_id] = {'pattern': r'^https?://.+', 'required': field.get('required', False)}
                else:
                    rules[field_id] = {'required': field.get('required', False)}
            return rules
            
        prompt = f"Given the form JSON: {json.dumps(schema_json)}, output an object mapping each field id to a validation rule set (regex, min/max, required) in JSON only."
        
        messages = [
            {"role": "system", "content": "You are a validation expert. Return only JSON with validation rules."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception:
            return {}
    
    def generate_privacy_text(self, business_type: str) -> Dict[str, str]:
        """Generate privacy and consent text"""
        if not self.openai_available:
            return {
                "consent_text": f"By submitting this form, you agree to our privacy policy and consent to be contacted regarding your {business_type} inquiry.",
                "privacy_summary": f"We collect and process your information to provide our {business_type} services. Your data is stored securely and protected. We do not share your personal information with third parties without your explicit consent. You may request access to, correction of, or deletion of your data at any time."
            }
            
        prompt = f"Given business type '{business_type}' and required legal items (GDPR, marketing opt-in), produce a short consent_text under 250 characters and a longer privacy_summary (300-600 chars). Return JSON with keys 'consent_text' and 'privacy_summary'."
        
        messages = [
            {"role": "system", "content": "You are a legal compliance expert. Return only JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.5,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception:
            return {
                "consent_text": "By submitting, you agree to our privacy policy and terms of service.",
                "privacy_summary": "We collect and process your information to provide our services. Your data is stored securely and never shared without your consent."
            }
    
    def generate_email_summary(self, payload_json: Dict[str, Any]) -> str:
        """Generate professional email summary of submission"""
        if not self.openai_available:
            # Generate a simple summary without AI
            field_count = len(payload_json)
            summary_lines = []
            for key, value in list(payload_json.items())[:5]:  # First 5 fields
                if value and str(value).strip():
                    # Clean up the key for display
                    clean_key = key.replace('_', ' ').replace('f ', 'Field ').title()
                    summary_lines.append(f"• {clean_key}: {value}")
            
            summary = f"New form submission received with {field_count} fields completed.\n\n"
            if summary_lines:
                summary += "Key Information:\n" + "\n".join(summary_lines)
            summary += "\n\nPlease review and respond to this submission at your earliest convenience."
            return summary
            
        prompt = f"Generate a 3-4 sentence professional email summary of the submission using this payload: {json.dumps(payload_json)}. Include call-to-action to reply."
        
        messages = [
            {"role": "system", "content": "You are a professional email writer."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception:
            return f"New form submission received with {len(payload_json)} fields completed."
