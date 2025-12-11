"""
Real-time collaboration and WebSocket services
"""
from typing import Dict, List
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class CollaborationService:
    """Real-time collaboration features"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def start_edit_session(self, form_id: str, user, session_id: str) -> Dict:
        """Start editing session"""
        from ..models_collaboration import FormEditSession
        
        try:
            session = FormEditSession.objects.create(
                form_id=form_id,
                user=user,
                session_id=session_id,
                is_active=True
            )
            
            # Notify other collaborators
            self._broadcast_to_form(
                form_id,
                {
                    'type': 'user_joined',
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'name': user.get_full_name()
                    },
                    'session_id': session_id
                },
                exclude_session=session_id
            )
            
            return {
                'success': True,
                'session_id': str(session.id)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def end_edit_session(self, session_id: str) -> Dict:
        """End editing session"""
        from ..models_collaboration import FormEditSession
        
        try:
            session = FormEditSession.objects.get(session_id=session_id)
            session.is_active = False
            session.save()
            
            # Notify other collaborators
            self._broadcast_to_form(
                str(session.form.id),
                {
                    'type': 'user_left',
                    'user': {
                        'id': str(session.user.id),
                        'email': session.user.email
                    }
                },
                exclude_session=session_id
            )
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_change(
        self,
        form_id: str,
        user,
        session_id: str,
        change_type: str,
        change_data: Dict
    ) -> Dict:
        """Sync real-time change to all collaborators"""
        from ..models_collaboration import FormChange
        
        try:
            # Record change
            change = FormChange.objects.create(
                form_id=form_id,
                user=user,
                session_id=session_id,
                change_type=change_type,
                field_id=change_data.get('field_id'),
                previous_value=change_data.get('previous_value'),
                new_value=change_data.get('new_value'),
                change_path=change_data.get('path'),
                is_synced=True
            )
            
            # Broadcast to other collaborators
            self._broadcast_to_form(
                form_id,
                {
                    'type': 'change_synced',
                    'change': {
                        'id': str(change.id),
                        'change_type': change_type,
                        'data': change_data,
                        'user': {
                            'id': str(user.id),
                            'email': user.email
                        },
                        'timestamp': change.created_at.isoformat()
                    }
                },
                exclude_session=session_id
            )
            
            return {
                'success': True,
                'change_id': str(change.id)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_cursor_position(
        self,
        session_id: str,
        field_id: str,
        cursor_position: Dict
    ):
        """Update user's cursor position"""
        from ..models_collaboration import FormEditSession
        
        try:
            session = FormEditSession.objects.get(session_id=session_id)
            session.cursor_position = cursor_position
            session.active_field = field_id
            session.save()
            
            # Broadcast cursor update
            self._broadcast_to_form(
                str(session.form.id),
                {
                    'type': 'cursor_moved',
                    'user': {
                        'id': str(session.user.id),
                        'email': session.user.email
                    },
                    'field_id': field_id,
                    'position': cursor_position
                },
                exclude_session=session_id
            )
        except Exception:
            pass
    
    def add_comment(
        self,
        form_id: str,
        user,
        field_id: str,
        content: str,
        mentions: List[str] = None
    ) -> Dict:
        """Add comment to form field"""
        from ..models_collaboration import FormComment
        
        try:
            comment = FormComment.objects.create(
                form_id=form_id,
                user=user,
                field_id=field_id,
                content=content,
                mentions=mentions or []
            )
            
            # Notify mentioned users
            for mentioned_user_id in (mentions or []):
                # Send notification (placeholder)
                pass
            
            # Broadcast comment
            self._broadcast_to_form(
                form_id,
                {
                    'type': 'comment_added',
                    'comment': {
                        'id': str(comment.id),
                        'field_id': field_id,
                        'content': content,
                        'user': {
                            'id': str(user.id),
                            'email': user.email
                        },
                        'timestamp': comment.created_at.isoformat()
                    }
                }
            )
            
            return {
                'success': True,
                'comment_id': str(comment.id)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def submit_for_review(self, form_id: str, user, reviewers: List[str]) -> Dict:
        """Submit form for review"""
        from ..models_collaboration import FormReviewWorkflow, FormReview
        
        try:
            workflow, created = FormReviewWorkflow.objects.get_or_create(
                form_id=form_id,
                defaults={
                    'submitted_by': user,
                    'status': 'in_review',
                    'submitted_at': datetime.now()
                }
            )
            
            if not created:
                workflow.status = 'in_review'
                workflow.submitted_at = datetime.now()
                workflow.save()
            
            # Create review assignments
            for reviewer_id in reviewers:
                FormReview.objects.get_or_create(
                    workflow=workflow,
                    reviewer_id=reviewer_id,
                    defaults={'decision': 'pending'}
                )
            
            # Notify reviewers (placeholder)
            
            return {
                'success': True,
                'workflow_id': str(workflow.id)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _broadcast_to_form(
        self,
        form_id: str,
        message: Dict,
        exclude_session: str = None
    ):
        """Broadcast message to all form collaborators via WebSocket"""
        if self.channel_layer:
            group_name = f'form_{form_id}'
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'form_message',
                    'message': message,
                    'exclude_session': exclude_session
                }
            )


