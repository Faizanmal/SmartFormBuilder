"""
Voice input service for accessibility and convenience
"""
import base64
from openai import OpenAI
from django.conf import settings


class VoiceInputService:
    """Service for handling voice input in forms"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def transcribe_audio(self, audio_data, audio_format='webm'):
        """
        Transcribe audio to text using OpenAI Whisper
        
        Args:
            audio_data: Base64 encoded audio or file object
            audio_format: Audio format (webm, mp3, wav, etc.)
            
        Returns:
            Transcribed text
        """
        try:
            # If base64 encoded, decode it
            if isinstance(audio_data, str):
                # Remove data URL prefix if present
                if audio_data.startswith('data:audio'):
                    audio_data = audio_data.split(',')[1]
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data
            
            # Save temporarily (Whisper API needs a file)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Transcribe using Whisper
            with open(temp_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Can be made dynamic
                )
            
            # Cleanup temp file
            import os
            os.unlink(temp_file_path)
            
            return transcript.text.strip()
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Voice transcription failed: {e}")
            raise ValueError(f"Failed to transcribe audio: {str(e)}")
    
    def text_to_speech(self, text, voice='alloy'):
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Base64 encoded audio
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Convert response to base64
            audio_content = response.content
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            return f"data:audio/mpeg;base64,{audio_base64}"
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Text-to-speech failed: {e}")
            return None
    
    def validate_voice_input(self, transcribed_text, field_type, expected_format=None):
        """
        Validate transcribed voice input against field requirements
        
        Args:
            transcribed_text: The transcribed text
            field_type: Type of field
            expected_format: Expected format (if any)
            
        Returns:
            Validated and formatted value
        """
        # Import the conversational service for parsing
        from .conversational_service import ConversationalFormService
        
        conv_service = ConversationalFormService()
        return conv_service.parse_user_response(transcribed_text, field_type)
    
    def enable_voice_commands(self, audio_data):
        """
        Recognize voice commands for form navigation
        
        Commands: next, back, submit, cancel, repeat, help
        
        Returns:
            Recognized command
        """
        transcribed = self.transcribe_audio(audio_data)
        transcribed_lower = transcribed.lower().strip()
        
        commands = {
            'next': ['next', 'continue', 'go on', 'move forward'],
            'back': ['back', 'previous', 'go back'],
            'submit': ['submit', 'send', 'finish', 'done'],
            'cancel': ['cancel', 'stop', 'quit', 'exit'],
            'repeat': ['repeat', 'say again', 'what', 'pardon'],
            'help': ['help', 'assist', 'support']
        }
        
        for command, keywords in commands.items():
            if any(keyword in transcribed_lower for keyword in keywords):
                return {
                    'command': command,
                    'original_text': transcribed
                }
        
        # Not a command, treat as input
        return {
            'command': 'input',
            'text': transcribed
        }
