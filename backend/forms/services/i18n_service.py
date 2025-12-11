"""
Internationalization (i18n) service for multi-language support
"""
import openai
from django.conf import settings
from typing import Dict, List
import requests


class I18nService:
    """Handle form translations and language detection"""
    
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'native': 'English', 'rtl': False},
        'es': {'name': 'Spanish', 'native': 'Español', 'rtl': False},
        'fr': {'name': 'French', 'native': 'Français', 'rtl': False},
        'de': {'name': 'German', 'native': 'Deutsch', 'rtl': False},
        'it': {'name': 'Italian', 'native': 'Italiano', 'rtl': False},
        'pt': {'name': 'Portuguese', 'native': 'Português', 'rtl': False},
        'ar': {'name': 'Arabic', 'native': 'العربية', 'rtl': True},
        'he': {'name': 'Hebrew', 'native': 'עברית', 'rtl': True},
        'zh': {'name': 'Chinese', 'native': '中文', 'rtl': False},
        'ja': {'name': 'Japanese', 'native': '日本語', 'rtl': False},
        'ko': {'name': 'Korean', 'native': '한국어', 'rtl': False},
        'ru': {'name': 'Russian', 'native': 'Русский', 'rtl': False},
        'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'rtl': False},
    }
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def translate_form(self, form_schema: Dict, target_language: str, source_language: str = 'en') -> Dict:
        """
        Translate entire form schema to target language using AI
        """
        # Extract translatable content
        translatable_content = self._extract_translatable_content(form_schema)
        
        # Translate using OpenAI
        translations = self._translate_with_ai(
            translatable_content,
            source_language,
            target_language
        )
        
        # Apply translations back to schema
        translated_schema = self._apply_translations(form_schema, translations)
        
        return translated_schema
    
    def _extract_translatable_content(self, schema: Dict) -> List[str]:
        """Extract all text that needs translation from form schema"""
        translatable = []
        
        # Form title and description
        if 'title' in schema:
            translatable.append(schema['title'])
        if 'description' in schema:
            translatable.append(schema['description'])
        
        # Field labels, placeholders, and validation messages
        if 'fields' in schema:
            for field in schema['fields']:
                if 'label' in field:
                    translatable.append(field['label'])
                if 'placeholder' in field:
                    translatable.append(field['placeholder'])
                if 'helpText' in field:
                    translatable.append(field['helpText'])
                if 'options' in field:
                    for option in field['options']:
                        if isinstance(option, dict) and 'label' in option:
                            translatable.append(option['label'])
                        elif isinstance(option, str):
                            translatable.append(option)
                if 'validation' in field and 'message' in field['validation']:
                    translatable.append(field['validation']['message'])
        
        # Button texts
        if 'buttons' in schema:
            for button in schema['buttons']:
                if 'text' in button:
                    translatable.append(button['text'])
        
        # Success/error messages
        if 'messages' in schema:
            for key, message in schema['messages'].items():
                if isinstance(message, str):
                    translatable.append(message)
        
        return translatable
    
    def _translate_with_ai(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> Dict[str, str]:
        """Use OpenAI to translate texts"""
        if not texts:
            return {}
        
        # Create translation prompt
        prompt = f"""Translate the following form texts from {source_lang} to {target_lang}.
Maintain formatting, preserve placeholders like {{fieldName}}, and keep technical terms accurate.
Return ONLY a JSON object mapping original text to translated text.

Texts to translate:
{chr(10).join(f'{i+1}. {text}' for i, text in enumerate(texts))}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in form localization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            import json
            translations = json.loads(response.choices[0].message.content)
            return translations
            
        except Exception as e:
            print(f"Translation error: {e}")
            return {text: text for text in texts}  # Return original if translation fails
    
    def _apply_translations(self, schema: Dict, translations: Dict[str, str]) -> Dict:
        """Apply translations to form schema"""
        import copy
        translated = copy.deepcopy(schema)
        
        # Translate title and description
        if 'title' in translated and translated['title'] in translations:
            translated['title'] = translations[translated['title']]
        if 'description' in translated and translated['description'] in translations:
            translated['description'] = translations[translated['description']]
        
        # Translate fields
        if 'fields' in translated:
            for field in translated['fields']:
                if 'label' in field and field['label'] in translations:
                    field['label'] = translations[field['label']]
                if 'placeholder' in field and field['placeholder'] in translations:
                    field['placeholder'] = translations[field['placeholder']]
                if 'helpText' in field and field['helpText'] in translations:
                    field['helpText'] = translations[field['helpText']]
                
                # Translate options
                if 'options' in field:
                    for i, option in enumerate(field['options']):
                        if isinstance(option, dict) and 'label' in option:
                            if option['label'] in translations:
                                field['options'][i]['label'] = translations[option['label']]
                        elif isinstance(option, str) and option in translations:
                            field['options'][i] = translations[option]
        
        return translated
    
    def detect_language_from_browser(self, accept_language_header: str) -> str:
        """Detect preferred language from browser Accept-Language header"""
        if not accept_language_header:
            return 'en'
        
        # Parse Accept-Language header
        languages = []
        for lang in accept_language_header.split(','):
            parts = lang.strip().split(';')
            code = parts[0].split('-')[0].lower()
            quality = 1.0
            if len(parts) > 1 and parts[1].startswith('q='):
                try:
                    quality = float(parts[1][2:])
                except ValueError:
                    pass
            languages.append((code, quality))
        
        # Sort by quality and find first supported language
        languages.sort(key=lambda x: x[1], reverse=True)
        for code, _ in languages:
            if code in self.SUPPORTED_LANGUAGES:
                return code
        
        return 'en'  # Default to English
    
    def detect_language_from_ip(self, ip_address: str) -> str:
        """Detect language based on IP geolocation"""
        try:
            # Using ipapi.co for geolocation
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=3)
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('country_code', '').upper()
                
                # Map countries to languages
                country_to_lang = {
                    'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en',
                    'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es',
                    'FR': 'fr', 'BE': 'fr', 'CH': 'fr',
                    'DE': 'de', 'AT': 'de',
                    'IT': 'it',
                    'PT': 'pt', 'BR': 'pt',
                    'SA': 'ar', 'AE': 'ar', 'EG': 'ar',
                    'IL': 'he',
                    'CN': 'zh', 'TW': 'zh',
                    'JP': 'ja',
                    'KR': 'ko',
                    'RU': 'ru',
                    'IN': 'hi',
                }
                
                return country_to_lang.get(country_code, 'en')
        except Exception as e:
            print(f"IP geolocation error: {e}")
        
        return 'en'
    
    def translate_submission_export(
        self,
        submission_data: Dict,
        field_schema: Dict,
        target_language: str
    ) -> Dict:
        """Translate submission field names for export"""
        # Extract field labels from schema
        field_labels = {}
        for field in field_schema.get('fields', []):
            field_id = field.get('id')
            field_label = field.get('label')
            if field_id and field_label:
                field_labels[field_id] = field_label
        
        # Translate labels
        if field_labels:
            translated_labels = self._translate_with_ai(
                list(field_labels.values()),
                'en',
                target_language
            )
            
            # Create translated submission
            translated_data = {}
            for field_id, value in submission_data.items():
                original_label = field_labels.get(field_id, field_id)
                translated_label = translated_labels.get(original_label, original_label)
                translated_data[translated_label] = value
            
            return translated_data
        
        return submission_data
    
    def get_rtl_languages(self) -> List[str]:
        """Get list of right-to-left languages"""
        return [code for code, info in self.SUPPORTED_LANGUAGES.items() if info['rtl']]
    
    def validate_translation(self, original: str, translated: str, language: str) -> Dict:
        """Validate translation quality"""
        return {
            'is_valid': len(translated) > 0,
            'length_difference': abs(len(translated) - len(original)),
            'has_placeholders': '{' in original and '{' in translated,
            'is_rtl': self.SUPPORTED_LANGUAGES.get(language, {}).get('rtl', False)
        }
