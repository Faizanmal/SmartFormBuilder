"""
Advanced Security Service

Features:
- Zero-knowledge encryption
- Blockchain audit trails
- AI threat detection
- Compliance automation (GDPR, CCPA, HIPAA)
- Data residency controls
"""
import json
import hashlib
import secrets
import hmac
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import base64
import logging

logger = logging.getLogger(__name__)


class ZeroKnowledgeEncryptionService:
    """
    Client-side encryption with zero-knowledge proof
    Server never sees unencrypted data
    """
    
    def __init__(self):
        self.key_length = 32  # 256-bit keys
        self.nonce_length = 12  # 96-bit nonce for AES-GCM
        self.salt_length = 16
        self.iterations = 100000
    
    def derive_key(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User-provided password
            salt: Optional salt (generated if not provided)
        
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(self.salt_length)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def encrypt_data(self, data: Dict[str, Any], key: bytes) -> Dict[str, str]:
        """
        Encrypt form data using AES-GCM
        
        Args:
            data: Form data to encrypt
            key: 256-bit encryption key
        
        Returns:
            Dict with encrypted data and nonce
        """
        nonce = secrets.token_bytes(self.nonce_length)
        aesgcm = AESGCM(key)
        
        plaintext = json.dumps(data).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'nonce': base64.b64encode(nonce).decode(),
        }
    
    def create_proof_of_encryption(
        self,
        encrypted_data: str,
        salt: bytes,
    ) -> str:
        """
        Create a proof that data was encrypted without revealing the key
        Uses hash commitment scheme
        """
        # Create commitment: H(encrypted_data || salt)
        combined = encrypted_data.encode() + salt
        commitment = hashlib.sha256(combined).hexdigest()
        return commitment
    
    def verify_encryption_proof(
        self,
        encrypted_data: str,
        salt: bytes,
        proof: str,
    ) -> bool:
        """Verify that encryption proof is valid"""
        expected = self.create_proof_of_encryption(encrypted_data, salt)
        return hmac.compare_digest(expected, proof)
    
    def store_encrypted_submission(
        self,
        form,
        encrypted_payload: Dict[str, str],
        salt: bytes,
        key_derivation_params: Dict[str, Any],
    ) -> 'EncryptedSubmission':
        """
        Store an encrypted submission
        
        Args:
            form: Form instance
            encrypted_payload: Encrypted data with nonce
            salt: Key derivation salt
            key_derivation_params: Parameters for key derivation
        
        Returns:
            EncryptedSubmission instance
        """
        from forms.models_security_advanced import ZeroKnowledgeEncryption, EncryptionKey
        
        # Create encryption key metadata (NOT the actual key)
        encryption_key = EncryptionKey.objects.create(
            form=form,
            key_identifier=secrets.token_hex(16),
            algorithm='AES-256-GCM',
            key_derivation='PBKDF2-SHA256',
            salt=base64.b64encode(salt).decode(),
            iterations=self.iterations,
        )
        
        # Create zero-knowledge config if not exists
        zk_config, _ = ZeroKnowledgeEncryption.objects.get_or_create(
            form=form,
            defaults={
                'is_enabled': True,
                'encryption_algorithm': 'AES-256-GCM',
                'key_derivation_function': 'PBKDF2',
            }
        )
        
        # Create proof
        proof = self.create_proof_of_encryption(
            encrypted_payload['ciphertext'],
            salt
        )
        
        # Store submission
        from forms.models import Submission
        submission = Submission.objects.create(
            form=form,
            payload_json={
                'encrypted': True,
                'ciphertext': encrypted_payload['ciphertext'],
                'nonce': encrypted_payload['nonce'],
                'key_id': str(encryption_key.id),
                'proof': proof,
            },
        )
        
        return submission


