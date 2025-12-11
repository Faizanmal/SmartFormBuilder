"""
Voice-Activated Form Design and Editing Service
Allow users to create and edit forms using voice commands
"""
import json
import re
from typing import Dict, Any, List, Optional
from django.conf import settings
from openai import OpenAI
import base64


class VoiceDesignService:
    """
    Service for voice-activated form design and editing.
    Uses OpenAI Whisper for transcription and GPT for intent understanding.
    """
    
    # Voice command patterns
    COMMAND_PATTERNS = {
        'create_form': [
            r'create (?:a )?(?:new )?form (?:called |named |for )?(.+)',
            r'make (?:a )?(?:new )?form (?:called |named |for )?(.+)',
            r'start (?:a )?(?:new )?form (?:called |named |for )?(.+)',
        ],
        'add_field': [
            r'add (?:a )?(?:an )?(\w+) field (?:called |named |for )?(.+)',
            r'add (?:a )?(?:an )?(\w+) (?:called |named |for )?(.+)',
            r'create (?:a )?(?:an )?(\w+) field (?:called |named |for )?(.+)',
        ],
        'remove_field': [
            r'remove (?:the )?(.+) field',
            r'delete (?:the )?(.+) field',
            r'get rid of (?:the )?(.+) field',
        ],
        'make_required': [
            r'make (?:the )?(.+) (?:field )?required',
            r'require (?:the )?(.+)',
            r'(.+) (?:field )?(?:should be |is )required',
        ],
        'make_optional': [
            r'make (?:the )?(.+) (?:field )?optional',
            r'(.+) (?:field )?(?:should be |is )optional',
        ],
        'reorder_field': [
            r'move (?:the )?(.+) (?:field )?(before|after|to position) (.+)',
            r'put (?:the )?(.+) (?:field )?(before|after) (.+)',
        ],
        'update_label': [
            r'(?:rename|change) (?:the )?(.+) (?:field )?(?:label )?to (.+)',
            r'(?:call|name) (?:the )?(.+) (?:field )?(.+)',
        ],
        'add_options': [
            r'add options? (.+) to (?:the )?(.+) field',
            r'(?:the )?(.+) field (?:should have |has )options? (.+)',
        ],
        'add_validation': [
            r'(?:add|set) validation (?:for |on )?(?:the )?(.+) (?:field )?(?:to )?(.+)',
            r'(?:the )?(.+) (?:field )?(?:should|must) (.+)',
        ],
        'save_form': [
            r'save (?:the )?form',
            r'publish (?:the )?form',
            r"i'?m done",
            r'finish',
        ],
        'undo': [
            r'undo',
            r'undo (?:the )?last (?:change|action)',
            r'go back',
            r'revert',
        ],
        'describe_form': [
            r'describe (?:the )?form',
            r'what (?:does )?(?:the )?form (?:look like|have)',
            r'list (?:the )?fields',
            r'show (?:me )?(?:the )?form',
        ],
    }
    
    # Field type mappings from natural language
    FIELD_TYPE_MAPPING = {
        'text': ['text', 'string', 'input', 'short answer'],
        'email': ['email', 'e-mail', 'email address'],
        'phone': ['phone', 'telephone', 'phone number', 'mobile'],
        'number': ['number', 'numeric', 'integer', 'amount'],
        'textarea': ['textarea', 'long text', 'paragraph', 'description', 'comments', 'message'],
        'date': ['date', 'birthday', 'appointment date'],
        'time': ['time', 'appointment time'],
        'select': ['select', 'dropdown', 'choice', 'pick one'],
        'radio': ['radio', 'single choice', 'one of'],
        'checkbox': ['checkbox', 'check', 'agree', 'multiple choice', 'check box'],
        'file': ['file', 'upload', 'attachment', 'document'],
        'url': ['url', 'website', 'link'],
        'payment': ['payment', 'credit card', 'pay'],
    }
    
    def __init__(self):
        self.client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
        self.command_history = []
    
    def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: str = 'webm',
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using OpenAI Whisper
        
        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (webm, mp3, wav, etc.)
            
        Returns:
            Transcription result with text and confidence
        """
        import tempfile
        import os
        
        try:
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(
                suffix=f'.{audio_format}', 
                delete=False
            ) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Transcribe with Whisper
            with open(temp_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return {
                'success': True,
                'text': response.text,
                'language': response.language,
                'duration': response.duration,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def process_voice_command(
        self,
        text: str,
        current_schema: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Process a voice command and return the action to take
        
        Args:
            text: Transcribed voice command
            current_schema: Current form schema (if editing)
            
        Returns:
            Action to take with updated schema
        """
        text = text.lower().strip()
        
        # Try pattern matching first
        for command_type, patterns in self.COMMAND_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return self._execute_command(
                        command_type, 
                        match.groups(), 
                        current_schema
                    )
        
        # Fall back to AI interpretation
        return self._interpret_with_ai(text, current_schema)
    
    def _execute_command(
        self,
        command_type: str,
        args: tuple,
        schema: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Execute a parsed voice command"""
        
        if schema is None:
            schema = {'title': 'New Form', 'fields': []}
        
        schema = schema.copy()
        
        if command_type == 'create_form':
            form_name = args[0] if args else 'New Form'
            return {
                'action': 'create_form',
                'success': True,
                'schema': {
                    'title': form_name.title(),
                    'description': '',
                    'fields': [],
                },
                'message': f'Created new form: {form_name.title()}',
            }
        
        elif command_type == 'add_field':
            field_type_text = args[0] if len(args) > 0 else 'text'
            field_name = args[1] if len(args) > 1 else 'New Field'
            
            field_type = self._parse_field_type(field_type_text)
            field_id = f'f_{len(schema.get("fields", [])) + 1}'
            
            new_field = {
                'id': field_id,
                'type': field_type,
                'label': field_name.title(),
                'required': False,
            }
            
            # Add options for select/radio
            if field_type in ['select', 'radio']:
                new_field['options'] = ['Option 1', 'Option 2', 'Option 3']
            
            schema.setdefault('fields', []).append(new_field)
            
            return {
                'action': 'add_field',
                'success': True,
                'schema': schema,
                'field': new_field,
                'message': f'Added {field_type} field: {field_name.title()}',
            }
        
        elif command_type == 'remove_field':
            field_name = args[0] if args else ''
            field_idx = self._find_field_by_name(schema, field_name)
            
            if field_idx is not None:
                removed_field = schema['fields'].pop(field_idx)
                return {
                    'action': 'remove_field',
                    'success': True,
                    'schema': schema,
                    'removed_field': removed_field,
                    'message': f'Removed field: {removed_field.get("label")}',
                }
            else:
                return {
                    'action': 'remove_field',
                    'success': False,
                    'schema': schema,
                    'message': f'Could not find field: {field_name}',
                }
        
        elif command_type == 'make_required':
            field_name = args[0] if args else ''
            field_idx = self._find_field_by_name(schema, field_name)
            
            if field_idx is not None:
                schema['fields'][field_idx]['required'] = True
                return {
                    'action': 'make_required',
                    'success': True,
                    'schema': schema,
                    'message': f'Made {schema["fields"][field_idx]["label"]} required',
                }
            else:
                return {
                    'action': 'make_required',
                    'success': False,
                    'schema': schema,
                    'message': f'Could not find field: {field_name}',
                }
        
        elif command_type == 'make_optional':
            field_name = args[0] if args else ''
            field_idx = self._find_field_by_name(schema, field_name)
            
            if field_idx is not None:
                schema['fields'][field_idx]['required'] = False
                return {
                    'action': 'make_optional',
                    'success': True,
                    'schema': schema,
                    'message': f'Made {schema["fields"][field_idx]["label"]} optional',
                }
            else:
                return {
                    'action': 'make_optional',
                    'success': False,
                    'schema': schema,
                    'message': f'Could not find field: {field_name}',
                }
        
        elif command_type == 'reorder_field':
            field_name = args[0] if len(args) > 0 else ''
            position = args[1] if len(args) > 1 else ''
            target = args[2] if len(args) > 2 else ''
            
            field_idx = self._find_field_by_name(schema, field_name)
            
            if field_idx is not None:
                field = schema['fields'].pop(field_idx)
                
                if position == 'before':
                    target_idx = self._find_field_by_name(schema, target)
                    if target_idx is not None:
                        schema['fields'].insert(target_idx, field)
                elif position == 'after':
                    target_idx = self._find_field_by_name(schema, target)
                    if target_idx is not None:
                        schema['fields'].insert(target_idx + 1, field)
                elif 'position' in position:
                    try:
                        new_pos = int(target) - 1
                        schema['fields'].insert(new_pos, field)
                    except:
                        schema['fields'].append(field)
                else:
                    schema['fields'].append(field)
                
                return {
                    'action': 'reorder_field',
                    'success': True,
                    'schema': schema,
                    'message': f'Moved {field["label"]} {position} {target}',
                }
            else:
                return {
                    'action': 'reorder_field',
                    'success': False,
                    'schema': schema,
                    'message': f'Could not find field: {field_name}',
                }
        
        elif command_type == 'update_label':
            old_name = args[0] if len(args) > 0 else ''
            new_name = args[1] if len(args) > 1 else ''
            
            field_idx = self._find_field_by_name(schema, old_name)
            
            if field_idx is not None:
                old_label = schema['fields'][field_idx]['label']
                schema['fields'][field_idx]['label'] = new_name.title()
                return {
                    'action': 'update_label',
                    'success': True,
                    'schema': schema,
                    'message': f'Renamed "{old_label}" to "{new_name.title()}"',
                }
            else:
                return {
                    'action': 'update_label',
                    'success': False,
                    'schema': schema,
                    'message': f'Could not find field: {old_name}',
                }
        
        elif command_type == 'add_options':
            options_text = args[0] if len(args) > 0 else ''
            field_name = args[1] if len(args) > 1 else ''
            
            field_idx = self._find_field_by_name(schema, field_name)
            
            if field_idx is not None:
                # Parse options (comma or "and" separated)
                options = re.split(r',\s*|\s+and\s+|\s+or\s+', options_text)
                options = [o.strip().title() for o in options if o.strip()]
                
                schema['fields'][field_idx]['options'] = options
                return {
                    'action': 'add_options',
                    'success': True,
                    'schema': schema,
                    'message': f'Set options for {schema["fields"][field_idx]["label"]}: {", ".join(options)}',
                }
            else:
                return {
                    'action': 'add_options',
                    'success': False,
                    'schema': schema,
                    'message': f'Could not find field: {field_name}',
                }
        
        elif command_type == 'describe_form':
            fields_desc = []
            for i, field in enumerate(schema.get('fields', []), 1):
                required = ' (required)' if field.get('required') else ''
                fields_desc.append(f"{i}. {field.get('label')} - {field.get('type')}{required}")
            
            description = f"Form: {schema.get('title', 'Untitled')}\n"
            description += f"Fields ({len(schema.get('fields', []))}):\n"
            description += '\n'.join(fields_desc) if fields_desc else 'No fields yet'
            
            return {
                'action': 'describe_form',
                'success': True,
                'schema': schema,
                'message': description,
            }
        
        elif command_type == 'save_form':
            return {
                'action': 'save_form',
                'success': True,
                'schema': schema,
                'message': 'Form saved successfully',
            }
        
        elif command_type == 'undo':
            # This would be handled at the session level
            return {
                'action': 'undo',
                'success': True,
                'schema': schema,
                'message': 'Undo last action',
            }
        
        return {
            'action': 'unknown',
            'success': False,
            'schema': schema,
            'message': 'Command not recognized',
        }
    
    def _interpret_with_ai(
        self,
        text: str,
        current_schema: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Use AI to interpret complex voice commands"""
        
        if current_schema is None:
            current_schema = {'title': 'New Form', 'fields': []}
        
        prompt = f"""You are a form builder assistant. Interpret this voice command and return a JSON response.

Current form schema:
{json.dumps(current_schema, indent=2)}

Voice command: "{text}"

Return JSON with this structure:
{{
    "action": "create_form|add_field|remove_field|update_field|reorder_field|save_form|describe_form|unknown",
    "success": true/false,
    "schema": {{updated schema}},
    "message": "Confirmation message to speak back",
    "field": {{new/updated field if applicable}}
}}

For add_field:
- Infer field type from context
- Generate appropriate field ID
- Set sensible defaults

For unknown commands:
- Set success to false
- Suggest what the user might mean

Return only valid JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a form builder assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                'action': 'error',
                'success': False,
                'schema': current_schema,
                'message': f'Error interpreting command: {str(e)}',
            }
    
    def _parse_field_type(self, text: str) -> str:
        """Parse field type from natural language"""
        text = text.lower().strip()
        
        for field_type, keywords in self.FIELD_TYPE_MAPPING.items():
            if any(kw in text for kw in keywords):
                return field_type
        
        return 'text'  # Default to text
    
    def _find_field_by_name(
        self, 
        schema: Dict, 
        name: str
    ) -> Optional[int]:
        """Find field index by name (fuzzy match)"""
        name = name.lower().strip()
        
        for i, field in enumerate(schema.get('fields', [])):
            label = field.get('label', '').lower()
            field_id = field.get('id', '').lower()
            
            # Exact match
            if label == name or field_id == name:
                return i
            
            # Partial match
            if name in label or name in field_id:
                return i
        
        return None
    
    def generate_form_from_description(
        self,
        description: str,
    ) -> Dict[str, Any]:
        """Generate complete form schema from voice description"""
        
        prompt = f"""Create a form schema from this description:

"{description}"

Return JSON with this structure:
{{
    "title": "Form title",
    "description": "Form description",
    "fields": [
        {{
            "id": "f_1",
            "type": "text|email|phone|textarea|number|date|select|radio|checkbox|file",
            "label": "Field label",
            "placeholder": "Placeholder text",
            "required": true/false,
            "help": "Help text",
            "options": ["option1", "option2"] // for select/radio
        }}
    ],
    "settings": {{
        "consent_text": "Consent text for GDPR",
        "redirect": "/thank-you"
    }}
}}

Make intelligent choices about:
- Field types based on context
- Which fields should be required
- Helpful placeholders and help text
- Logical field ordering

Return only valid JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert form designer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            schema = json.loads(response.choices[0].message.content)
            
            return {
                'success': True,
                'schema': schema,
                'message': f'Created form: {schema.get("title")} with {len(schema.get("fields", []))} fields',
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error generating form: {str(e)}',
            }
    
    def text_to_speech(self, text: str, voice: str = 'nova') -> bytes:
        """Convert text response to speech"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,  # alloy, echo, fable, onyx, nova, shimmer
                input=text,
            )
            
            return response.content
            
        except Exception as e:
            raise Exception(f"TTS error: {str(e)}")
    
    def start_voice_session(self) -> Dict[str, Any]:
        """Start a new voice design session"""
        return {
            'session_id': str(hash(str(datetime.now()))),
            'schema': {
                'title': 'New Form',
                'description': '',
                'fields': [],
            },
            'history': [],
            'message': "Voice design session started. Say 'create a form called...' to begin.",
        }
    
    def process_session_command(
        self,
        session: Dict[str, Any],
        audio_data: bytes = None,
        text: str = None,
    ) -> Dict[str, Any]:
        """Process a command in a voice session"""
        
        # Transcribe if audio provided
        if audio_data:
            transcription = self.transcribe_audio(audio_data)
            if not transcription['success']:
                return {
                    'session': session,
                    'error': transcription['error'],
                }
            text = transcription['text']
        
        if not text:
            return {
                'session': session,
                'error': 'No command provided',
            }
        
        # Store current schema in history for undo
        session['history'].append(session['schema'].copy())
        
        # Process command
        result = self.process_voice_command(text, session['schema'])
        
        # Handle undo
        if result['action'] == 'undo' and session['history']:
            session['schema'] = session['history'].pop()
            result['schema'] = session['schema']
            result['message'] = 'Undid last action'
        else:
            session['schema'] = result['schema']
        
        # Generate audio response
        audio_response = None
        try:
            audio_response = self.text_to_speech(result['message'])
        except:
            pass
        
        return {
            'session': session,
            'result': result,
            'transcription': text,
            'audio_response': base64.b64encode(audio_response).decode() if audio_response else None,
        }


class VoiceCommandHistory:
    """Track voice command history for a session"""
    
    def __init__(self, max_history: int = 50):
        self.commands = []
        self.max_history = max_history
    
    def add(self, command: str, result: Dict):
        """Add command to history"""
        self.commands.append({
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'result': result,
        })
        
        # Trim history
        if len(self.commands) > self.max_history:
            self.commands = self.commands[-self.max_history:]
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get recent commands"""
        return self.commands[-count:]
    
    def undo(self) -> Optional[Dict]:
        """Get last command for undo"""
        if self.commands:
            return self.commands.pop()
        return None
