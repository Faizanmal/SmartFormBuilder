/**
 * Real-Time Collaboration Panel Component
 * Displays active collaborators, cursors, and chat
 */
'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Users,
  MessageCircle,
  Send,
  Wifi,
  WifiOff,
  Circle,
  MousePointer2,
} from 'lucide-react';
import { FormCollaborationSocket, CollaborationUser, CollaborationMessage, ConnectionState, getRandomColor } from '@/lib/websocket';
import { cn } from '@/lib/utils';

interface ChatMessage {
  userId: string;
  userName: string;
  message: string;
  timestamp: Date;
  color: string;
}

interface CollaborationPanelProps {
  formId: string;
  userId: string;
  userName: string;
  onSchemaUpdate?: (schema: Record<string, unknown>) => void;
  onFieldSelect?: (userId: string, fieldId: string | null) => void;
  className?: string;
}

export function CollaborationPanel({
  formId,
  userId,
  userName,
  onSchemaUpdate,
  onFieldSelect,
  className,
}: CollaborationPanelProps) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [collaborators, setCollaborators] = useState<Map<string, CollaborationUser>>(new Map());
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  
  const socketRef = useRef<FormCollaborationSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const userColorRef = useRef(getRandomColor());

  const handleMessage = useCallback((message: CollaborationMessage) => {
    switch (message.type) {
      case 'user_joined': {
        const payload = message.payload as { joinedAt: string };
        setCollaborators((prev) => {
          const updated = new Map(prev);
          updated.set(message.userId, {
            id: message.userId,
            name: message.userName || 'Anonymous',
            color: getRandomColor(),
          });
          return updated;
        });
        
        // System message
        setChatMessages((prev) => [...prev, {
          userId: 'system',
          userName: 'System',
          message: `${message.userName || 'Someone'} joined the session`,
          timestamp: new Date(payload.joinedAt),
          color: '#888',
        }]);
        break;
      }
      
      case 'user_left':
        setCollaborators((prev) => {
          const updated = new Map(prev);
          updated.delete(message.userId);
          return updated;
        });
        
        setChatMessages((prev) => [...prev, {
          userId: 'system',
          userName: 'System',
          message: `${message.userName || 'Someone'} left the session`,
          timestamp: new Date(),
          color: '#888',
        }]);
        break;
      
      case 'cursor_move': {
        const cursorPayload = message.payload as { x: number; y: number };
        setCollaborators((prev) => {
          const updated = new Map(prev);
          const user = updated.get(message.userId);
          if (user) {
            updated.set(message.userId, {
              ...user,
              cursor: { x: cursorPayload.x, y: cursorPayload.y },
            });
          }
          return updated;
        });
        break;
      }
      
      case 'field_select': {
        const selectPayload = message.payload as { fieldId: string | null };
        setCollaborators((prev) => {
          const updated = new Map(prev);
          const user = updated.get(message.userId);
          if (user) {
            updated.set(message.userId, {
              ...user,
              selectedField: selectPayload.fieldId || undefined,
            });
          }
          return updated;
        });
        onFieldSelect?.(message.userId, selectPayload.fieldId);
        break;
      }
      
      case 'schema_update': {
        const schemaPayload = message.payload as { schema: Record<string, unknown> };
        onSchemaUpdate?.(schemaPayload.schema);
        break;
      }
      
      case 'chat': {
        const chatPayload = message.payload as { message: string };
        const user = collaborators.get(message.userId);
        setChatMessages((prev) => [...prev, {
          userId: message.userId,
          userName: message.userName || 'Anonymous',
          message: chatPayload.message,
          timestamp: new Date(message.timestamp),
          color: user?.color || getRandomColor(),
        }]);
        
        if (!showChat) {
          setUnreadCount((prev) => prev + 1);
        }
        break;
      }
    }
  }, [onFieldSelect, onSchemaUpdate, showChat, collaborators]);

  useEffect(() => {
    const socket = new FormCollaborationSocket(formId, userId, userName);
    socketRef.current = socket;

    socket.onConnectionStateChange(setConnectionState);
    socket.on('all', handleMessage);

    socket.connect().catch(console.error);

    return () => {
      socket.disconnect();
    };
  }, [formId, userId, userName, handleMessage]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const sendMessage = () => {
    if (!newMessage.trim() || !socketRef.current) return;
    
    socketRef.current.sendChatMessage(newMessage);
    setChatMessages((prev) => [...prev, {
      userId,
      userName,
      message: newMessage,
      timestamp: new Date(),
      color: userColorRef.current,
    }]);
    setNewMessage('');
  };

  const toggleChat = () => {
    setShowChat(!showChat);
    if (!showChat) {
      setUnreadCount(0);
    }
  };

  const collaboratorList = Array.from(collaborators.values()).filter((c) => c.id !== userId);

  return (
    <div className={cn('space-y-4', className)}>
      {/* Connection Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {connectionState === 'connected' ? (
            <Wifi className="h-4 w-4 text-green-500" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-500" />
          )}
          <span className="text-sm text-muted-foreground">
            {connectionState === 'connected' ? 'Live' : connectionState}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="gap-1">
            <Users className="h-3 w-3" />
            {collaboratorList.length + 1}
          </Badge>
          
          <Button
            variant="outline"
            size="sm"
            onClick={toggleChat}
            className="relative"
          >
            <MessageCircle className="h-4 w-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </Button>
        </div>
      </div>

      {/* Collaborators List */}
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm">Active Collaborators</CardTitle>
        </CardHeader>
        <CardContent className="py-2">
          <div className="space-y-2">
            {/* Current User */}
            <div className="flex items-center gap-2">
              <Avatar className="h-6 w-6">
                <AvatarFallback 
                  style={{ backgroundColor: userColorRef.current }}
                  className="text-white text-xs"
                >
                  {userName.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium">{userName}</span>
              <Badge variant="outline" className="text-xs">You</Badge>
            </div>

            {/* Other Collaborators */}
            {collaboratorList.map((user) => (
              <div key={user.id} className="flex items-center gap-2">
                <div className="relative">
                  <Avatar className="h-6 w-6">
                    <AvatarFallback 
                      style={{ backgroundColor: user.color }}
                      className="text-white text-xs"
                    >
                      {user.name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <Circle 
                    className="absolute -bottom-0.5 -right-0.5 h-2 w-2 fill-green-500 text-green-500"
                  />
                </div>
                <span className="text-sm">{user.name}</span>
                {user.selectedField && (
                  <Badge variant="secondary" className="text-xs gap-1">
                    <MousePointer2 className="h-3 w-3" />
                    Editing
                  </Badge>
                )}
              </div>
            ))}

            {collaboratorList.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No other collaborators yet
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Chat Panel */}
      {showChat && (
        <Card className="animate-in slide-in-from-right-5">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Team Chat</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-64 px-4">
              <div className="space-y-3 py-4">
                {chatMessages.map((msg, index) => (
                  <div 
                    key={index} 
                    className={cn(
                      'flex gap-2',
                      msg.userId === userId && 'flex-row-reverse'
                    )}
                  >
                    {msg.userId !== 'system' && (
                      <Avatar className="h-6 w-6 shrink-0">
                        <AvatarFallback 
                          style={{ backgroundColor: msg.color }}
                          className="text-white text-xs"
                        >
                          {msg.userName.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    )}
                    <div className={cn(
                      'max-w-[80%]',
                      msg.userId === userId && 'text-right'
                    )}>
                      {msg.userId === 'system' ? (
                        <p className="text-xs text-muted-foreground italic text-center">
                          {msg.message}
                        </p>
                      ) : (
                        <>
                          <p className="text-xs text-muted-foreground">
                            {msg.userId === userId ? 'You' : msg.userName}
                          </p>
                          <div className={cn(
                            'rounded-lg px-3 py-2 text-sm',
                            msg.userId === userId 
                              ? 'bg-primary text-primary-foreground' 
                              : 'bg-muted'
                          )}>
                            {msg.message}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            </ScrollArea>
            
            <div className="p-4 border-t flex gap-2">
              <Input
                placeholder="Type a message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              />
              <Button size="icon" onClick={sendMessage}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default CollaborationPanel;
