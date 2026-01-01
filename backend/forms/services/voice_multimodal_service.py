"""
Voice and Multimodal Input Service

Features:
- Voice-to-text transcription (Whisper, Google, Azure, AWS)
- OCR/document scanning
- QR/barcode scanning
- AR form preview
- NFC tap-to-fill
- AI alt-text generation
"""
import json
import base64
import hashlib
from typing import Dict, Any, List
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class VoiceTranscriptionService:
    """Multi-engine voice transcription service"""
    
    def __init__(self):
        self.engines = {}
        self._init_engines()
    
    def _init_engines(self):
        """Initialize available transcription engines"""
        # OpenAI Whisper
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        if openai_key and openai_key != 'your-openai-api-key':
            self.engines['whisper'] = {'type': 'openai', 'key': openai_key}
        
        # Google Speech-to-Text
        google_creds = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None)
        if google_creds:
            self.engines['google'] = {'type': 'google', 'credentials': google_creds}
        
        # Azure Speech
        azure_key = getattr(settings, 'AZURE_SPEECH_KEY', None)
        azure_region = getattr(settings, 'AZURE_SPEECH_REGION', None)
        if azure_key and azure_region:
            self.engines['azure'] = {'type': 'azure', 'key': azure_key, 'region': azure_region}
        
        # AWS Transcribe
        aws_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        if aws_key:
            self.engines['aws'] = {'type': 'aws'}
    
    def get_available_engines(self) -> List[str]:
        """Get list of available transcription engines"""
        return list(self.engines.keys())
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        engine: str = 'whisper',
        language: str = None,
        format: str = 'webm',
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Raw audio bytes
            engine: Transcription engine to use
            language: ISO language code (e.g., 'en', 'es')
            format: Audio format (webm, wav, mp3, etc.)
        
        Returns:
            Dict with transcription, confidence, and metadata
        """
        if engine not in self.engines:
            # Fallback to available engine
            if self.engines:
                engine = list(self.engines.keys())[0]
            else:
                return {'error': 'No transcription engine available', 'text': None}
        
        try:
            if engine == 'whisper':
                return await self._transcribe_whisper(audio_data, language, format)
            elif engine == 'google':
                return await self._transcribe_google(audio_data, language, format)
            elif engine == 'azure':
                return await self._transcribe_azure(audio_data, language, format)
            elif engine == 'aws':
                return await self._transcribe_aws(audio_data, language, format)
        except Exception as e:
            logger.error(f"Transcription error with {engine}: {str(e)}")
            return {'error': str(e), 'text': None}
    
    async def _transcribe_whisper(
        self,
        audio_data: bytes,
        language: str,
        format: str,
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper"""
        from openai import OpenAI
        import tempfile
        import os
        
        client = OpenAI(api_key=self.engines['whisper']['key'])
        
        # Write audio to temp file
        suffix = f'.{format}' if format else '.webm'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as audio_file:
                params = {'file': audio_file, 'model': 'whisper-1'}
                if language:
                    params['language'] = language
                
                transcript = client.audio.transcriptions.create(**params)
            
            return {
                'text': transcript.text,
                'engine': 'whisper',
                'language': language,
                'confidence': 0.95,  # Whisper doesn't return confidence
                'duration': None,
            }
        finally:
            os.unlink(temp_path)
    
    async def _transcribe_google(
        self,
        audio_data: bytes,
        language: str,
        format: str,
    ) -> Dict[str, Any]:
        """Transcribe using Google Cloud Speech-to-Text"""
        from google.cloud import speech
        
        client = speech.SpeechClient()
        
        # Configure audio
        audio = speech.RecognitionAudio(content=audio_data)
        
        # Map format to encoding
        encoding_map = {
            'webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            'wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            'flac': speech.RecognitionConfig.AudioEncoding.FLAC,
        }
        
        config = speech.RecognitionConfig(
            encoding=encoding_map.get(format, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS),
            language_code=language or 'en-US',
            enable_automatic_punctuation=True,
        )
        
        response = client.recognize(config=config, audio=audio)
        
        if response.results:
            result = response.results[0]
            alternative = result.alternatives[0]
            return {
                'text': alternative.transcript,
                'engine': 'google',
                'language': language,
                'confidence': alternative.confidence,
                'duration': None,
            }
        
        return {'text': '', 'engine': 'google', 'confidence': 0}
    
    async def _transcribe_azure(
        self,
        audio_data: bytes,
        language: str,
        format: str,
    ) -> Dict[str, Any]:
        """Transcribe using Azure Speech Services"""
        import azure.cognitiveservices.speech as speechsdk
        import tempfile
        import os
        
        config = self.engines['azure']
        
        speech_config = speechsdk.SpeechConfig(
            subscription=config['key'],
            region=config['region']
        )
        
        if language:
            speech_config.speech_recognition_language = language
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            audio_input = speechsdk.AudioConfig(filename=temp_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_input
            )
            
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    'text': result.text,
                    'engine': 'azure',
                    'language': language,
                    'confidence': 0.9,
                    'duration': result.duration,
                }
            else:
                return {'text': '', 'engine': 'azure', 'error': str(result.reason)}
        finally:
            os.unlink(temp_path)
    
    async def _transcribe_aws(
        self,
        audio_data: bytes,
        language: str,
        format: str,
    ) -> Dict[str, Any]:
        """Transcribe using AWS Transcribe"""
        import boto3
        import time
        
        # Upload to S3 first
        s3 = boto3.client('s3')
        transcribe = boto3.client('transcribe')
        
        bucket = getattr(settings, 'AWS_TRANSCRIBE_BUCKET', 'transcribe-temp')
        key = f"audio/{hashlib.md5(audio_data).hexdigest()}.{format}"
        
        s3.put_object(Bucket=bucket, Key=key, Body=audio_data)
        
        job_name = f"transcribe-{int(time.time())}"
        
        try:
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f"s3://{bucket}/{key}"},
                MediaFormat=format,
                LanguageCode=language or 'en-US',
            )
            
            # Poll for completion
            while True:
                status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status == 'COMPLETED':
                    # Get transcript
                    import urllib.request
                    uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    with urllib.request.urlopen(uri) as response:
                        transcript_data = json.loads(response.read())
                        text = transcript_data['results']['transcripts'][0]['transcript']
                    
                    return {
                        'text': text,
                        'engine': 'aws',
                        'language': language,
                        'confidence': 0.9,
                    }
                elif job_status == 'FAILED':
                    return {'text': '', 'engine': 'aws', 'error': 'Transcription failed'}
                
                time.sleep(1)
        finally:
            # Cleanup
            s3.delete_object(Bucket=bucket, Key=key)
            try:
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            except:
                pass
    
    def log_voice_interaction(
        self,
        form,
        field_id: str,
        audio_duration: float,
        transcription: str,
        engine: str,
        confidence: float,
        user_accepted: bool = True,
    ):
        """Log a voice interaction for analytics"""
        from forms.models_voice_multimodal import VoiceInteraction
        
        VoiceInteraction.objects.create(
            form=form,
            field_id=field_id,
            audio_duration=audio_duration,
            transcription_text=transcription,
            transcription_engine=engine,
            confidence_score=confidence,
            user_accepted=user_accepted,
        )


