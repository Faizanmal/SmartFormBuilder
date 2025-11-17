"""
AI Service for generating form schemas using OpenAI
"""
import json
from typing import Dict, Any, Optional
from openai import OpenAI
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
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_form_schema(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a form schema from a natural language description
        
        Args:
            prompt: Natural language description of the form
            context: Optional context about business type or tags
            
        Returns:
            Dictionary containing the generated form schema
        """
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
    
    def generate_validation_rules(self, schema_json: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation rules for form fields"""
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
            
        except Exception as e:
            return {}
    
    def generate_privacy_text(self, business_type: str) -> Dict[str, str]:
        """Generate privacy and consent text"""
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
            
        except Exception as e:
            return {
                "consent_text": "By submitting, you agree to our privacy policy and terms of service.",
                "privacy_summary": "We collect and process your information to provide our services. Your data is stored securely and never shared without your consent."
            }
    
    def generate_email_summary(self, payload_json: Dict[str, Any]) -> str:
        """Generate professional email summary of submission"""
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
            
        except Exception as e:
            return f"New form submission received with {len(payload_json)} fields completed."
