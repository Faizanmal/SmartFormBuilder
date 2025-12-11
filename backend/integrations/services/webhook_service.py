"""
Webhook service for delivering form submissions to external URLs
"""
import hmac
import hashlib
import json
import requests
from typing import Dict, Any


class WebhookService:
    """Service for handling webhook deliveries"""
    
    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def deliver_webhook(
        url: str,
        payload: Dict[str, Any],
        secret: str,
        timeout: int = 30
    ) -> tuple[int, str]:
        """
        Deliver webhook to external URL with HMAC signature
        
        Args:
            url: Webhook URL
            payload: Data to send
            secret: Secret key for HMAC
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (status_code, response_body)
        """
        payload_str = json.dumps(payload, default=str)
        signature = f"sha256={WebhookService.generate_signature(payload_str, secret)}"
        
        headers = {
            'Content-Type': 'application/json',
            'X-FF-Signature': signature,
            'User-Agent': 'FormForge-Webhook/1.0'
        }
        
        try:
            response = requests.post(
                url,
                data=payload_str,
                headers=headers,
                timeout=timeout
            )
            return response.status_code, response.text
            
        except requests.exceptions.Timeout:
            return 0, "Request timeout"
        except requests.exceptions.RequestException as e:
            return 0, str(e)
    
    @staticmethod
    def prepare_submission_payload(submission, form) -> Dict[str, Any]:
        """Prepare submission data for webhook delivery"""
        return {
            "form_id": str(form.id),
            "form_slug": form.slug,
            "form_title": form.title,
            "submission_id": str(submission.id),
            "payload": submission.payload_json,
            "created_at": submission.created_at.isoformat(),
            "ip_address": submission.ip_address,
        }
