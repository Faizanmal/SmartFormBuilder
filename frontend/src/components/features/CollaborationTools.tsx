'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Users,
  MessageSquare,
  History,
  GitBranch,
  Shield,
  UserPlus,
  Send,
  Check,
  X,
  ChevronRight,
  ChevronDown,
  Clock,
  Pencil,
  Eye,
  Crown,
  Loader2,
  ArrowLeftRight,
  RotateCcw,
} from 'lucide-react';

interface Collaborator {
  id: string;
  user_email: string;
  user_name: string;
  role: 'owner' | 'editor' | 'reviewer' | 'viewer';
  is_online: boolean;
  last_active_at: string;
  avatar_url?: string;
}

interface EditSession {
  session_id: string;
  user_email: string;
  user_name: string;
  cursor_position: { x: number; y: number };
  active_field: string;
  started_at: string;
}

interface FormChange {
  id: string;
  user_email: string;
  user_name: string;
  change_type: string;
  field_id: string;
  previous_value: any;
  new_value: any;
  created_at: string;
}

interface Comment {
  id: string;
  user_email: string;
  user_name: string;
  field_id: string;
  content: string;
  is_resolved: boolean;
  created_at: string;
  replies: Comment[];
}

interface CollaborationToolsProps {
  formId: string;
  currentUserEmail: string;
}

const ROLE_CONFIG = {
  owner: { label: 'Owner', icon: Crown, color: 'text-yellow-500', permissions: 'Full access' },
  editor: { label: 'Editor', icon: Pencil, color: 'text-blue-500', permissions: 'Can edit form' },
  reviewer: { label: 'Reviewer', icon: MessageSquare, color: 'text-purple-500', permissions: 'Can comment' },
  viewer: { label: 'Viewer', icon: Eye, color: 'text-gray-500', permissions: 'View only' },
};