class PredictiveService:
    """Predictive form completion and smart defaults"""
    
    def predict_field_value(
        self,
        form_id: str,
        field_id: str,
        context_data: Dict
    ) -> Dict:
        """Predict field value based on context"""
        from ..models_predictive import FieldPrediction, UserSubmissionHistory
        
        try:
            prediction_config = FieldPrediction.objects.get(
                form_id=form_id,
                field_id=field_id,
                is_active=True
            )
            
            rule = prediction_config.prediction_rule
            rule_type = rule.get('type')
            
            if rule_type == 'zip_to_city':
                # Predict city from ZIP code
                zip_code = context_data.get('zip_code')
                if zip_code:
                    city = self._lookup_city_from_zip(zip_code)
                    return {
                        'predicted_value': city,
                        'confidence': 0.95
                    }
            
            elif rule_type == 'email_to_domain':
                # Extract domain from email
                email = context_data.get('email')
                if email and '@' in email:
                    domain = email.split('@')[1]
                    return {
                        'predicted_value': domain,
                        'confidence': 1.0
                    }
            
            elif rule_type == 'historical':
                # Use historical data
                user_id = context_data.get('user_identifier')
                history = UserSubmissionHistory.objects.filter(
                    user_identifier=user_id,
                    form_id=form_id
                ).first()
                
                if history and field_id in history.field_values:
                    return {
                        'predicted_value': history.field_values[field_id],
                        'confidence': 0.8
                    }
            
            return {'predicted_value': None, 'confidence': 0}
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_completion_prediction(
        self,
        form_id: str,
        session_id: str,
        filled_fields: int,
        total_fields: int
    ) -> Dict:
        """Calculate form completion prediction"""
        from ..models_predictive import CompletionPrediction
        
        # Simple heuristic-based prediction
        progress_percent = int((filled_fields / total_fields) * 100)
        
        # Estimate time remaining based on average field completion time
        avg_time_per_field = 30  # seconds
        remaining_fields = total_fields - filled_fields
        estimated_time = remaining_fields * avg_time_per_field
        
        prediction = CompletionPrediction.objects.create(
            form_id=form_id,
            session_id=session_id,
            current_field_index=filled_fields,
            total_fields=total_fields,
            required_fields_completed=filled_fields,  # Simplified
            required_fields_total=total_fields,
            predicted_completion_percent=progress_percent,
            estimated_time_remaining=estimated_time,
            confidence_score=0.75
        )
        
        return {
            'completion_percent': progress_percent,
            'estimated_time_remaining': estimated_time,
            'fields_remaining': remaining_fields
        }
    
    def _lookup_city_from_zip(self, zip_code: str) -> str:
        """Lookup city from ZIP code (placeholder)"""
        # In production, use a ZIP code database or API
        return "Unknown City"


class MobileService:
    """Mobile optimization services"""
    
    def track_mobile_analytics(
        self,
        form_id: str,
        device_info: Dict,
        metrics: Dict
    ):
        """Track mobile-specific analytics"""
        from ..models_mobile import MobileAnalytics
        
        MobileAnalytics.objects.create(
            form_id=form_id,
            device_type=device_info.get('device_type'),
            os=device_info.get('os'),
            os_version=device_info.get('os_version'),
            browser=device_info.get('browser'),
            screen_resolution=device_info.get('screen_resolution'),
            touch_interactions=metrics.get('touch_interactions', 0),
            swipe_actions=metrics.get('swipe_actions', 0),
            load_time_ms=metrics.get('load_time_ms', 0),
            completion_time_s=metrics.get('completion_time_s', 0),
            session_id=metrics.get('session_id'),
            submitted=metrics.get('submitted', False)
        )
    
    def queue_offline_submission(
        self,
        form_id: str,
        device_id: str,
        submission_data: Dict
    ) -> Dict:
        """Queue submission for offline sync"""
        from ..models_mobile import OfflineSubmission
        
        try:
            offline_sub = OfflineSubmission.objects.create(
                form_id=form_id,
                device_id=device_id,
                submission_data=submission_data,
                status='pending',
                created_at=datetime.now()
            )
            
            return {
                'success': True,
                'offline_id': str(offline_sub.id)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_push_notification(
        self,
        subscription_id: str,
        title: str,
        body: str,
        data: Dict = None
    ) -> Dict:
        """Send push notification to mobile device"""
        from ..models_mobile import PushNotificationSubscription, FormNotification
        
        try:
            subscription = PushNotificationSubscription.objects.get(
                id=subscription_id,
                is_active=True
            )
            
            # Create notification record
            notification = FormNotification.objects.create(
                form_id=data.get('form_id') if data else None,
                subscription=subscription,
                notification_type=data.get('type', 'custom') if data else 'custom',
                title=title,
                body=body,
                data=data or {}
            )
            
            # Send via Web Push (placeholder - requires VAPID keys)
            # webpush(
            #     subscription_info={...},
            #     data=json.dumps({'title': title, 'body': body}),
            #     vapid_private_key=settings.VAPID_PRIVATE_KEY,
            #     vapid_claims={...}
            # )
            
            notification.sent_at = datetime.now()
            notification.save()
            
            return {
                'success': True,
                'notification_id': str(notification.id)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
