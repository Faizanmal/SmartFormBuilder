"""
Export utilities for form submissions
"""
import csv
import json
from io import StringIO, BytesIO
from typing import List, Dict, Any
from datetime import datetime


class SubmissionExporter:
    """Export form submissions to various formats"""
    
    @staticmethod
    def to_csv(submissions: List[Dict[str, Any]], field_names: List[str] = None) -> str:
        """
        Export submissions to CSV format
        
        Args:
            submissions: List of submission dictionaries
            field_names: Optional list of field names to include
            
        Returns:
            CSV string
        """
        if not submissions:
            return ""
        
        output = StringIO()
        
        # Determine all unique field keys
        all_keys = set()
        for submission in submissions:
            payload = submission.get('payload_json', {})
            all_keys.update(payload.keys())
        
        # Filter to specified field names if provided
        if field_names:
            all_keys = [k for k in all_keys if k in field_names]
        else:
            all_keys = sorted(all_keys)
        
        # Add metadata columns
        columns = ['submission_id', 'submitted_at', 'ip_address'] + list(all_keys)
        
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        
        for submission in submissions:
            row = {
                'submission_id': str(submission.get('id', '')),
                'submitted_at': submission.get('created_at', ''),
                'ip_address': submission.get('ip_address', ''),
            }
            
            # Add payload fields
            payload = submission.get('payload_json', {})
            for key in all_keys:
                value = payload.get(key, '')
                # Convert lists to comma-separated strings
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                row[key] = value
            
            writer.writerow(row)
        
        return output.getvalue()
    
    @staticmethod
    def to_json(submissions: List[Dict[str, Any]]) -> str:
        """
        Export submissions to JSON format
        
        Args:
            submissions: List of submission dictionaries
            
        Returns:
            JSON string
        """
        # Convert datetime objects to ISO format strings
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        return json.dumps(submissions, indent=2, default=serialize_datetime)
    
    @staticmethod
    def to_xlsx(submissions: List[Dict[str, Any]], field_names: List[str] = None) -> bytes:
        """
        Export submissions to Excel XLSX format
        
        Args:
            submissions: List of submission dictionaries
            field_names: Optional list of field names to include
            
        Returns:
            XLSX file bytes
        """
        try:
            import openpyxl
            from openpyxl import Workbook
        except ImportError:
            raise ImportError("openpyxl is required for XLSX export. Install with: pip install openpyxl")
        
        if not submissions:
            return b""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Submissions"
        
        # Determine all unique field keys
        all_keys = set()
        for submission in submissions:
            payload = submission.get('payload_json', {})
            all_keys.update(payload.keys())
        
        # Filter to specified field names if provided
        if field_names:
            all_keys = [k for k in all_keys if k in field_names]
        else:
            all_keys = sorted(all_keys)
        
        # Headers
        headers = ['Submission ID', 'Submitted At', 'IP Address'] + list(all_keys)
        ws.append(headers)
        
        # Data rows
        for submission in submissions:
            row = [
                str(submission.get('id', '')),
                str(submission.get('created_at', '')),
                submission.get('ip_address', ''),
            ]
            
            payload = submission.get('payload_json', {})
            for key in all_keys:
                value = payload.get(key, '')
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                row.append(value)
            
            ws.append(row)
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def flatten_submission(submission) -> Dict[str, Any]:
        """
        Flatten a Submission model instance to a dictionary
        
        Args:
            submission: Submission model instance
            
        Returns:
            Flattened dictionary
        """
        return {
            'id': submission.id,
            'form_id': submission.form_id,
            'payload_json': submission.payload_json,
            'ip_address': submission.ip_address,
            'user_agent': submission.user_agent,
            'payment_status': submission.payment_status,
            'payment_id': submission.payment_id,
            'payment_amount': submission.payment_amount,
            'created_at': submission.created_at,
            'processed_at': submission.processed_at,
        }