export function CollaborationTools({ formId, currentUserEmail }: CollaborationToolsProps) {
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
  const [activeSessions, setActiveSessions] = useState<EditSession[]>([]);
  const [changes, setChanges] = useState<FormChange[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newCollaboratorEmail, setNewCollaboratorEmail] = useState('');
  const [newCollaboratorRole, setNewCollaboratorRole] = useState<string>('editor');
  const [newComment, setNewComment] = useState('');
  const [selectedField, setSelectedField] = useState<string>('');
  const [showDiff, setShowDiff] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const fetchCollaborators = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/form-collaborators/?form_id=${formId}`);
      const data = await response.json();
      setCollaborators(data.results || data);
    } catch (error) {
      console.error('Failed to fetch collaborators:', error);
    }
  }, [formId]);

  const fetchActiveSessions = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/collaboration/live/${formId}/`);
      const data = await response.json();
      setActiveSessions(data.active_sessions || []);
    } catch (error) {
      console.error('Failed to fetch active sessions:', error);
    }
  }, [formId]);

  const fetchChanges = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/collaboration/history/${formId}/`);
      const data = await response.json();
      setChanges(data.results || data);
    } catch (error) {
      console.error('Failed to fetch changes:', error);
    }
  }, [formId]);

  const fetchComments = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/collaboration/comments/?form_id=${formId}`);
      const data = await response.json();
      setComments(data.results || data);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  }, [formId]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([
        fetchCollaborators(),
        fetchActiveSessions(),
        fetchChanges(),
        fetchComments(),
      ]);
      setLoading(false);
    };
    loadAll();

    // Set up WebSocket for real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/forms/${formId}/edit/`;
    
    try {
      wsRef.current = new WebSocket(wsUrl);
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }

    return () => {
      wsRef.current?.close();
    };
  }, [fetchCollaborators, fetchActiveSessions, fetchChanges, fetchComments, formId]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'cursor_update':
        setActiveSessions(prev =>
          prev.map(s =>
            s.user_email === data.user_email
              ? { ...s, cursor_position: data.position, active_field: data.field }
              : s
          )
        );
        break;
      case 'user_joined':
        fetchActiveSessions();
        break;
      case 'user_left':
        setActiveSessions(prev =>
          prev.filter(s => s.user_email !== data.user_email)
        );
        break;
      case 'change':
        fetchChanges();
        break;
      case 'comment':
        fetchComments();
        break;
    }
  };

  const inviteCollaborator = async () => {
    if (!newCollaboratorEmail) return;
    
    try {
      await fetch(`/api/v1/form-collaborators/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          email: newCollaboratorEmail,
          role: newCollaboratorRole,
        }),
      });
      setNewCollaboratorEmail('');
      fetchCollaborators();
    } catch (error) {
      console.error('Failed to invite collaborator:', error);
    }
  };

  const updateCollaboratorRole = async (collaboratorId: string, role: string) => {
    try {
      await fetch(`/api/v1/form-collaborators/${collaboratorId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role }),
      });
      fetchCollaborators();
    } catch (error) {
      console.error('Failed to update role:', error);
    }
  };

  const removeCollaborator = async (collaboratorId: string) => {
    try {
      await fetch(`/api/v1/form-collaborators/${collaboratorId}/`, {
        method: 'DELETE',
      });
      fetchCollaborators();
    } catch (error) {
      console.error('Failed to remove collaborator:', error);
    }
  };

  const addComment = async () => {
    if (!newComment.trim()) return;
    
    try {
      await fetch(`/api/v1/features/collaboration/comments/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          field_id: selectedField,
          content: newComment,
          comment_type: 'feedback',
        }),
      });
      setNewComment('');
      fetchComments();
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  const resolveComment = async (commentId: string) => {
    try {
      await fetch(`/api/v1/features/collaboration/comments/${commentId}/resolve/`, {
        method: 'POST',
      });
      fetchComments();
    } catch (error) {
      console.error('Failed to resolve comment:', error);
    }
  };

  const restoreVersion = async (changeId: string) => {
    try {
      await fetch(`/api/v1/features/collaboration/history/${formId}/${changeId}/restore/`, {
        method: 'POST',
      });
      fetchChanges();
    } catch (error) {
      console.error('Failed to restore version:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Active Users */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Users className="h-6 w-6" />
            Collaboration
          </h2>
          <p className="text-muted-foreground">Work together on forms in real-time</p>
        </div>
        
        {/* Active Users Avatars */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground mr-2">
            {activeSessions.length} active
          </span>
          <div className="flex -space-x-2">
            {activeSessions.slice(0, 5).map((session) => (
              <Avatar
                key={session.session_id}
                className="border-2 border-background w-8 h-8"
                title={session.user_name}
              >
                <AvatarFallback className="text-xs">
                  {session.user_name.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
            ))}
            {activeSessions.length > 5 && (
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs border-2 border-background">
                +{activeSessions.length - 5}
              </div>
            )}
          </div>
        </div>
      </div>

      <Tabs defaultValue="team">
        <TabsList>
          <TabsTrigger value="team" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Team
          </TabsTrigger>
          <TabsTrigger value="comments" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Comments
            {comments.filter(c => !c.is_resolved).length > 0 && (
              <Badge variant="secondary" className="ml-1">
                {comments.filter(c => !c.is_resolved).length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            History
          </TabsTrigger>
          <TabsTrigger value="permissions" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Permissions
          </TabsTrigger>
        </TabsList>

        {/* Team Tab */}
        <TabsContent value="team" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Invite Collaborator</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="Email address"
                  value={newCollaboratorEmail}
                  onChange={(e) => setNewCollaboratorEmail(e.target.value)}
                  className="flex-1"
                />
                <Select value={newCollaboratorRole} onValueChange={setNewCollaboratorRole}>
                  <SelectTrigger className="w-[140px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="editor">Editor</SelectItem>
                    <SelectItem value="reviewer">Reviewer</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={inviteCollaborator}>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Invite
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Team Members</CardTitle>
              <CardDescription>{collaborators.length} collaborators</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {collaborators.map((collaborator) => {
                  const roleConfig = ROLE_CONFIG[collaborator.role];
                  const RoleIcon = roleConfig.icon;
                  const isCurrentUser = collaborator.user_email === currentUserEmail;
                  
                  return (
                    <div
                      key={collaborator.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <Avatar>
                            <AvatarImage src={collaborator.avatar_url} />
                            <AvatarFallback>
                              {collaborator.user_name.slice(0, 2).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          {collaborator.is_online && (
                            <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-background rounded-full" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium">
                            {collaborator.user_name}
                            {isCurrentUser && (
                              <span className="text-muted-foreground ml-1">(you)</span>
                            )}
                          </p>
                          <p className="text-sm text-muted-foreground">{collaborator.user_email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={`flex items-center gap-1 ${roleConfig.color}`}>
                          <RoleIcon className="h-4 w-4" />
                          <span className="text-sm">{roleConfig.label}</span>
                        </div>
                        {!isCurrentUser && collaborator.role !== 'owner' && (
                          <>
                            <Select
                              value={collaborator.role}
                              onValueChange={(role) => updateCollaboratorRole(collaborator.id, role)}
                            >
                              <SelectTrigger className="w-[120px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="editor">Editor</SelectItem>
                                <SelectItem value="reviewer">Reviewer</SelectItem>
                                <SelectItem value="viewer">Viewer</SelectItem>
                              </SelectContent>
                            </Select>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => removeCollaborator(collaborator.id)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Comments Tab */}
        <TabsContent value="comments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Add Comment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Input
                  placeholder="Field ID (optional)"
                  value={selectedField}
                  onChange={(e) => setSelectedField(e.target.value)}
                />
                <Textarea
                  placeholder="Write your comment..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
                <Button onClick={addComment} className="w-full">
                  <Send className="h-4 w-4 mr-2" />
                  Post Comment
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Comments</CardTitle>
              <CardDescription>
                {comments.filter(c => !c.is_resolved).length} open,{' '}
                {comments.filter(c => c.is_resolved).length} resolved
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {comments.filter(c => !c.is_resolved).map((comment) => (
                  <div key={comment.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <Avatar className="w-8 h-8">
                          <AvatarFallback className="text-xs">
                            {comment.user_name.slice(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-sm">{comment.user_name}</span>
                            <span className="text-xs text-muted-foreground">
                              {new Date(comment.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          {comment.field_id && (
                            <Badge variant="outline" className="text-xs mt-1">
                              {comment.field_id}
                            </Badge>
                          )}
                          <p className="text-sm mt-2">{comment.content}</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => resolveComment(comment.id)}
                      >
                        <Check className="h-4 w-4 mr-1" />
                        Resolve
                      </Button>
                    </div>
                    
                    {/* Replies */}
                    {comment.replies && comment.replies.length > 0 && (
                      <div className="ml-11 mt-3 space-y-3 border-l-2 pl-4">
                        {comment.replies.map((reply) => (
                          <div key={reply.id} className="flex items-start gap-2">
                            <Avatar className="w-6 h-6">
                              <AvatarFallback className="text-xs">
                                {reply.user_name.slice(0, 2).toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <span className="text-sm font-medium">{reply.user_name}</span>
                              <p className="text-sm text-muted-foreground">{reply.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                {comments.filter(c => !c.is_resolved).length === 0 && (
                  <p className="text-center text-muted-foreground py-4">
                    No open comments
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
              <CardDescription>Track all changes made to this form</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {changes.map((change, index) => (
                  <div key={change.id} className="relative">
                    {index !== changes.length - 1 && (
                      <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-muted" />
                    )}
                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center z-10">
                        <GitBranch className="h-4 w-4" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-medium">{change.user_name}</span>
                            <span className="text-sm text-muted-foreground ml-2">
                              {change.change_type.replace('_', ' ')}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">
                              {new Date(change.created_at).toLocaleString()}
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setShowDiff(showDiff === change.id ? null : change.id)}
                            >
                              <ArrowLeftRight className="h-4 w-4 mr-1" />
                              Diff
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => restoreVersion(change.id)}
                            >
                              <RotateCcw className="h-4 w-4 mr-1" />
                              Restore
                            </Button>
                          </div>
                        </div>
                        {change.field_id && (
                          <Badge variant="outline" className="mt-1">
                            Field: {change.field_id}
                          </Badge>
                        )}
                        
                        {/* Diff View */}
                        {showDiff === change.id && (
                          <div className="mt-3 grid grid-cols-2 gap-4">
                            <div className="p-3 bg-red-50 dark:bg-red-950/20 rounded-lg">
                              <p className="text-xs text-red-600 mb-1">Previous</p>
                              <pre className="text-xs overflow-auto">
                                {JSON.stringify(change.previous_value, null, 2)}
                              </pre>
                            </div>
                            <div className="p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                              <p className="text-xs text-green-600 mb-1">New</p>
                              <pre className="text-xs overflow-auto">
                                {JSON.stringify(change.new_value, null, 2)}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {changes.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No changes recorded yet
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Permissions Tab */}
        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Role Permissions</CardTitle>
              <CardDescription>What each role can do</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(ROLE_CONFIG).map(([role, config]) => {
                  const Icon = config.icon;
                  return (
                    <div key={role} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full bg-muted ${config.color}`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="font-medium">{config.label}</p>
                          <p className="text-sm text-muted-foreground">{config.permissions}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {role === 'owner' && (
                          <>
                            <Badge>Edit</Badge>
                            <Badge>Comment</Badge>
                            <Badge>Publish</Badge>
                            <Badge>Manage Team</Badge>
                          </>
                        )}
                        {role === 'editor' && (
                          <>
                            <Badge>Edit</Badge>
                            <Badge>Comment</Badge>
                          </>
                        )}
                        {role === 'reviewer' && (
                          <Badge>Comment</Badge>
                        )}
                        {role === 'viewer' && (
                          <Badge variant="secondary">View Only</Badge>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default CollaborationTools;
