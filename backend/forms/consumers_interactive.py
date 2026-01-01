"""
WebSocket Consumers for Real-Time Features
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime


class CollaborationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time collaboration
    """
    async def connect(self):
        self.form_id = self.scope['url_route']['kwargs']['form_id']
        self.room_group_name = f'form_{self.form_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send user joined message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.scope.get('user', {}).get('id', 'anonymous'),
                'timestamp': datetime.now().isoformat(),
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Send user left message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.scope.get('user', {}).get('id', 'anonymous'),
                'timestamp': datetime.now().isoformat(),
            }
        )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Route message based on type
        if message_type == 'cursor_move':
            await self.handle_cursor_move(data)
        elif message_type == 'field_select':
            await self.handle_field_select(data)
        elif message_type == 'schema_update':
            await self.handle_schema_update(data)
        elif message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'heartbeat':
            await self.send(text_data=json.dumps({'type': 'heartbeat_ack'}))

    async def handle_cursor_move(self, data):
        """Handle cursor movement"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_update',
                'user_id': data.get('userId'),
                'x': data.get('x'),
                'y': data.get('y'),
            }
        )

    async def handle_field_select(self, data):
        """Handle field selection"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'field_selected',
                'user_id': data.get('userId'),
                'field_id': data.get('fieldId'),
            }
        )

    async def handle_schema_update(self, data):
        """Handle schema/form structure update"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'schema_changed',
                'user_id': data.get('userId'),
                'changes': data.get('changes'),
                'timestamp': datetime.now().isoformat(),
            }
        )

    async def handle_chat_message(self, data):
        """Handle chat message"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_received',
                'user_id': data.get('userId'),
                'user_name': data.get('userName'),
                'message': data.get('message'),
                'timestamp': datetime.now().isoformat(),
            }
        )

    # Message handlers (receive from group_send)
    async def user_joined(self, event):
        """Send user joined event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'userId': event['user_id'],
            'timestamp': event['timestamp'],
        }))

    async def user_left(self, event):
        """Send user left event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'userId': event['user_id'],
            'timestamp': event['timestamp'],
        }))

    async def cursor_update(self, event):
        """Send cursor update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'cursor_move',
            'userId': event['user_id'],
            'x': event['x'],
            'y': event['y'],
        }))

    async def field_selected(self, event):
        """Send field selection to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'field_select',
            'userId': event['user_id'],
            'fieldId': event['field_id'],
        }))

    async def schema_changed(self, event):
        """Send schema change to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'schema_update',
            'userId': event['user_id'],
            'changes': event['changes'],
            'timestamp': event['timestamp'],
        }))

    async def chat_message_received(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'userId': event['user_id'],
            'userName': event['user_name'],
            'message': event['message'],
            'timestamp': event['timestamp'],
        }))


class AnalyticsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time analytics updates
    """
    async def connect(self):
        self.form_id = self.scope['url_route']['kwargs']['form_id']
        self.room_group_name = f'analytics_{self.form_id}'
        
        # Join analytics group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave analytics group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming messages"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            # Subscribe to specific analytics metrics
            pass

    async def analytics_update(self, event):
        """Send analytics update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'analytics_update',
            'metric': event['metric'],
            'value': event['value'],
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
        }))

    async def new_submission(self, event):
        """Send new submission notification"""
        await self.send(text_data=json.dumps({
            'type': 'new_submission',
            'submissionId': event['submission_id'],
            'data': event['data'],
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
        }))


class WorkflowExecutionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for workflow execution updates
    """
    async def connect(self):
        self.workflow_id = self.scope['url_route']['kwargs']['workflow_id']
        self.room_group_name = f'workflow_{self.workflow_id}'
        
        # Join workflow group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave workflow group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def workflow_started(self, event):
        """Send workflow started event"""
        await self.send(text_data=json.dumps({
            'type': 'workflow_started',
            'executionId': event['execution_id'],
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
        }))

    async def node_executing(self, event):
        """Send node execution event"""
        await self.send(text_data=json.dumps({
            'type': 'node_executing',
            'nodeId': event['node_id'],
            'nodeName': event['node_name'],
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
        }))

    async def node_completed(self, event):
        """Send node completed event"""
        await self.send(text_data=json.dumps({
            'type': 'node_completed',
            'nodeId': event['node_id'],
            'status': event['status'],
            'result': event.get('result'),
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
        }))

    async def workflow_completed(self, event):
        """Send workflow completed event"""
        await self.send(text_data=json.dumps({
            'type': 'workflow_completed',
            'executionId': event['execution_id'],
            'status': event['status'],
            'result': event.get('result'),
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
        }))
