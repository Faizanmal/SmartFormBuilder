"""
Service for submission bulk actions and batch processing
"""
import logging
from django.utils import timezone
from typing import List, Dict, Any

from forms.models_new_features import BulkAction, BatchProcessingQueue
from forms.models import Submission
from forms.tasks import process_bulk_action_async

logger = logging.getLogger(__name__)


class BulkActionService:
    """Service for handling bulk operations on submissions"""
    
    @classmethod
    def create_bulk_action(cls, form_id: str, user_id: str, action_type: str,
                          submission_ids: List[str] = None,
                          filter_criteria: Dict = None,
                          action_params: Dict = None) -> BulkAction:
        """
        Create a new bulk action
        
        Args:
            form_id: Form ID
            user_id: User initiating the action
            action_type: Type of bulk action
            submission_ids: Specific submission IDs (optional)
            filter_criteria: Query filters for selection (optional)
            action_params: Action-specific parameters
            
        Returns:
            Created BulkAction instance
        """
        action_params = action_params or {}
        
        # Get submissions
        submissions = cls._get_submissions(form_id, submission_ids, filter_criteria)
        submission_ids_list = [str(s.id) for s in submissions]
        
        # Create bulk action
        bulk_action = BulkAction.objects.create(
            form_id=form_id,
            user_id=user_id,
            action_type=action_type,
            submission_ids=submission_ids_list,
            filter_criteria=filter_criteria or {},
            action_params=action_params,
            total_submissions=len(submission_ids_list),
            status='pending'
        )
        
        # Queue items for processing
        for submission in submissions:
            BatchProcessingQueue.objects.create(
                bulk_action=bulk_action,
                submission=submission,
                status='pending'
            )
        
        # Start asynchronous processing
        process_bulk_action_async.delay(str(bulk_action.id))
        
        return bulk_action
    
    @classmethod
    def _get_submissions(cls, form_id: str, submission_ids: List[str] = None,
                        filter_criteria: Dict = None) -> List[Submission]:
        """Get submissions based on IDs or filter criteria"""
        queryset = Submission.objects.filter(form_id=form_id)
        
        if submission_ids:
            queryset = queryset.filter(id__in=submission_ids)
        
        if filter_criteria:
            # Apply filters
            if 'date_from' in filter_criteria:
                queryset = queryset.filter(created_at__gte=filter_criteria['date_from'])
            if 'date_to' in filter_criteria:
                queryset = queryset.filter(created_at__lte=filter_criteria['date_to'])
            if 'payment_status' in filter_criteria:
                queryset = queryset.filter(payment_status=filter_criteria['payment_status'])
        
        return list(queryset)
    
    @classmethod
    def process_bulk_action(cls, bulk_action_id: str):
        """Process a bulk action (called by async task)"""
        try:
            bulk_action = BulkAction.objects.get(id=bulk_action_id)
            bulk_action.status = 'processing'
            bulk_action.started_at = timezone.now()
            bulk_action.save()
            
            # Get pending queue items
            queue_items = BatchProcessingQueue.objects.filter(
                bulk_action=bulk_action,
                status='pending'
            )
            
            for item in queue_items:
                try:
                    item.status = 'processing'
                    item.save()
                    
                    # Execute action based on type
                    if bulk_action.action_type == 'approve':
                        result = cls._approve_submission(item.submission, bulk_action.action_params)
                    elif bulk_action.action_type == 'reject':
                        result = cls._reject_submission(item.submission, bulk_action.action_params)
                    elif bulk_action.action_type == 'delete':
                        result = cls._delete_submission(item.submission)
                    elif bulk_action.action_type == 'tag':
                        result = cls._tag_submission(item.submission, bulk_action.action_params)
                    elif bulk_action.action_type == 'assign':
                        result = cls._assign_submission(item.submission, bulk_action.action_params)
                    elif bulk_action.action_type == 'status_change':
                        result = cls._change_status(item.submission, bulk_action.action_params)
                    elif bulk_action.action_type == 'export':
                        result = cls._export_submission(item.submission, bulk_action.action_params)
                    else:
                        result = {'success': False, 'error': 'Unknown action type'}
                    
                    if result.get('success'):
                        item.status = 'completed'
                        item.result = result
                        bulk_action.successful_submissions += 1
                    else:
                        item.status = 'failed'
                        item.error_message = result.get('error', 'Unknown error')
                        bulk_action.failed_submissions += 1
                    
                    item.processed_at = timezone.now()
                    item.save()
                    
                except Exception as e:
                    logger.error(f"Error processing queue item {item.id}: {str(e)}")
                    item.status = 'failed'
                    item.error_message = str(e)
                    item.save()
                    bulk_action.failed_submissions += 1
                
                bulk_action.processed_submissions += 1
                bulk_action.save()
            
            # Handle export action - combine all exports
            if bulk_action.action_type == 'export':
                cls._finalize_export(bulk_action)
            
            # Mark as completed
            bulk_action.status = 'completed' if bulk_action.failed_submissions == 0 else 'partial'
            bulk_action.completed_at = timezone.now()
            bulk_action.save()
            
        except Exception as e:
            logger.error(f"Error processing bulk action {bulk_action_id}: {str(e)}")
            bulk_action.status = 'failed'
            bulk_action.result_data = {'error': str(e)}
            bulk_action.completed_at = timezone.now()
            bulk_action.save()
    
    @classmethod
    def _approve_submission(cls, submission: Submission, params: Dict) -> Dict:
        """Approve a submission"""
        # Update submission metadata
        if not hasattr(submission, 'metadata_json'):
            submission.metadata_json = {}
        
        submission.metadata_json['approved'] = True
        submission.metadata_json['approved_at'] = timezone.now().isoformat()
        submission.metadata_json['approval_note'] = params.get('note', '')
        submission.save()
        
        return {'success': True}
    
    @classmethod
    def _reject_submission(cls, submission: Submission, params: Dict) -> Dict:
        """Reject a submission"""
        if not hasattr(submission, 'metadata_json'):
            submission.metadata_json = {}
        
        submission.metadata_json['rejected'] = True
        submission.metadata_json['rejected_at'] = timezone.now().isoformat()
        submission.metadata_json['rejection_reason'] = params.get('reason', '')
        submission.save()
        
        return {'success': True}
    
    @classmethod
    def _delete_submission(cls, submission: Submission) -> Dict:
        """Delete a submission"""
        submission.delete()
        return {'success': True}
    
    @classmethod
    def _tag_submission(cls, submission: Submission, params: Dict) -> Dict:
        """Add tags to a submission"""
        if not hasattr(submission, 'metadata_json'):
            submission.metadata_json = {}
        
        if 'tags' not in submission.metadata_json:
            submission.metadata_json['tags'] = []
        
        tags = params.get('tags', [])
        submission.metadata_json['tags'].extend(tags)
        submission.metadata_json['tags'] = list(set(submission.metadata_json['tags']))  # Remove duplicates
        submission.save()
        
        return {'success': True}
    
    @classmethod
    def _assign_submission(cls, submission: Submission, params: Dict) -> Dict:
        """Assign submission to a user"""
        if not hasattr(submission, 'metadata_json'):
            submission.metadata_json = {}
        
        submission.metadata_json['assigned_to'] = params.get('user_id')
        submission.metadata_json['assigned_at'] = timezone.now().isoformat()
        submission.save()
        
        return {'success': True}
    
    @classmethod
    def _change_status(cls, submission: Submission, params: Dict) -> Dict:
        """Change submission status"""
        if not hasattr(submission, 'metadata_json'):
            submission.metadata_json = {}
        
        submission.metadata_json['status'] = params.get('status')
        submission.metadata_json['status_changed_at'] = timezone.now().isoformat()
        submission.save()
        
        return {'success': True}
    
    @classmethod
    def _export_submission(cls, submission: Submission, params: Dict) -> Dict:
        """Export submission data"""
        return {
            'success': True,
            'data': {
                'id': str(submission.id),
                'payload': submission.payload_json,
                'created_at': submission.created_at.isoformat()
            }
        }
    
    @classmethod
    def _finalize_export(cls, bulk_action: BulkAction):
        """Finalize export by combining all exported data"""
        queue_items = BatchProcessingQueue.objects.filter(
            bulk_action=bulk_action,
            status='completed'
        )
        
        format_type = bulk_action.action_params.get('format', 'csv')
        
        if format_type == 'csv':
            file_url = cls._create_csv_export(bulk_action, queue_items)
        elif format_type == 'json':
            file_url = cls._create_json_export(bulk_action, queue_items)
        else:
            file_url = ''
        
        bulk_action.export_file_url = file_url
        bulk_action.save()
    
    @classmethod
    def _create_csv_export(cls, bulk_action: BulkAction, queue_items) -> str:
        """Create CSV export file"""
        # This would generate a CSV file and upload to S3/storage
        # For now, return a placeholder URL
        return f"/exports/bulk_action_{bulk_action.id}.csv"
    
    @classmethod
    def _create_json_export(cls, bulk_action: BulkAction, queue_items) -> str:
        """Create JSON export file"""
        return f"/exports/bulk_action_{bulk_action.id}.json"
    
    @classmethod
    def get_bulk_action_progress(cls, bulk_action_id: str) -> Dict[str, Any]:
        """Get progress of a bulk action"""
        bulk_action = BulkAction.objects.get(id=bulk_action_id)
        
        progress_percentage = 0
        if bulk_action.total_submissions > 0:
            progress_percentage = (bulk_action.processed_submissions / bulk_action.total_submissions) * 100
        
        return {
            'id': str(bulk_action.id),
            'status': bulk_action.status,
            'action_type': bulk_action.action_type,
            'total': bulk_action.total_submissions,
            'processed': bulk_action.processed_submissions,
            'successful': bulk_action.successful_submissions,
            'failed': bulk_action.failed_submissions,
            'progress_percentage': round(progress_percentage, 2),
            'started_at': bulk_action.started_at,
            'completed_at': bulk_action.completed_at,
            'export_file_url': bulk_action.export_file_url
        }
    
    @classmethod
    def cancel_bulk_action(cls, bulk_action_id: str) -> bool:
        """Cancel a pending or processing bulk action"""
        try:
            bulk_action = BulkAction.objects.get(id=bulk_action_id)
            
            if bulk_action.status in ['pending', 'processing']:
                # Mark remaining items as cancelled
                BatchProcessingQueue.objects.filter(
                    bulk_action=bulk_action,
                    status='pending'
                ).update(status='failed', error_message='Cancelled by user')
                
                bulk_action.status = 'failed'
                bulk_action.result_data = {'cancelled': True}
                bulk_action.completed_at = timezone.now()
                bulk_action.save()
                
                return True
            
            return False
            
        except BulkAction.DoesNotExist:
            return False
