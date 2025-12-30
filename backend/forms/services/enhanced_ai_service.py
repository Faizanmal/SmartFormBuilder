"""
Enhanced AI Service with Multi-Provider Support

Features:
- Claude, Gemini, OpenAI integration
- Smart form layout suggestions
- Computer vision heatmap analysis
- Automated form personalization
- Conversational AI chatbots
"""
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


class EnhancedAIService:
    """Multi-provider AI service for form optimization"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available AI providers"""
        # OpenAI
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        if openai_key and openai_key != 'your-openai-api-key':
            try:
                from openai import OpenAI
                self.providers['openai'] = OpenAI(api_key=openai_key)
            except Exception:
                pass
        
        # Anthropic Claude
        anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        if anthropic_key:
            try:
                import anthropic
                self.providers['anthropic'] = anthropic.Anthropic(api_key=anthropic_key)
            except Exception:
                pass
        
        # Google Gemini
        google_key = getattr(settings, 'GOOGLE_AI_API_KEY', None)
        if google_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_key)
                self.providers['google'] = genai
            except Exception:
                pass
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return list(self.providers.keys())
    
    def generate_completion(
        self,
        prompt: str,
        provider: str = 'openai',
        model: str = None,
        system_prompt: str = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate AI completion using specified provider
        """
        if provider not in self.providers:
            # Fallback to available provider
            if self.providers:
                provider = list(self.providers.keys())[0]
            else:
                return {'error': 'No AI provider configured', 'content': None}
        
        try:
            if provider == 'openai':
                return self._openai_completion(prompt, system_prompt, model or 'gpt-4o', max_tokens, temperature)
            elif provider == 'anthropic':
                return self._anthropic_completion(prompt, system_prompt, model or 'claude-3-5-sonnet-20241022', max_tokens, temperature)
            elif provider == 'google':
                return self._gemini_completion(prompt, system_prompt, model or 'gemini-pro', max_tokens, temperature)
        except Exception as e:
            return {'error': str(e), 'content': None}
    
    def _openai_completion(self, prompt: str, system_prompt: str, model: str, max_tokens: int, temperature: float) -> Dict:
        """OpenAI completion"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.providers['openai'].chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return {
            'content': response.choices[0].message.content,
            'provider': 'openai',
            'model': model,
            'tokens_used': response.usage.total_tokens if response.usage else 0,
        }
    
    def _anthropic_completion(self, prompt: str, system_prompt: str, model: str, max_tokens: int, temperature: float) -> Dict:
        """Anthropic Claude completion"""
        message = self.providers['anthropic'].messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        
        return {
            'content': message.content[0].text,
            'provider': 'anthropic',
            'model': model,
            'tokens_used': message.usage.input_tokens + message.usage.output_tokens,
        }
    
    def _gemini_completion(self, prompt: str, system_prompt: str, model: str, max_tokens: int, temperature: float) -> Dict:
        """Google Gemini completion"""
        genai = self.providers['google']
        model_instance = genai.GenerativeModel(model)
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = model_instance.generate_content(full_prompt)
        
        return {
            'content': response.text,
            'provider': 'google',
            'model': model,
            'tokens_used': 0,  # Gemini doesn't provide token counts the same way
        }