class OCRService:
    """Document scanning and OCR service"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize OCR providers"""
        # Google Cloud Vision
        google_creds = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None)
        if google_creds:
            self.providers['google_vision'] = {'type': 'google'}
        
        # Azure Computer Vision
        azure_key = getattr(settings, 'AZURE_VISION_KEY', None)
        if azure_key:
            self.providers['azure'] = {
                'type': 'azure',
                'key': azure_key,
                'endpoint': getattr(settings, 'AZURE_VISION_ENDPOINT', ''),
            }
        
        # AWS Textract
        aws_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        if aws_key:
            self.providers['aws_textract'] = {'type': 'aws'}
    
    def extract_text_from_image(
        self,
        image_data: bytes,
        provider: str = None,
        document_type: str = 'general',
    ) -> Dict[str, Any]:
        """
        Extract text from an image
        
        Args:
            image_data: Raw image bytes
            provider: OCR provider to use
            document_type: Type of document (general, id_card, passport, form)
        
        Returns:
            Dict with extracted text and structured data
        """
        if not provider:
            provider = list(self.providers.keys())[0] if self.providers else None
        
        if not provider:
            return {'error': 'No OCR provider available'}
        
        try:
            if provider == 'google_vision':
                return self._extract_google_vision(image_data, document_type)
            elif provider == 'azure':
                return self._extract_azure(image_data, document_type)
            elif provider == 'aws_textract':
                return self._extract_aws(image_data, document_type)
        except Exception as e:
            logger.error(f"OCR error with {provider}: {str(e)}")
            return {'error': str(e)}
    
    def _extract_google_vision(
        self,
        image_data: bytes,
        document_type: str,
    ) -> Dict[str, Any]:
        """Extract text using Google Cloud Vision"""
        from google.cloud import vision
        
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_data)
        
        if document_type in ['id_card', 'passport', 'form']:
            # Use document text detection for better accuracy
            response = client.document_text_detection(image=image)
            full_text = response.full_text_annotation
            
            # Extract structured data
            blocks = []
            for page in full_text.pages:
                for block in page.blocks:
                    block_text = ''
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            block_text += ''.join([s.text for s in word.symbols]) + ' '
                    blocks.append({
                        'text': block_text.strip(),
                        'confidence': block.confidence,
                        'bounding_box': [(v.x, v.y) for v in block.bounding_box.vertices],
                    })
            
            return {
                'raw_text': full_text.text,
                'blocks': blocks,
                'provider': 'google_vision',
                'document_type': document_type,
            }
        else:
            # Use simple text detection
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                return {
                    'raw_text': texts[0].description,
                    'blocks': [{'text': t.description} for t in texts[1:]],
                    'provider': 'google_vision',
                }
        
        return {'raw_text': '', 'blocks': [], 'provider': 'google_vision'}
    
    def _extract_azure(
        self,
        image_data: bytes,
        document_type: str,
    ) -> Dict[str, Any]:
        """Extract text using Azure Computer Vision"""
        from azure.cognitiveservices.vision.computervision import ComputerVisionClient
        from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
        from msrest.authentication import CognitiveServicesCredentials
        import io
        import time
        
        config = self.providers['azure']
        client = ComputerVisionClient(
            config['endpoint'],
            CognitiveServicesCredentials(config['key'])
        )
        
        # Start read operation
        read_response = client.read_in_stream(io.BytesIO(image_data), raw=True)
        operation_location = read_response.headers['Operation-Location']
        operation_id = operation_location.split('/')[-1]
        
        # Poll for results
        while True:
            result = client.get_read_result(operation_id)
            if result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(0.5)
        
        if result.status == OperationStatusCodes.succeeded:
            lines = []
            for page in result.analyze_result.read_results:
                for line in page.lines:
                    lines.append({
                        'text': line.text,
                        'confidence': line.confidence if hasattr(line, 'confidence') else None,
                        'bounding_box': line.bounding_box,
                    })
            
            full_text = '\n'.join([l['text'] for l in lines])
            return {
                'raw_text': full_text,
                'blocks': lines,
                'provider': 'azure',
            }
        
        return {'raw_text': '', 'blocks': [], 'provider': 'azure', 'error': str(result.status)}
    
    def _extract_aws(
        self,
        image_data: bytes,
        document_type: str,
    ) -> Dict[str, Any]:
        """Extract text using AWS Textract"""
        import boto3
        
        client = boto3.client('textract')
        
        if document_type in ['id_card', 'form']:
            # Use analyze_document for forms and IDs
            response = client.analyze_document(
                Document={'Bytes': image_data},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            # Extract key-value pairs
            key_map = {}
            value_map = {}
            block_map = {}
            
            for block in response['Blocks']:
                block_map[block['Id']] = block
                if block['BlockType'] == 'KEY_VALUE_SET':
                    if 'KEY' in block.get('EntityTypes', []):
                        key_map[block['Id']] = block
                    else:
                        value_map[block['Id']] = block
            
            # Build key-value pairs
            kvs = []
            for key_id, key_block in key_map.items():
                key_text = self._get_text_from_block(key_block, block_map)
                value_text = ''
                
                for rel in key_block.get('Relationships', []):
                    if rel['Type'] == 'VALUE':
                        for value_id in rel['Ids']:
                            value_block = value_map.get(value_id, {})
                            value_text = self._get_text_from_block(value_block, block_map)
                
                if key_text:
                    kvs.append({'key': key_text, 'value': value_text})
            
            return {
                'raw_text': '\n'.join([f"{kv['key']}: {kv['value']}" for kv in kvs]),
                'key_value_pairs': kvs,
                'provider': 'aws_textract',
            }
        else:
            # Use simple text detection
            response = client.detect_document_text(Document={'Bytes': image_data})
            
            lines = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    lines.append({
                        'text': block['Text'],
                        'confidence': block['Confidence'],
                    })
            
            return {
                'raw_text': '\n'.join([l['text'] for l in lines]),
                'blocks': lines,
                'provider': 'aws_textract',
            }
    
    def _get_text_from_block(self, block: Dict, block_map: Dict) -> str:
        """Extract text from an AWS Textract block"""
        text = ''
        for rel in block.get('Relationships', []):
            if rel['Type'] == 'CHILD':
                for child_id in rel['Ids']:
                    child = block_map.get(child_id, {})
                    if child.get('BlockType') == 'WORD':
                        text += child.get('Text', '') + ' '
        return text.strip()
    
    def auto_fill_from_document(
        self,
        form,
        extracted_data: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Attempt to auto-fill form fields from extracted document data
        """
        from .enhanced_ai_service import EnhancedAIService
        
        ai = EnhancedAIService()
        
        # Get form fields
        fields = form.schema_json.get('fields', [])
        field_labels = [f.get('label', f.get('id')) for f in fields]
        
        # Use AI to map extracted data to form fields
        prompt = f"""Map this extracted document data to form fields:

Document Text:
{extracted_data.get('raw_text', '')}

Form Fields:
{json.dumps(field_labels, indent=2)}

Return a JSON object mapping field labels to extracted values:
{{"field_label": "extracted_value", ...}}

Only include fields where you have high confidence in the extracted value.
"""
        
        response = ai.generate_completion(
            prompt=prompt,
            system_prompt="You are a document parsing expert. Extract accurate data and map to form fields.",
            max_tokens=1000,
        )
        
        if response.get('content'):
            try:
                content = response['content']
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
            except json.JSONDecodeError:
                pass
        
        return {}


class QRBarcodeService:
    """QR code and barcode scanning service"""
    
    def decode_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Decode QR codes and barcodes from an image
        
        Returns:
            Dict with decoded data and format
        """
        try:
            from pyzbar import pyzbar
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_data))
            decoded = pyzbar.decode(image)
            
            results = []
            for obj in decoded:
                results.append({
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type,
                    'rect': {
                        'left': obj.rect.left,
                        'top': obj.rect.top,
                        'width': obj.rect.width,
                        'height': obj.rect.height,
                    },
                })
            
            return {
                'success': len(results) > 0,
                'results': results,
                'count': len(results),
            }
        except ImportError:
            # Fallback to browser-based decoding indicator
            return {
                'success': False,
                'error': 'Server-side QR/barcode scanning not available. Use client-side scanning.',
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def parse_qr_data(self, qr_data: str, expected_format: str = None) -> Dict[str, Any]:
        """
        Parse QR code data into structured format
        
        Args:
            qr_data: Raw QR code string
            expected_format: Expected format (vcard, url, wifi, etc.)
        
        Returns:
            Parsed data dictionary
        """
        # URL
        if qr_data.startswith(('http://', 'https://')):
            return {'type': 'url', 'url': qr_data}
        
        # vCard
        if qr_data.startswith('BEGIN:VCARD'):
            return self._parse_vcard(qr_data)
        
        # WiFi
        if qr_data.startswith('WIFI:'):
            return self._parse_wifi(qr_data)
        
        # Phone
        if qr_data.startswith('tel:'):
            return {'type': 'phone', 'number': qr_data[4:]}
        
        # Email
        if qr_data.startswith('mailto:'):
            return {'type': 'email', 'address': qr_data[7:].split('?')[0]}
        
        # SMS
        if qr_data.startswith('sms:'):
            return {'type': 'sms', 'number': qr_data[4:].split('?')[0]}
        
        # JSON data
        try:
            return {'type': 'json', 'data': json.loads(qr_data)}
        except json.JSONDecodeError:
            pass
        
        # Plain text
        return {'type': 'text', 'text': qr_data}
    
    def _parse_vcard(self, vcard: str) -> Dict[str, Any]:
        """Parse vCard format"""
        data = {'type': 'vcard'}
        lines = vcard.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.split(';')[0].upper()
                
                if key == 'FN':
                    data['full_name'] = value.strip()
                elif key == 'N':
                    parts = value.split(';')
                    if len(parts) >= 2:
                        data['last_name'] = parts[0].strip()
                        data['first_name'] = parts[1].strip()
                elif key == 'TEL':
                    data['phone'] = value.strip()
                elif key == 'EMAIL':
                    data['email'] = value.strip()
                elif key == 'ORG':
                    data['organization'] = value.strip()
                elif key == 'TITLE':
                    data['title'] = value.strip()
                elif key == 'ADR':
                    data['address'] = value.replace(';', ', ').strip()
        
        return data
    
    def _parse_wifi(self, wifi: str) -> Dict[str, Any]:
        """Parse WiFi QR format"""
        data = {'type': 'wifi'}
        content = wifi[5:]  # Remove 'WIFI:'
        
        parts = content.split(';')
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                if key == 'S':
                    data['ssid'] = value
                elif key == 'P':
                    data['password'] = value
                elif key == 'T':
                    data['security'] = value
                elif key == 'H':
                    data['hidden'] = value.lower() == 'true'
        
        return data


class NFCService:
    """NFC tap-to-fill service"""
    
    def encode_form_data(self, data: Dict[str, Any]) -> bytes:
        """
        Encode form data for NFC tag
        
        Args:
            data: Form field data to encode
        
        Returns:
            Encoded bytes for NFC tag
        """
        # Create NDEF message
        import ndef
        
        # Encode as JSON
        json_data = json.dumps(data, separators=(',', ':'))
        
        # Create NDEF record
        record = ndef.TextRecord(json_data)
        return b''.join(ndef.message_encoder([record]))
    
    def decode_nfc_data(self, raw_data: bytes) -> Dict[str, Any]:
        """
        Decode NFC tag data
        
        Args:
            raw_data: Raw bytes from NFC tag
        
        Returns:
            Decoded form data
        """
        try:
            import ndef
            
            records = list(ndef.message_decoder(raw_data))
            
            for record in records:
                if isinstance(record, ndef.TextRecord):
                    try:
                        return {'type': 'form_data', 'data': json.loads(record.text)}
                    except json.JSONDecodeError:
                        return {'type': 'text', 'text': record.text}
                elif isinstance(record, ndef.UriRecord):
                    return {'type': 'url', 'url': record.uri}
            
            return {'type': 'unknown', 'raw': raw_data.hex()}
        except ImportError:
            return {'error': 'NDEF library not available'}
        except Exception as e:
            return {'error': str(e)}


class AIAltTextService:
    """AI-powered alt text generation for accessibility"""
    
    def __init__(self):
        from .enhanced_ai_service import EnhancedAIService
        self.ai_service = EnhancedAIService()
    
    def generate_alt_text(
        self,
        image_data: bytes,
        context: str = None,
        max_length: int = 125,
    ) -> Dict[str, Any]:
        """
        Generate accessible alt text for an image
        
        Args:
            image_data: Raw image bytes
            context: Additional context about the image
            max_length: Maximum alt text length
        
        Returns:
            Dict with alt text and confidence
        """
        providers = self.ai_service.get_available_providers()
        
        if 'openai' in providers:
            return self._generate_openai(image_data, context, max_length)
        elif 'anthropic' in providers:
            return self._generate_anthropic(image_data, context, max_length)
        elif 'google' in providers:
            return self._generate_google(image_data, context, max_length)
        
        return {'error': 'No AI provider available for image analysis'}
    
    def _generate_openai(
        self,
        image_data: bytes,
        context: str,
        max_length: int,
    ) -> Dict[str, Any]:
        """Generate alt text using OpenAI GPT-4 Vision"""
        from openai import OpenAI
        
        client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Generate a concise, accessible alt text for this image.
The alt text should be descriptive but under {max_length} characters.
Focus on the most important visual information.
{"Context: " + context if context else ""}
Return only the alt text, no additional explanation."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=100,
        )
        
        alt_text = response.choices[0].message.content.strip()
        
        # Truncate if needed
        if len(alt_text) > max_length:
            alt_text = alt_text[:max_length-3] + '...'
        
        return {
            'alt_text': alt_text,
            'provider': 'openai',
            'confidence': 0.9,
            'character_count': len(alt_text),
        }
    
    def _generate_anthropic(
        self,
        image_data: bytes,
        context: str,
        max_length: int,
    ) -> Dict[str, Any]:
        """Generate alt text using Claude"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=getattr(settings, 'ANTHROPIC_API_KEY', ''))
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"""Generate accessible alt text under {max_length} characters.
{"Context: " + context if context else ""}
Return only the alt text."""
                        }
                    ],
                }
            ],
        )
        
        alt_text = message.content[0].text.strip()
        
        if len(alt_text) > max_length:
            alt_text = alt_text[:max_length-3] + '...'
        
        return {
            'alt_text': alt_text,
            'provider': 'anthropic',
            'confidence': 0.9,
            'character_count': len(alt_text),
        }
    
    def _generate_google(
        self,
        image_data: bytes,
        context: str,
        max_length: int,
    ) -> Dict[str, Any]:
        """Generate alt text using Google Cloud Vision + Gemini"""
        from google.cloud import vision
        
        # First, get image description from Vision API
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_data)
        
        response = client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations[:5]]
        
        response = client.object_localization(image=image)
        objects = [obj.name for obj in response.localized_object_annotations[:5]]
        
        # Combine into alt text
        elements = list(set(labels + objects))
        
        if len(elements) == 0:
            return {'alt_text': 'Image', 'provider': 'google', 'confidence': 0.5}
        
        if len(elements) == 1:
            alt_text = elements[0]
        else:
            alt_text = ', '.join(elements[:-1]) + ' and ' + elements[-1]
        
        # Add context if provided
        if context:
            alt_text = f"{alt_text} - {context}"
        
        if len(alt_text) > max_length:
            alt_text = alt_text[:max_length-3] + '...'
        
        return {
            'alt_text': alt_text,
            'provider': 'google',
            'confidence': 0.85,
            'character_count': len(alt_text),
        }


class ARPreviewService:
    """Augmented Reality form preview service"""
    
    def generate_ar_config(
        self,
        form,
        environment_type: str = 'desktop',
    ) -> Dict[str, Any]:
        """
        Generate AR configuration for form preview
        
        Args:
            form: Form to preview
            environment_type: Target environment (desktop, mobile, headset)
        
        Returns:
            AR configuration for client-side rendering
        """
        from forms.models_voice_multimodal import ARPreviewConfig
        
        config, _ = ARPreviewConfig.objects.get_or_create(
            form=form,
            defaults={
                'is_enabled': True,
                'environment_type': environment_type,
            }
        )
        
        # Generate 3D layout based on form schema
        fields = form.schema_json.get('fields', [])
        
        ar_layout = {
            'form_id': str(form.id),
            'title': form.title,
            'panels': self._generate_ar_panels(fields),
            'environment': {
                'type': environment_type,
                'lighting': 'natural',
                'background': config.background_settings,
            },
            'interaction': {
                'pointer_type': 'gaze' if environment_type == 'headset' else 'touch',
                'haptic_feedback': environment_type == 'mobile',
            },
        }
        
        return ar_layout
    
    def _generate_ar_panels(self, fields: List[Dict]) -> List[Dict]:
        """Generate AR panel layout for fields"""
        panels = []
        current_y = 0
        
        for i, field in enumerate(fields):
            panel = {
                'id': field.get('id', f'field_{i}'),
                'type': field.get('type', 'text'),
                'label': field.get('label', ''),
                'position': {
                    'x': 0,
                    'y': current_y,
                    'z': 0,
                },
                'size': self._get_panel_size(field),
                'material': {
                    'color': '#ffffff',
                    'opacity': 0.95,
                    'border_radius': 8,
                },
            }
            
            current_y -= panel['size']['height'] + 0.02  # 2cm gap
            panels.append(panel)
        
        return panels
    
    def _get_panel_size(self, field: Dict) -> Dict[str, float]:
        """Get panel size based on field type"""
        field_type = field.get('type', 'text')
        
        sizes = {
            'text': {'width': 0.3, 'height': 0.06},
            'textarea': {'width': 0.3, 'height': 0.15},
            'select': {'width': 0.3, 'height': 0.06},
            'checkbox': {'width': 0.3, 'height': 0.04},
            'radio': {'width': 0.3, 'height': 0.08},
            'date': {'width': 0.3, 'height': 0.06},
            'file': {'width': 0.3, 'height': 0.1},
        }
        
        return sizes.get(field_type, {'width': 0.3, 'height': 0.06})
