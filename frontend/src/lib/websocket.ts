/**
 * WebSocket utilities for real-time collaboration
 */

export interface CollaborationUser {
  id: string;
  name: string;
  color: string;
  cursor?: { x: number; y: number };
  selectedField?: string;
}

export interface CollaborationMessage {
  type: 'user_joined' | 'user_left' | 'cursor_move' | 'field_update' | 'field_select' | 'schema_update' | 'chat';
  userId: string;
  userName?: string;
  payload: unknown;
  timestamp: string;
}

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export class FormCollaborationSocket {
  private ws: WebSocket | null = null;
  private formId: string;
  private userId: string;
  private userName: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, ((message: CollaborationMessage) => void)[]> = new Map();
  private connectionStateHandlers: ((state: ConnectionState) => void)[] = [];
  
  constructor(formId: string, userId: string, userName: string) {
    this.formId = formId;
    this.userId = userId;
    this.userName = userName;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Use environment variable or default to backend URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = process.env.NEXT_PUBLIC_WS_URL || 
                     (process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000');
      const wsUrl = `${wsProtocol}//${wsHost}/ws/collaboration/${this.formId}/`;
      
      this.notifyConnectionState('connecting');
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.notifyConnectionState('connected');
        
        // Send join message
        this.send({
          type: 'user_joined',
          userId: this.userId,
          userName: this.userName,
          payload: { joinedAt: new Date().toISOString() },
          timestamp: new Date().toISOString(),
        });

        // Start heartbeat
        this.startHeartbeat();
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: CollaborationMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyConnectionState('error');
        reject(error);
      };

      this.ws.onclose = () => {
        this.notifyConnectionState('disconnected');
        this.stopHeartbeat();
        this.attemptReconnect();
      };
    });
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      setTimeout(() => this.connect(), delay);
    }
  }

  private handleMessage(message: CollaborationMessage) {
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach((handler) => handler(message));
    
    // Also notify 'all' handlers
    const allHandlers = this.messageHandlers.get('all') || [];
    allHandlers.forEach((handler) => handler(message));
  }

  private notifyConnectionState(state: ConnectionState) {
    this.connectionStateHandlers.forEach((handler) => handler(state));
  }

  on(type: string, handler: (message: CollaborationMessage) => void) {
    const handlers = this.messageHandlers.get(type) || [];
    handlers.push(handler);
    this.messageHandlers.set(type, handlers);
  }

  off(type: string, handler: (message: CollaborationMessage) => void) {
    const handlers = this.messageHandlers.get(type) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
      this.messageHandlers.set(type, handlers);
    }
  }

  onConnectionStateChange(handler: (state: ConnectionState) => void) {
    this.connectionStateHandlers.push(handler);
  }

  send(message: CollaborationMessage) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  sendCursorPosition(x: number, y: number) {
    this.send({
      type: 'cursor_move',
      userId: this.userId,
      userName: this.userName,
      payload: { x, y },
      timestamp: new Date().toISOString(),
    });
  }

  sendFieldSelect(fieldId: string | null) {
    this.send({
      type: 'field_select',
      userId: this.userId,
      userName: this.userName,
      payload: { fieldId },
      timestamp: new Date().toISOString(),
    });
  }

  sendFieldUpdate(fieldId: string, updates: Record<string, unknown>) {
    this.send({
      type: 'field_update',
      userId: this.userId,
      userName: this.userName,
      payload: { fieldId, updates },
      timestamp: new Date().toISOString(),
    });
  }

  sendSchemaUpdate(schema: Record<string, unknown>) {
    this.send({
      type: 'schema_update',
      userId: this.userId,
      userName: this.userName,
      payload: { schema },
      timestamp: new Date().toISOString(),
    });
  }

  sendChatMessage(message: string) {
    this.send({
      type: 'chat',
      userId: this.userId,
      userName: this.userName,
      payload: { message },
      timestamp: new Date().toISOString(),
    });
  }

  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.send({
        type: 'user_left',
        userId: this.userId,
        payload: {},
        timestamp: new Date().toISOString(),
      });
      this.ws.close();
      this.ws = null;
    }
  }
}

// Color palette for collaboration users
export const COLLABORATION_COLORS = [
  '#667eea', '#f093fb', '#4facfe', '#fa709a', '#43e97b',
  '#f5576c', '#4481eb', '#04befe', '#ff930f', '#a855f7',
];

export function getRandomColor(): string {
  return COLLABORATION_COLORS[Math.floor(Math.random() * COLLABORATION_COLORS.length)];
}