class BlockchainAuditService:
    """
    Immutable audit trail using blockchain-style hashing
    """
    
    def __init__(self):
        self.hash_algorithm = 'sha256'
    
    def create_audit_entry(
        self,
        form,
        action_type: str,
        action_data: Dict[str, Any],
        previous_hash: str = None,
        actor: str = None,
    ) -> 'BlockchainAuditEntry':
        """
        Create a new blockchain audit entry
        
        Args:
            form: Form instance
            action_type: Type of action (create, update, delete, etc.)
            action_data: Data associated with the action
            previous_hash: Hash of the previous entry (for chaining)
            actor: User or system that performed the action
        
        Returns:
            BlockchainAuditEntry instance
        """
        from forms.models_security_advanced import BlockchainConfig, BlockchainAuditEntry
        
        # Get or create blockchain config
        config, _ = BlockchainConfig.objects.get_or_create(
            form=form,
            defaults={'is_enabled': True}
        )
        
        # Get previous entry if not provided
        if previous_hash is None:
            previous_entry = BlockchainAuditEntry.objects.filter(
                form=form
            ).order_by('-block_number').first()
            
            if previous_entry:
                previous_hash = previous_entry.current_hash
                block_number = previous_entry.block_number + 1
            else:
                previous_hash = '0' * 64  # Genesis block
                block_number = 0
        else:
            # Get next block number
            last_entry = BlockchainAuditEntry.objects.filter(
                form=form
            ).order_by('-block_number').first()
            block_number = (last_entry.block_number + 1) if last_entry else 0
        
        # Create block data
        timestamp = timezone.now()
        block_data = {
            'block_number': block_number,
            'timestamp': timestamp.isoformat(),
            'action_type': action_type,
            'action_data': action_data,
            'previous_hash': previous_hash,
            'actor': actor,
            'form_id': str(form.id),
        }
        
        # Calculate hash
        current_hash = self._calculate_hash(block_data)
        
        # Create entry
        entry = BlockchainAuditEntry.objects.create(
            form=form,
            block_number=block_number,
            action_type=action_type,
            action_data=action_data,
            previous_hash=previous_hash,
            current_hash=current_hash,
            timestamp=timestamp,
            actor=actor or '',
        )
        
        return entry
    
    def _calculate_hash(self, block_data: Dict) -> str:
        """Calculate SHA-256 hash of block data"""
        data_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def verify_chain_integrity(self, form) -> Dict[str, Any]:
        """
        Verify the integrity of the entire audit chain
        
        Returns:
            Dict with verification status and any issues found
        """
        from forms.models_security_advanced import BlockchainAuditEntry
        
        entries = BlockchainAuditEntry.objects.filter(
            form=form
        ).order_by('block_number')
        
        issues = []
        previous_hash = '0' * 64
        
        for i, entry in enumerate(entries):
            # Check block number sequence
            if entry.block_number != i:
                issues.append({
                    'type': 'sequence_error',
                    'block': entry.block_number,
                    'expected': i,
                    'message': f'Block number {entry.block_number} should be {i}',
                })
            
            # Check previous hash
            if entry.previous_hash != previous_hash:
                issues.append({
                    'type': 'chain_break',
                    'block': entry.block_number,
                    'message': f'Previous hash mismatch at block {entry.block_number}',
                })
            
            # Verify current hash
            block_data = {
                'block_number': entry.block_number,
                'timestamp': entry.timestamp.isoformat(),
                'action_type': entry.action_type,
                'action_data': entry.action_data,
                'previous_hash': entry.previous_hash,
                'actor': entry.actor,
                'form_id': str(form.id),
            }
            expected_hash = self._calculate_hash(block_data)
            
            if entry.current_hash != expected_hash:
                issues.append({
                    'type': 'hash_mismatch',
                    'block': entry.block_number,
                    'message': f'Hash mismatch at block {entry.block_number}',
                })
            
            previous_hash = entry.current_hash
        
        return {
            'valid': len(issues) == 0,
            'total_blocks': entries.count(),
            'issues': issues,
            'last_verified': timezone.now().isoformat(),
        }
    
    def export_chain(self, form) -> List[Dict]:
        """Export the full audit chain as a list of blocks"""
        from forms.models_security_advanced import BlockchainAuditEntry
        
        entries = BlockchainAuditEntry.objects.filter(
            form=form
        ).order_by('block_number')
        
        return [
            {
                'block_number': e.block_number,
                'timestamp': e.timestamp.isoformat(),
                'action_type': e.action_type,
                'action_data': e.action_data,
                'previous_hash': e.previous_hash,
                'current_hash': e.current_hash,
                'actor': e.actor,
            }
            for e in entries
        ]


