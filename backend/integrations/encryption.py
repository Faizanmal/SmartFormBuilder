"""
Encryption utilities for sensitive data storage
"""
from cryptography.fernet import Fernet
from django.conf import settings
import base64


def get_encryption_key():
    """Get or create encryption key from settings"""
    key = getattr(settings, 'ENCRYPTION_KEY', None)
    if not key:
        # Generate a key if not in settings (for development only)
        # In production, this should be in environment variables
        key = Fernet.generate_key()
        settings.ENCRYPTION_KEY = key
    
    if isinstance(key, str):
        key = key.encode()
    
    return key


def encrypt_data(plaintext: str) -> str:
    """Encrypt string data"""
    if not plaintext:
        return plaintext
    
    key = get_encryption_key()
    f = Fernet(key)
    
    encrypted = f.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(ciphertext: str) -> str:
    """Decrypt string data"""
    if not ciphertext:
        return ciphertext
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        
        decoded = base64.urlsafe_b64decode(ciphertext.encode())
        decrypted = f.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        # Log error but don't expose encryption details
        print(f"Decryption error: {e}")
        return None


def encrypt_dict(data: dict) -> dict:
    """Encrypt sensitive fields in a dictionary"""
    import json
    if not data:
        return data
    
    json_str = json.dumps(data)
    return {'encrypted': encrypt_data(json_str)}


def decrypt_dict(data: dict) -> dict:
    """Decrypt dictionary from encrypted storage"""
    import json
    if not data or 'encrypted' not in data:
        return data
    
    decrypted_str = decrypt_data(data['encrypted'])
    if decrypted_str:
        return json.loads(decrypted_str)
    return {}
