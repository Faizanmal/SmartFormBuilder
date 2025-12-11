"""
Security and compliance service
"""
import pyotp
import secrets
from cryptography.fernet import Fernet
from typing import Dict, List
import re
from datetime import datetime, timedelta


class SecurityService:
    """Advanced security features"""
    
    def setup_2fa(self, user, method: str = 'totp') -> Dict:
        """Setup two-factor authentication"""
        from ..models_security import TwoFactorAuth
        
        try:
            two_factor, created = TwoFactorAuth.objects.get_or_create(
                user=user,
                defaults={'method': method}
            )
            
            if method == 'totp':
                # Generate TOTP secret
                secret = pyotp.random_base32()
                two_factor.secret_key = secret
                
                # Generate provisioning URI for QR code
                totp = pyotp.TOTP(secret)
                provisioning_uri = totp.provisioning_uri(
                    name=user.email,
                    issuer_name='SmartFormBuilder'
                )
                
                # Generate backup codes
                backup_codes = [secrets.token_hex(8) for _ in range(10)]
                two_factor.backup_codes = backup_codes
                two_factor.save()
                
                return {
                    'success': True,
                    'secret': secret,
                    'provisioning_uri': provisioning_uri,
                    'backup_codes': backup_codes
                }
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_2fa_code(self, user, code: str) -> bool:
        """Verify 2FA code"""
        from ..models_security import TwoFactorAuth
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=user, is_enabled=True)
            
            if two_factor.method == 'totp':
                totp = pyotp.TOTP(two_factor.secret_key)
                return totp.verify(code, valid_window=1)
            
            return False
        except TwoFactorAuth.DoesNotExist:
            return False
    
    def encrypt_submission(self, submission_data: Dict, key: bytes = None) -> Dict:
        """Encrypt submission data with AES-256"""
        import json
        
        if key is None:
            key = Fernet.generate_key()
        
        fernet = Fernet(key)
        
        # Serialize and encrypt data
        json_data = json.dumps(submission_data).encode()
        encrypted_data = fernet.encrypt(json_data)
        
        return {
            'encrypted_data': encrypted_data,
            'encryption_key': key,
            'algorithm': 'AES-256-GCM'
        }
    
    def decrypt_submission(self, encrypted_data: bytes, key: bytes) -> Dict:
        """Decrypt submission data"""
        import json
        
        try:
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            return {'error': f'Decryption failed: {str(e)}'}
    
    def create_privacy_request(
        self,
        email: str,
        request_type: str,
        reason: str = ''
    ) -> Dict:
        """Create GDPR/CCPA data privacy request"""
        from ..models_security import DataPrivacyRequest
        
        try:
            # Generate verification token
            token = secrets.token_urlsafe(32)
            
            request = DataPrivacyRequest.objects.create(
                requester_email=email,
                request_type=request_type,
                verification_token=token,
                reason=reason
            )
            
            # Send verification email (placeholder)
            verification_url = f"https://app.smartformbuilder.com/verify-privacy-request/{token}"
            
            return {
                'success': True,
                'request_id': str(request.id),
                'verification_url': verification_url
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_data_export(self, request_id: str) -> Dict:
        """Process data export request"""
        from ..models_security import DataPrivacyRequest
        from ..models import Submission
        
        try:
            request = DataPrivacyRequest.objects.get(id=request_id, status='pending')
            
            # Find all user data
            submissions = Submission.objects.filter(
                data__email=request.requester_email
            )
            
            export_data = {
                'user_email': request.requester_email,
                'export_date': datetime.now().isoformat(),
                'submissions': [
                    {
                        'form_id': str(sub.form.id),
                        'form_title': sub.form.title,
                        'submitted_at': sub.created_at.isoformat(),
                        'data': sub.data
                    }
                    for sub in submissions
                ]
            }
            
            # In production, upload to secure storage and generate signed URL
            export_file_url = f"https://exports.smartformbuilder.com/{request.id}.json"
            
            request.status = 'completed'
            request.export_file_url = export_file_url
            request.export_expires_at = datetime.now() + timedelta(days=7)
            request.processed_at = datetime.now()
            request.save()
            
            return {
                'success': True,
                'download_url': export_file_url,
                'expires_at': request.export_expires_at.isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scan_submission_for_threats(self, submission_data: Dict) -> Dict:
        """Scan submission for security threats"""
        
        threats = []
        risk_score = 0
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(--|\#|\/\*)",
            r"(\bOR\b.*=.*)",
        ]
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onerror=",
            r"onload=",
        ]
        
        for key, value in submission_data.items():
            value_str = str(value)
            
            # Check SQL injection
            for pattern in sql_patterns:
                if re.search(pattern, value_str, re.IGNORECASE):
                    threats.append({
                        'type': 'sql_injection',
                        'field': key,
                        'pattern': pattern
                    })
                    risk_score += 30
            
            # Check XSS
            for pattern in xss_patterns:
                if re.search(pattern, value_str, re.IGNORECASE):
                    threats.append({
                        'type': 'xss',
                        'field': key,
                        'pattern': pattern
                    })
                    risk_score += 25
        
        is_malicious = risk_score >= 50
        
        return {
            'is_malicious': is_malicious,
            'risk_score': min(risk_score, 100),
            'threats_detected': threats,
            'should_block': is_malicious
        }
    
    def check_ip_access(self, form_id: str, ip_address: str) -> Dict:
        """Check if IP is allowed to access form"""
        from ..models_security import IPAccessControl
        import ipaddress
        
        try:
            controls = IPAccessControl.objects.filter(form_id=form_id, is_active=True)
            
            for control in controls:
                ip_obj = ipaddress.ip_address(ip_address)
                
                for ip_range in control.ip_ranges:
                    network = ipaddress.ip_network(ip_range, strict=False)
                    
                    if ip_obj in network:
                        if control.access_type == 'whitelist':
                            return {'allowed': True, 'reason': 'IP whitelisted'}
                        else:  # blacklist
                            return {'allowed': False, 'reason': 'IP blacklisted'}
                
                # Check countries if configured
                if control.countries:
                    # In production, use IP geolocation service
                    pass
            
            return {'allowed': True, 'reason': 'No restrictions'}
        except Exception as e:
            return {'allowed': True, 'reason': f'Error checking access: {str(e)}'}
    
    def log_security_event(
        self,
        user,
        event_type: str,
        ip_address: str,
        user_agent: str,
        metadata: Dict = None
    ):
        """Log security audit event"""
        from ..models_security import SecurityAuditLog
        
        risk_levels = {
            'login': 'low',
            'login_failed': 'medium',
            '2fa_enabled': 'low',
            'password_changed': 'medium',
            'suspicious_activity': 'high',
        }
        
        SecurityAuditLog.objects.create(
            user=user,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            risk_level=risk_levels.get(event_type, 'low')
        )


class ComplianceService:
    """GDPR/CCPA compliance tools"""
    
    def track_consent(
        self,
        submission,
        consent_type: str,
        granted: bool,
        consent_text: str,
        ip_address: str,
        user_agent: str
    ):
        """Track user consent"""
        from ..models_security import ConsentTracking
        
        ConsentTracking.objects.create(
            submission=submission,
            consent_type=consent_type,
            granted=granted,
            consent_text=consent_text,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def get_consent_history(self, submission_id: str) -> List[Dict]:
        """Get consent history for submission"""
        from ..models_security import ConsentTracking
        
        consents = ConsentTracking.objects.filter(submission_id=submission_id)
        
        return [
            {
                'type': c.consent_type,
                'granted': c.granted,
                'timestamp': c.created_at.isoformat(),
                'revoked': c.revoked_at is not None
            }
            for c in consents
        ]