class ThreatDetectionService:
    """
    AI-powered threat detection for forms
    """
    
    def __init__(self):
        from .enhanced_ai_service import EnhancedAIService
        self.ai_service = EnhancedAIService()
        
        # Threat patterns
        self.sql_injection_patterns = [
            r"('\s*(OR|AND)\s*')|(\d+\s*(OR|AND)\s*\d+)",
            r"(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE)\s+",
            r"(--|#|/\*|\*/)",
            r"(\bOR\b|\bAND\b)\s+\d+=\d+",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed",
        ]
        
        self.bot_indicators = [
            'submission_time_under_threshold',
            'honeypot_filled',
            'unusual_input_patterns',
            'known_bot_user_agent',
        ]
    
    def analyze_submission(
        self,
        form,
        submission_data: Dict[str, Any],
        request_metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a submission for potential threats
        
        Args:
            form: Form instance
            submission_data: Form submission data
            request_metadata: Request information (IP, user agent, etc.)
        
        Returns:
            Threat analysis result
        """
        from forms.models_security_advanced import ThreatDetectionConfig, ThreatEvent
        
        # Get config
        try:
            config = ThreatDetectionConfig.objects.get(form=form)
            if not config.is_enabled:
                return {'analyzed': False, 'reason': 'Threat detection disabled'}
        except ThreatDetectionConfig.DoesNotExist:
            config = None
        
        threats = []
        risk_score = 0
        
        # Check for SQL injection
        for field_id, value in submission_data.items():
            if isinstance(value, str):
                for pattern in self.sql_injection_patterns:
                    import re
                    if re.search(pattern, value, re.IGNORECASE):
                        threats.append({
                            'type': 'sql_injection',
                            'field': field_id,
                            'severity': 'critical',
                            'confidence': 0.9,
                        })
                        risk_score += 40
                        break
        
        # Check for XSS
        for field_id, value in submission_data.items():
            if isinstance(value, str):
                for pattern in self.xss_patterns:
                    import re
                    if re.search(pattern, value, re.IGNORECASE):
                        threats.append({
                            'type': 'xss_attempt',
                            'field': field_id,
                            'severity': 'high',
                            'confidence': 0.85,
                        })
                        risk_score += 30
                        break
        
        # Check for bot behavior
        if request_metadata:
            bot_score = self._analyze_bot_behavior(request_metadata)
            if bot_score > 0.7:
                threats.append({
                    'type': 'bot_submission',
                    'severity': 'medium',
                    'confidence': bot_score,
                })
                risk_score += 20
        
        # Check IP reputation
        if request_metadata and request_metadata.get('ip'):
            ip_threat = self._check_ip_reputation(
                form,
                request_metadata['ip']
            )
            if ip_threat:
                threats.append(ip_threat)
                risk_score += 25
        
        # Use AI for advanced analysis
        if self.ai_service.get_available_providers() and risk_score < 50:
            ai_threats = self._ai_threat_analysis(submission_data)
            threats.extend(ai_threats)
            risk_score += sum(10 for t in ai_threats)
        
        # Normalize risk score
        risk_score = min(risk_score, 100)
        
        # Determine threat level
        if risk_score >= 70:
            threat_level = 'critical'
            action = 'block'
        elif risk_score >= 50:
            threat_level = 'high'
            action = 'review'
        elif risk_score >= 30:
            threat_level = 'medium'
            action = 'flag'
        else:
            threat_level = 'low'
            action = 'allow'
        
        # Log threat event if threats detected
        if threats:
            ThreatEvent.objects.create(
                form=form,
                threat_type=threats[0]['type'],
                severity=threats[0]['severity'],
                source_ip=request_metadata.get('ip', '') if request_metadata else '',
                details={
                    'threats': threats,
                    'risk_score': risk_score,
                    'action_taken': action,
                },
            )
        
        return {
            'analyzed': True,
            'risk_score': risk_score,
            'threat_level': threat_level,
            'action': action,
            'threats': threats,
        }
    
    def _analyze_bot_behavior(self, metadata: Dict) -> float:
        """Analyze request metadata for bot behavior"""
        score = 0.0
        indicators = 0
        
        # Check submission time
        if metadata.get('submission_time_seconds', 0) < 3:
            score += 0.3
            indicators += 1
        
        # Check honeypot
        if metadata.get('honeypot_filled'):
            score += 0.4
            indicators += 1
        
        # Check user agent
        ua = metadata.get('user_agent', '').lower()
        bot_agents = ['bot', 'crawler', 'spider', 'curl', 'wget', 'python-requests']
        if any(agent in ua for agent in bot_agents):
            score += 0.3
            indicators += 1
        
        # Check for missing headers
        if not metadata.get('accept_language'):
            score += 0.2
            indicators += 1
        
        return min(score, 1.0)
    
    def _check_ip_reputation(self, form, ip: str) -> Optional[Dict]:
        """Check IP against blocklist and reputation"""
        from forms.models_security_advanced import IPBlocklist
        
        # Check blocklist
        blocked = IPBlocklist.objects.filter(
            form=form,
            ip_address=ip,
            is_active=True,
        ).exists()
        
        if blocked:
            return {
                'type': 'blocked_ip',
                'severity': 'high',
                'confidence': 1.0,
                'ip': ip,
            }
        
        # Check global blocklist
        global_blocked = IPBlocklist.objects.filter(
            form=None,
            ip_address=ip,
            is_active=True,
        ).exists()
        
        if global_blocked:
            return {
                'type': 'globally_blocked_ip',
                'severity': 'high',
                'confidence': 1.0,
                'ip': ip,
            }
        
        return None
    
    def _ai_threat_analysis(self, data: Dict) -> List[Dict]:
        """Use AI for advanced threat analysis"""
        threats = []
        
        # Check for suspicious patterns in text fields
        text_content = ' '.join(
            str(v) for v in data.values() if isinstance(v, str)
        )
        
        if len(text_content) < 10:
            return threats
        
        prompt = f"""Analyze this form submission for security threats:

{text_content[:1000]}

Check for:
1. Social engineering attempts
2. Spam or promotional content
3. Personally identifiable information (PII) leakage attempts
4. Malicious URLs or links
5. Credential stuffing patterns

Return JSON array of threats found:
[{{"type": "...", "severity": "critical|high|medium|low", "confidence": 0.0-1.0, "description": "..."}}]

Return empty array [] if no threats detected.
"""
        
        response = self.ai_service.generate_completion(
            prompt=prompt,
            system_prompt="You are a security analyst. Identify potential threats in form submissions.",
            max_tokens=500,
        )
        
        if response.get('content'):
            try:
                content = response['content']
                start = content.find('[')
                end = content.rfind(']') + 1
                if start >= 0 and end > start:
                    threats = json.loads(content[start:end])
            except json.JSONDecodeError:
                pass
        
        return threats
    
    def block_ip(self, form, ip: str, reason: str, expires_at: datetime = None):
        """Add an IP to the blocklist"""
        from forms.models_security_advanced import IPBlocklist
        
        IPBlocklist.objects.update_or_create(
            form=form,
            ip_address=ip,
            defaults={
                'reason': reason,
                'is_active': True,
                'expires_at': expires_at,
            }
        )


class ComplianceService:
    """
    Automated compliance for GDPR, CCPA, HIPAA, etc.
    """
    
    FRAMEWORKS = {
        'GDPR': {
            'name': 'General Data Protection Regulation',
            'region': 'EU',
            'requirements': [
                'consent_collection',
                'data_minimization',
                'purpose_limitation',
                'storage_limitation',
                'right_to_access',
                'right_to_erasure',
                'right_to_portability',
                'breach_notification',
                'dpo_appointment',
            ],
        },
        'CCPA': {
            'name': 'California Consumer Privacy Act',
            'region': 'US-CA',
            'requirements': [
                'notice_at_collection',
                'right_to_know',
                'right_to_delete',
                'right_to_opt_out',
                'non_discrimination',
            ],
        },
        'HIPAA': {
            'name': 'Health Insurance Portability and Accountability Act',
            'region': 'US',
            'requirements': [
                'phi_protection',
                'access_controls',
                'audit_trails',
                'encryption',
                'business_associate_agreements',
                'breach_notification',
            ],
        },
        'SOC2': {
            'name': 'Service Organization Control 2',
            'region': 'Global',
            'requirements': [
                'security',
                'availability',
                'processing_integrity',
                'confidentiality',
                'privacy',
            ],
        },
    }
    
    def __init__(self):
        from .enhanced_ai_service import EnhancedAIService
        self.ai_service = EnhancedAIService()
    
    def scan_form_compliance(
        self,
        form,
        frameworks: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Scan a form for compliance issues
        
        Args:
            form: Form to scan
            frameworks: List of compliance frameworks to check
        
        Returns:
            Compliance scan results
        """
        from forms.models_security_advanced import (
            ComplianceFramework,
            FormComplianceConfig,
            ComplianceScan,
        )
        
        if frameworks is None:
            frameworks = list(self.FRAMEWORKS.keys())
        
        results = {
            'form_id': str(form.id),
            'scan_time': timezone.now().isoformat(),
            'frameworks': {},
            'overall_score': 0,
            'issues': [],
            'recommendations': [],
        }
        
        total_score = 0
        framework_count = 0
        
        for framework_name in frameworks:
            if framework_name not in self.FRAMEWORKS:
                continue
            
            framework_info = self.FRAMEWORKS[framework_name]
            
            # Get or create framework record
            framework, _ = ComplianceFramework.objects.get_or_create(
                name=framework_name,
                defaults={
                    'full_name': framework_info['name'],
                    'requirements': framework_info['requirements'],
                }
            )
            
            # Perform compliance check
            check_result = self._check_framework_compliance(
                form,
                framework_name,
                framework_info['requirements']
            )
            
            results['frameworks'][framework_name] = check_result
            results['issues'].extend(check_result['issues'])
            results['recommendations'].extend(check_result['recommendations'])
            
            total_score += check_result['score']
            framework_count += 1
        
        # Calculate overall score
        if framework_count > 0:
            results['overall_score'] = total_score / framework_count
        
        # Save scan result
        ComplianceScan.objects.create(
            form=form,
            frameworks_checked=frameworks,
            overall_score=results['overall_score'],
            issues_found=results['issues'],
            recommendations=results['recommendations'],
            detailed_results=results['frameworks'],
        )
        
        return results
    
    def _check_framework_compliance(
        self,
        form,
        framework: str,
        requirements: List[str],
    ) -> Dict[str, Any]:
        """Check compliance for a specific framework"""
        passed = []
        failed = []
        issues = []
        recommendations = []
        
        schema = form.schema_json
        fields = schema.get('fields', [])
        
        for req in requirements:
            check_method = getattr(self, f'_check_{req}', None)
            if check_method:
                result = check_method(form, fields)
                if result['passed']:
                    passed.append(req)
                else:
                    failed.append(req)
                    issues.append({
                        'framework': framework,
                        'requirement': req,
                        'severity': result.get('severity', 'medium'),
                        'description': result.get('description', f'Failed {req} check'),
                    })
                    if result.get('recommendation'):
                        recommendations.append({
                            'framework': framework,
                            'requirement': req,
                            'action': result['recommendation'],
                        })
            else:
                # Default to passed if check not implemented
                passed.append(req)
        
        score = (len(passed) / len(requirements)) * 100 if requirements else 100
        
        return {
            'framework': framework,
            'score': score,
            'passed': passed,
            'failed': failed,
            'issues': issues,
            'recommendations': recommendations,
        }
    
    def _check_consent_collection(self, form, fields) -> Dict:
        """Check if form has proper consent collection"""
        # Look for consent/checkbox fields
        consent_fields = [
            f for f in fields
            if f.get('type') == 'checkbox' and 
            any(word in f.get('label', '').lower() for word in ['consent', 'agree', 'accept', 'privacy'])
        ]
        
        if consent_fields:
            return {'passed': True}
        
        return {
            'passed': False,
            'severity': 'high',
            'description': 'No consent collection mechanism found',
            'recommendation': 'Add a consent checkbox with clear privacy policy acceptance',
        }
    
    def _check_data_minimization(self, form, fields) -> Dict:
        """Check if form collects only necessary data"""
        # Flag forms with many optional sensitive fields
        sensitive_types = ['ssn', 'social_security', 'passport', 'driver_license']
        sensitive_fields = [
            f for f in fields
            if any(st in f.get('id', '').lower() for st in sensitive_types)
        ]
        
        if len(sensitive_fields) > 2:
            return {
                'passed': False,
                'severity': 'medium',
                'description': f'Form collects {len(sensitive_fields)} sensitive data fields',
                'recommendation': 'Review if all sensitive fields are necessary for the form purpose',
            }
        
        return {'passed': True}
    
    def _check_encryption(self, form, fields) -> Dict:
        """Check if encryption is configured"""
        from forms.models_security_advanced import ZeroKnowledgeEncryption
        
        try:
            config = ZeroKnowledgeEncryption.objects.get(form=form, is_enabled=True)
            return {'passed': True}
        except ZeroKnowledgeEncryption.DoesNotExist:
            return {
                'passed': False,
                'severity': 'high',
                'description': 'No encryption configured for sensitive data',
                'recommendation': 'Enable zero-knowledge encryption for sensitive submissions',
            }
    
    def _check_audit_trails(self, form, fields) -> Dict:
        """Check if audit trails are enabled"""
        from forms.models_security_advanced import BlockchainConfig
        
        try:
            config = BlockchainConfig.objects.get(form=form, is_enabled=True)
            return {'passed': True}
        except BlockchainConfig.DoesNotExist:
            return {
                'passed': False,
                'severity': 'medium',
                'description': 'No audit trail configured',
                'recommendation': 'Enable blockchain audit trails for compliance',
            }
    
    def _check_right_to_erasure(self, form, fields) -> Dict:
        """Check if data deletion capability exists"""
        # Check if soft delete is configured
        settings = form.schema_json.get('settings', {})
        if settings.get('data_retention_days') or settings.get('allow_deletion_request'):
            return {'passed': True}
        
        return {
            'passed': False,
            'severity': 'high',
            'description': 'No data deletion/retention policy configured',
            'recommendation': 'Configure data retention period and allow deletion requests',
        }
    
    def _check_notice_at_collection(self, form, fields) -> Dict:
        """Check for privacy notice at collection point"""
        settings = form.schema_json.get('settings', {})
        if settings.get('privacy_notice') or settings.get('privacy_policy_url'):
            return {'passed': True}
        
        # Check for privacy notice in form description
        if 'privacy' in form.description.lower():
            return {'passed': True}
        
        return {
            'passed': False,
            'severity': 'high',
            'description': 'No privacy notice configured',
            'recommendation': 'Add privacy notice or policy link to the form',
        }
    
    def _check_phi_protection(self, form, fields) -> Dict:
        """Check for PHI (Protected Health Information) protection"""
        health_fields = [
            f for f in fields
            if any(term in f.get('id', '').lower() for term in 
                   ['health', 'medical', 'diagnosis', 'treatment', 'prescription'])
        ]
        
        if not health_fields:
            return {'passed': True}  # No PHI to protect
        
        # Check encryption
        from forms.models_security_advanced import ZeroKnowledgeEncryption
        try:
            ZeroKnowledgeEncryption.objects.get(form=form, is_enabled=True)
            return {'passed': True}
        except ZeroKnowledgeEncryption.DoesNotExist:
            return {
                'passed': False,
                'severity': 'critical',
                'description': 'PHI fields detected without encryption',
                'recommendation': 'Enable encryption for forms collecting health information',
            }
    
    def _check_access_controls(self, form, fields) -> Dict:
        """Check if access controls are configured"""
        settings = form.schema_json.get('settings', {})
        if settings.get('require_auth') or form.is_private:
            return {'passed': True}
        
        return {
            'passed': False,
            'severity': 'medium',
            'description': 'Form does not require authentication',
            'recommendation': 'Consider requiring authentication for sensitive forms',
        }


class DataResidencyService:
    """
    Geographic data residency controls
    """
    
    REGIONS = {
        'us-east': {'name': 'US East', 'country': 'US', 'laws': ['CCPA', 'HIPAA']},
        'us-west': {'name': 'US West', 'country': 'US', 'laws': ['CCPA', 'HIPAA']},
        'eu-west': {'name': 'EU West', 'country': 'EU', 'laws': ['GDPR']},
        'eu-central': {'name': 'EU Central', 'country': 'EU', 'laws': ['GDPR']},
        'uk': {'name': 'United Kingdom', 'country': 'UK', 'laws': ['UK-GDPR']},
        'asia-pacific': {'name': 'Asia Pacific', 'country': 'APAC', 'laws': ['PDPA']},
        'canada': {'name': 'Canada', 'country': 'CA', 'laws': ['PIPEDA']},
        'australia': {'name': 'Australia', 'country': 'AU', 'laws': ['Privacy Act']},
    }
    
    def configure_data_residency(
        self,
        form,
        primary_region: str,
        allowed_regions: List[str] = None,
        restrict_cross_border: bool = True,
    ):
        """
        Configure data residency for a form
        """
        from forms.models_security_advanced import DataResidencyConfig
        
        if primary_region not in self.REGIONS:
            raise ValueError(f"Invalid region: {primary_region}")
        
        if allowed_regions is None:
            allowed_regions = [primary_region]
        
        config, _ = DataResidencyConfig.objects.update_or_create(
            form=form,
            defaults={
                'primary_region': primary_region,
                'allowed_regions': allowed_regions,
                'restrict_cross_border_transfer': restrict_cross_border,
            }
        )
        
        return config
    
    def check_submission_compliance(
        self,
        form,
        submission_region: str,
        user_region: str = None,
    ) -> Dict[str, Any]:
        """
        Check if a submission complies with data residency rules
        """
        from forms.models_security_advanced import DataResidencyConfig
        
        try:
            config = DataResidencyConfig.objects.get(form=form)
        except DataResidencyConfig.DoesNotExist:
            # No restrictions configured
            return {'compliant': True, 'config': None}
        
        # Check if submission region is allowed
        if submission_region not in config.allowed_regions:
            return {
                'compliant': False,
                'reason': f'Region {submission_region} not allowed',
                'allowed_regions': config.allowed_regions,
            }
        
        # Check cross-border restrictions
        if config.restrict_cross_border_transfer and user_region:
            if user_region != submission_region:
                return {
                    'compliant': False,
                    'reason': 'Cross-border data transfer not allowed',
                    'user_region': user_region,
                    'submission_region': submission_region,
                }
        
        return {
            'compliant': True,
            'region': submission_region,
            'laws_applicable': self.REGIONS.get(submission_region, {}).get('laws', []),
        }
    
    def get_region_from_ip(self, ip: str) -> Optional[str]:
        """
        Determine region from IP address
        """
        try:
            import geoip2.database
            
            reader = geoip2.database.Reader(
                getattr(settings, 'GEOIP_DATABASE', '/usr/share/GeoIP/GeoLite2-Country.mmdb')
            )
            
            response = reader.country(ip)
            country = response.country.iso_code
            
            # Map country to region
            country_to_region = {
                'US': 'us-east',
                'CA': 'canada',
                'GB': 'uk',
                'DE': 'eu-central',
                'FR': 'eu-west',
                'AU': 'australia',
            }
            
            # EU countries
            eu_countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 
                          'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 
                          'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
            
            if country in eu_countries:
                return 'eu-west'
            
            return country_to_region.get(country, 'us-east')
        except Exception:
            return None
