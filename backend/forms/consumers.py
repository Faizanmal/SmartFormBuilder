"""
WebSocket consumers for real-time collaboration
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class FormCollaborationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for real-time form collaboration"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.form_id = self.scope['url_route']['kwargs']['form_id']
        self.room_group_name = f'form_{self.form_id}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others of new user
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': {
                    'id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                    'email': self.user.email if self.user.is_authenticated else 'Anonymous'
                }
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Notify others of user leaving
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': {
                    'id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                    'email': self.user.email if self.user.is_authenticated else 'Anonymous'
                }
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Receive message from WebSocket"""
        message_type = content.get('type')
        
        if message_type == 'form_change':
            # Broadcast form change to all clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'form_change',
                    'change': content.get('change'),
                    'user': {
                        'id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                        'email': self.user.email if self.user.is_authenticated else 'Anonymous'
                    }
                }
            )
        
        elif message_type == 'cursor_move':
            # Broadcast cursor position
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cursor_moved',
                    'field_id': content.get('field_id'),
                    'position': content.get('position'),
                    'user': {
                        'id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                        'email': self.user.email if self.user.is_authenticated else 'Anonymous'
                    }
                }
            )
        
        elif message_type == 'comment':
            # Handle comment
            await self.save_comment(content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'comment_added',
                    'comment': content.get('comment'),
                    'user': {
                        'id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                        'email': self.user.email if self.user.is_authenticated else 'Anonymous'
                    }
                }
            )
    
    # Handlers for different message types
    async def user_joined(self, event):
        """Send user joined notification"""
        await self.send_json({
            'type': 'user_joined',
            'user': event['user']
        })
    
    async def user_left(self, event):
        """Send user left notification"""
        await self.send_json({
            'type': 'user_left',
            'user': event['user']
        })
    
    async def form_change(self, event):
        """Send form change update"""
        await self.send_json({
            'type': 'form_change',
            'change': event['change'],
            'user': event['user']
        })
    
    async def cursor_moved(self, event):
        """Send cursor position update"""
        await self.send_json({
            'type': 'cursor_moved',
            'field_id': event['field_id'],
            'position': event['position'],
            'user': event['user']
        })
    
    async def comment_added(self, event):
        """Send new comment notification"""
        await self.send_json({
            'type': 'comment_added',
            'comment': event['comment'],
            'user': event['user']
        })
    
    @database_sync_to_async
    def save_comment(self, content):
        """Save comment to database"""
        from .models_collaboration import FormComment
        from .models import Form
        
        if self.user.is_authenticated:
            try:
                form = Form.objects.get(id=self.form_id)
                FormComment.objects.create(
                    form=form,
                    user=self.user,
                    field_id=content.get('field_id'),
                    content=content.get('content', ''),
                    mentions=content.get('mentions', [])
                )
            except Exception as e:
                print(f"Error saving comment: {e}")