class LayoutOptimizationService:
    """AI-powered form layout optimization"""
    
    def __init__(self):
        self.ai_service = EnhancedAIService()
    
    def analyze_heatmap_for_suggestions(
        self,
        form,
        heatmap_data: Dict[str, Any],
        interaction_patterns: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Analyze heatmap data and generate layout suggestions
        """
        from forms.models_emerging_tech import AILayoutSuggestion
        
        suggestions = []
        
        # Analyze click distribution
        click_hotspots = self._identify_hotspots(heatmap_data.get('clicks', []))
        cold_zones = self._identify_cold_zones(heatmap_data.get('clicks', []))
        
        # Analyze scroll depth
        scroll_data = heatmap_data.get('scroll', {})
        avg_scroll_depth = scroll_data.get('avg_depth', 100)
        
        # Analyze field completion patterns
        field_patterns = interaction_patterns.get('field_completion', {})
        drop_off_fields = self._identify_drop_off_points(field_patterns)
        
        # Generate suggestions based on analysis
        
        # 1. Check for fields below average scroll depth
        if avg_scroll_depth < 70:
            schema = form.schema_json.get('fields', [])
            below_fold_fields = [f for i, f in enumerate(schema) if i > len(schema) * (avg_scroll_depth / 100)]
            if below_fold_fields:
                suggestions.append({
                    'suggestion_type': 'field_order',
                    'priority': 'high',
                    'title': 'Move important fields above the fold',
                    'description': f'{len(below_fold_fields)} fields are below the average scroll depth',
                    'rationale': 'Users typically only scroll to {:.0f}% of the form. Consider moving critical fields higher.'.format(avg_scroll_depth),
                    'field_ids': [f.get('id') for f in below_fold_fields[:3]],
                    'predicted_conversion_lift': 5.0 + (100 - avg_scroll_depth) * 0.1,
                    'confidence_score': 0.75,
                })
        
        # 2. Check for high drop-off fields
        for field_id, drop_rate in drop_off_fields.items():
            if drop_rate > 0.2:  # More than 20% drop off
                suggestions.append({
                    'suggestion_type': 'field_visibility',
                    'priority': 'critical' if drop_rate > 0.4 else 'high',
                    'title': f'High drop-off detected on field',
                    'description': f'Field {field_id} has a {drop_rate*100:.1f}% drop-off rate',
                    'rationale': 'Consider simplifying this field, making it optional, or providing better help text.',
                    'field_ids': [field_id],
                    'predicted_conversion_lift': drop_rate * 50,
                    'confidence_score': 0.85,
                })
        
        # 3. Check for cold zones (unengaged areas)
        if cold_zones:
            suggestions.append({
                'suggestion_type': 'visual_hierarchy',
                'priority': 'medium',
                'title': 'Low engagement areas detected',
                'description': f'{len(cold_zones)} areas have minimal user interaction',
                'rationale': 'These areas may need visual enhancement or content reorganization.',
                'heatmap_data': {'cold_zones': cold_zones},
                'predicted_conversion_lift': 2.0,
                'confidence_score': 0.65,
            })
        
        # Use AI to generate additional insights
        if self.ai_service.get_available_providers():
            ai_suggestions = self._get_ai_layout_suggestions(form, heatmap_data, interaction_patterns)
            suggestions.extend(ai_suggestions)
        
        # Save suggestions to database
        for suggestion_data in suggestions:
            AILayoutSuggestion.objects.create(
                form=form,
                **suggestion_data,
                heatmap_data=heatmap_data,
                interaction_patterns=interaction_patterns,
            )
        
        return suggestions
    
    def _identify_hotspots(self, click_data: List[Dict]) -> List[Dict]:
        """Identify high-activity hotspots from click data"""
        # Group clicks by region
        regions = {}
        for click in click_data:
            x, y = int(click.get('x', 0) / 10) * 10, int(click.get('y', 0) / 10) * 10
            key = f"{x},{y}"
            regions[key] = regions.get(key, 0) + 1
        
        # Find hotspots (regions with significantly more clicks)
        if not regions:
            return []
        
        avg_clicks = sum(regions.values()) / len(regions)
        hotspots = [
            {'region': k, 'clicks': v, 'intensity': v / avg_clicks}
            for k, v in regions.items()
            if v > avg_clicks * 2
        ]
        
        return sorted(hotspots, key=lambda x: x['intensity'], reverse=True)[:10]
    
    def _identify_cold_zones(self, click_data: List[Dict]) -> List[Dict]:
        """Identify low-activity cold zones"""
        # Similar to hotspots but find areas with minimal interaction
        regions = {}
        for click in click_data:
            x, y = int(click.get('x', 0) / 10) * 10, int(click.get('y', 0) / 10) * 10
            key = f"{x},{y}"
            regions[key] = regions.get(key, 0) + 1
        
        if not regions:
            return []
        
        avg_clicks = sum(regions.values()) / len(regions)
        cold_zones = [
            {'region': k, 'clicks': v}
            for k, v in regions.items()
            if v < avg_clicks * 0.2
        ]
        
        return cold_zones[:5]
    
    def _identify_drop_off_points(self, field_patterns: Dict) -> Dict[str, float]:
        """Identify fields with high drop-off rates"""
        drop_offs = {}
        for field_id, data in field_patterns.items():
            started = data.get('started', 0)
            completed = data.get('completed', 0)
            if started > 10:  # Minimum sample size
                drop_offs[field_id] = 1 - (completed / started)
        return drop_offs
    
    def _get_ai_layout_suggestions(
        self,
        form,
        heatmap_data: Dict,
        interaction_patterns: Dict,
    ) -> List[Dict]:
        """Get AI-generated layout suggestions"""
        prompt = f"""Analyze this form data and suggest layout optimizations:

Form Schema:
{json.dumps(form.schema_json.get('fields', [])[:10], indent=2)}

Heatmap Summary:
- Average scroll depth: {heatmap_data.get('scroll', {}).get('avg_depth', 'N/A')}%
- Hotspot count: {len(heatmap_data.get('clicks', []))}

Field Completion Patterns:
{json.dumps(interaction_patterns.get('field_completion', {}), indent=2)}

Provide 2-3 specific, actionable layout suggestions in JSON format:
[
    {{
        "suggestion_type": "field_order|field_grouping|remove_field|field_size|visual_hierarchy",
        "priority": "critical|high|medium|low",
        "title": "Short title",
        "description": "Detailed description",
        "rationale": "Why this will help",
        "predicted_conversion_lift": 0.0-20.0,
        "confidence_score": 0.0-1.0
    }}
]
"""
        
        response = self.ai_service.generate_completion(
            prompt=prompt,
            system_prompt="You are a UX expert specializing in form optimization. Provide data-driven suggestions.",
            max_tokens=1000,
        )
        
        if response.get('content'):
            try:
                # Extract JSON from response
                content = response['content']
                start = content.find('[')
                end = content.rfind(']') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
            except json.JSONDecodeError:
                pass
        
        return []


class ConversationalFormService:
    """AI chatbot for conversational form filling"""
    
    def __init__(self):
        self.ai_service = EnhancedAIService()
    
    def start_conversation(
        self,
        form,
        session_id: str,
        user_identifier: str = None,
        language: str = 'en',
    ) -> Dict[str, Any]:
        """Start a new conversational form session"""
        from forms.models_emerging_tech import ConversationalAIConfig, ConversationSession
        
        # Get or create config
        config, _ = ConversationalAIConfig.objects.get_or_create(
            form=form,
            defaults={'is_enabled': True}
        )
        
        if not config.is_enabled:
            return {'error': 'Conversational AI is not enabled for this form'}
        
        # Create session
        session = ConversationSession.objects.create(
            form=form,
            config=config,
            session_id=session_id,
            user_identifier=user_identifier or '',
            language_detected=language,
        )
        
        # Generate welcome message
        welcome = self._generate_welcome_message(form, config, language)
        
        # Store message
        self._save_message(session, 'assistant', welcome)
        
        return {
            'session_id': session_id,
            'message': welcome,
            'current_field': self._get_first_field(form),
            'progress': 0,
        }
    
    def process_user_message(
        self,
        session_id: str,
        user_message: str,
        input_method: str = 'text',
    ) -> Dict[str, Any]:
        """Process user message and generate response"""
        from forms.models_emerging_tech import ConversationSession, ConversationMessage
        
        try:
            session = ConversationSession.objects.get(session_id=session_id, status='active')
        except ConversationSession.DoesNotExist:
            return {'error': 'Session not found or expired'}
        
        form = session.form
        config = session.config
        
        # Save user message
        self._save_message(session, 'user', user_message, input_method=input_method)
        
        # Get current field
        fields = form.schema_json.get('fields', [])
        current_index = session.current_field_index
        
        if current_index >= len(fields):
            # Form complete
            return self._complete_conversation(session)
        
        current_field = fields[current_index]
        
        # Parse user response
        parsed_value = self._parse_response(user_message, current_field)
        
        if parsed_value.get('valid'):
            # Store value and move to next field
            collected = session.collected_data
            collected[current_field['id']] = parsed_value['value']
            session.collected_data = collected
            session.fields_completed.append(current_field['id'])
            session.current_field_index = current_index + 1
            session.save()
            
            # Generate response for next field
            if current_index + 1 < len(fields):
                next_field = fields[current_index + 1]
                response = self._generate_field_prompt(next_field, config, session)
                field_info = next_field
            else:
                response = self._generate_completion_summary(session)
                field_info = None
        else:
            # Ask for clarification
            session.clarification_count += 1
            session.save()
            
            response = self._generate_clarification(current_field, parsed_value.get('error'), config)
            field_info = current_field
        
        # Save assistant message
        self._save_message(session, 'assistant', response)
        
        progress = (session.current_field_index / len(fields)) * 100
        
        return {
            'session_id': session_id,
            'message': response,
            'current_field': field_info,
            'collected_data': session.collected_data,
            'progress': progress,
            'is_complete': session.current_field_index >= len(fields),
        }
    
    def _generate_welcome_message(self, form, config, language: str) -> str:
        """Generate personalized welcome message"""
        if config.welcome_message:
            return config.welcome_message
        
        fields = form.schema_json.get('fields', [])
        first_field = fields[0] if fields else None
        
        greeting = f"Hi! I'm {config.assistant_name}. I'll help you complete the {form.title} form."
        
        if first_field:
            greeting += f"\n\nLet's start with: **{first_field.get('label', 'the first question')}**"
            if first_field.get('help'):
                greeting += f"\n_{first_field['help']}_"
        
        return greeting
    
    def _generate_field_prompt(self, field: Dict, config, session) -> str:
        """Generate prompt for a specific field"""
        prompt_parts = [f"Great! Now, {field.get('label', 'please answer')}"]
        
        if field.get('type') == 'select':
            options = field.get('options', [])
            prompt_parts.append(f"\nOptions: {', '.join(options)}")
        
        if field.get('help'):
            prompt_parts.append(f"\n_{field['help']}_")
        
        if not field.get('required'):
            prompt_parts.append("\n(You can skip this by saying 'skip')")
        
        return ''.join(prompt_parts)
    
    def _generate_clarification(self, field: Dict, error: str, config) -> str:
        """Generate clarification request"""
        base = f"I didn't quite catch that for '{field.get('label')}'."
        
        if error:
            base += f" {error}"
        
        if field.get('type') == 'email':
            base += " Please provide a valid email address."
        elif field.get('type') == 'phone':
            base += " Please provide a valid phone number."
        elif field.get('type') == 'select':
            options = field.get('options', [])
            base += f" Please choose from: {', '.join(options)}"
        
        base += "\n\nCould you try again?"
        return base
    
    def _generate_completion_summary(self, session) -> str:
        """Generate form completion summary"""
        data = session.collected_data
        summary = "Wonderful! You've completed all the questions.\n\n"
        summary += "Here's a summary of your responses:\n"
        
        for key, value in data.items():
            summary += f"• **{key}**: {value}\n"
        
        summary += "\nWould you like to submit this form? (Say 'yes' to submit or 'edit' to make changes)"
        return summary
    
    def _complete_conversation(self, session) -> Dict:
        """Complete the conversation and create submission"""
        from forms.models import Submission
        
        session.status = 'completed'
        session.completed_at = timezone.now()
        
        # Create submission
        submission = Submission.objects.create(
            form=session.form,
            payload_json=session.collected_data,
        )
        
        session.submission = submission
        session.save()
        
        return {
            'session_id': str(session.session_id),
            'message': "Thank you! Your form has been submitted successfully.",
            'is_complete': True,
            'submission_id': str(submission.id),
        }
    
    def _parse_response(self, user_message: str, field: Dict) -> Dict[str, Any]:
        """Parse user response based on field type"""
        message = user_message.strip()
        field_type = field.get('type', 'text')
        
        # Handle skip
        if message.lower() in ['skip', 'pass', 'next'] and not field.get('required'):
            return {'valid': True, 'value': None, 'skipped': True}
        
        # Type-specific parsing
        if field_type == 'email':
            import re
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message):
                return {'valid': True, 'value': message}
            return {'valid': False, 'error': 'That doesn\'t look like a valid email.'}
        
        elif field_type == 'phone':
            import re
            cleaned = re.sub(r'[^\d+]', '', message)
            if len(cleaned) >= 10:
                return {'valid': True, 'value': cleaned}
            return {'valid': False, 'error': 'Please provide a complete phone number.'}
        
        elif field_type == 'number':
            try:
                value = float(message.replace(',', ''))
                return {'valid': True, 'value': value}
            except ValueError:
                return {'valid': False, 'error': 'Please provide a number.'}
        
        elif field_type in ['select', 'radio']:
            options = [o.lower() for o in field.get('options', [])]
            if message.lower() in options:
                # Return original case option
                idx = options.index(message.lower())
                return {'valid': True, 'value': field.get('options', [])[idx]}
            return {'valid': False, 'error': f'Please choose from the available options.'}
        
        elif field_type == 'checkbox':
            affirmative = ['yes', 'true', 'yeah', 'yep', 'sure', 'ok', 'okay', '1']
            negative = ['no', 'false', 'nope', 'nah', '0']
            if message.lower() in affirmative:
                return {'valid': True, 'value': True}
            if message.lower() in negative:
                return {'valid': True, 'value': False}
            return {'valid': False, 'error': 'Please answer yes or no.'}
        
        elif field_type == 'date':
            # Try to parse date
            from dateutil import parser
            try:
                parsed = parser.parse(message)
                return {'valid': True, 'value': parsed.strftime('%Y-%m-%d')}
            except:
                return {'valid': False, 'error': 'Please provide a valid date.'}
        
        # Default: accept as text
        if field.get('required') and not message:
            return {'valid': False, 'error': 'This field is required.'}
        
        return {'valid': True, 'value': message}
    
    def _get_first_field(self, form) -> Optional[Dict]:
        """Get the first field of the form"""
        fields = form.schema_json.get('fields', [])
        return fields[0] if fields else None
    
    def _save_message(self, session, role: str, content: str, **kwargs):
        """Save a message to the conversation"""
        from forms.models_emerging_tech import ConversationMessage
        
        session.total_messages += 1
        if role == 'user':
            session.user_messages += 1
        else:
            session.ai_messages += 1
        session.save()
        
        ConversationMessage.objects.create(
            session=session,
            role=role,
            content=content,
            **kwargs,
        )


class PersonalizationService:
    """AI-driven form personalization based on user behavior"""
    
    def __init__(self):
        self.ai_service = EnhancedAIService()
    
    def get_personalized_form(
        self,
        form,
        user_identifier: str = None,
        device_type: str = 'desktop',
        referrer: str = None,
        geolocation: Dict = None,
    ) -> Dict[str, Any]:
        """Get personalized form configuration for a user"""
        from forms.models_emerging_tech import AIPersonalization, UserBehaviorProfile
        
        # Get user profile if exists
        profile = None
        if user_identifier:
            try:
                profile = UserBehaviorProfile.objects.get(user_identifier=user_identifier)
            except UserBehaviorProfile.DoesNotExist:
                pass
        
        # Get active personalizations for this form
        personalizations = AIPersonalization.objects.filter(
            form=form,
            is_active=True,
        ).order_by('priority')
        
        # Build context
        context = {
            'device': device_type,
            'referrer': referrer,
            'geolocation': geolocation,
            'user_segment': profile.segments if profile else [],
            'returning_user': profile is not None,
            'previous_abandonment': profile and profile.forms_abandoned > 0,
            'engagement_score': profile.engagement_score if profile else 0,
        }
        
        # Apply matching personalizations
        applied_adaptations = []
        modified_schema = form.schema_json.copy()
        
        for personalization in personalizations:
            if self._matches_conditions(personalization.trigger_conditions, context):
                adaptation = self._apply_adaptation(
                    modified_schema,
                    personalization.adaptation_type,
                    personalization.adaptation_rules,
                    context,
                )
                if adaptation:
                    applied_adaptations.append({
                        'name': personalization.name,
                        'type': personalization.adaptation_type,
                    })
                    personalization.times_applied += 1
                    personalization.save()
        
        # Use AI for additional personalization if profile exists
        ai_recommendations = []
        if profile and profile.engagement_score > 0:
            ai_recommendations = self._get_ai_recommendations(form, profile, context)
        
        return {
            'schema': modified_schema,
            'personalizations_applied': applied_adaptations,
            'ai_recommendations': ai_recommendations,
            'user_context': {
                'returning': profile is not None,
                'engagement_level': self._get_engagement_level(profile),
            },
        }
    
    def _matches_conditions(self, conditions: Dict, context: Dict) -> bool:
        """Check if context matches trigger conditions"""
        if not conditions:
            return True
        
        for key, expected in conditions.items():
            actual = context.get(key)
            
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif isinstance(expected, bool):
                if bool(actual) != expected:
                    return False
            elif expected != actual:
                return False
        
        return True
    
    def _apply_adaptation(
        self,
        schema: Dict,
        adaptation_type: str,
        rules: Dict,
        context: Dict,
    ) -> bool:
        """Apply an adaptation to the schema"""
        try:
            if adaptation_type == 'field_order':
                # Reorder fields based on rules
                new_order = rules.get('order', [])
                if new_order:
                    fields = schema.get('fields', [])
                    field_map = {f['id']: f for f in fields}
                    reordered = [field_map[fid] for fid in new_order if fid in field_map]
                    remaining = [f for f in fields if f['id'] not in new_order]
                    schema['fields'] = reordered + remaining
                    return True
            
            elif adaptation_type == 'field_visibility':
                # Show/hide fields
                hide = rules.get('hide', [])
                show = rules.get('show', [])
                for field in schema.get('fields', []):
                    if field['id'] in hide:
                        field['hidden'] = True
                    elif field['id'] in show:
                        field['hidden'] = False
                return bool(hide or show)
            
            elif adaptation_type == 'default_values':
                # Set default values
                defaults = rules.get('defaults', {})
                for field in schema.get('fields', []):
                    if field['id'] in defaults:
                        field['defaultValue'] = defaults[field['id']]
                return bool(defaults)
            
            elif adaptation_type == 'ui_complexity':
                # Adjust UI complexity
                level = rules.get('level', 'normal')
                settings = schema.setdefault('settings', {})
                settings['uiComplexity'] = level
                return True
            
        except Exception:
            pass
        
        return False
    
    def _get_engagement_level(self, profile) -> str:
        """Determine user engagement level"""
        if not profile:
            return 'new'
        
        if profile.engagement_score > 70:
            return 'high'
        elif profile.engagement_score > 40:
            return 'medium'
        else:
            return 'low'
    
    def _get_ai_recommendations(
        self,
        form,
        profile,
        context: Dict,
    ) -> List[Dict]:
        """Get AI-powered recommendations for the user"""
        if not self.ai_service.get_available_providers():
            return []
        
        prompt = f"""Based on this user profile, suggest personalization for the form:

User Profile:
- Forms completed: {profile.forms_completed}
- Forms abandoned: {profile.forms_abandoned}
- Engagement score: {profile.engagement_score}
- Preferred device: {profile.preferred_device}
- Average completion time: {profile.avg_completion_time}s

Form: {form.title}
Field count: {len(form.schema_json.get('fields', []))}
Device: {context.get('device')}

Suggest 2-3 specific adaptations to improve this user's experience. Return JSON:
[{{"type": "...", "description": "...", "expected_impact": "..."}}]
"""
        
        response = self.ai_service.generate_completion(
            prompt=prompt,
            system_prompt="You are a UX personalization expert. Provide actionable recommendations.",
            max_tokens=500,
        )
        
        if response.get('content'):
            try:
                content = response['content']
                start = content.find('[')
                end = content.rfind(']') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
            except:
                pass
        
        return []
