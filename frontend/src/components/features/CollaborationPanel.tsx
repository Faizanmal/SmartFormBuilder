'use client';

import { useState, useEffect, useCallback } from 'react';
import { collaborationAPI } from '@/lib/advancedFeaturesAPI';
import { FormCollaborator, FormEditSession, FormComment } from '@/types/advancedFeatures';

interface CollaborationPanelProps {
  formId: string;
}

export default function CollaborationPanel({ formId }: CollaborationPanelProps) {
  const [collaborators, setCollaborators] = useState<FormCollaborator[]>([]);
  const [activeSessions, setActiveSessions] = useState<FormEditSession[]>([]);
  const [comments, setComments] = useState<FormComment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [collaboratorsData, sessionsData, commentsData] = await Promise.all([
        collaborationAPI.getCollaborators(formId),
        collaborationAPI.getActiveSessions(formId),
        collaborationAPI.getComments(formId),
      ]);
      setCollaborators(collaboratorsData);
      setActiveSessions(sessionsData);
      setComments(commentsData);
    } catch (error) {
      console.error('Failed to load collaboration data:', error);
    } finally {
      setLoading(false);
    }
  }, [formId]);

  const loadActiveSessions = useCallback(async () => {
    try {
      const sessionsData = await collaborationAPI.getActiveSessions(formId);
      setActiveSessions(sessionsData);
    } catch (error) {
      console.error('Failed to load active sessions:', error);
    }
  }, [formId]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadActiveSessions, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, [loadData, loadActiveSessions]);

  const handleInviteCollaborator = async () => {
    const email = prompt('Enter collaborator email:');
    if (!email) return;

    const role = prompt('Enter role (viewer/editor/admin):', 'editor');
    if (!role) return;

    try {
      await collaborationAPI.inviteCollaborator({
        form: formId,
        user: email, // This should be user ID in production
        role: role as 'viewer' | 'editor' | 'admin',
        permissions: [],
      });
      await loadData();
      alert('Invitation sent!');
    } catch (error) {
      console.error('Failed to invite collaborator:', error);
      alert('Failed to send invitation');
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      await collaborationAPI.createComment({
        form: formId,
        content: newComment,
        field_id: null,
      });
      setNewComment('');
      await loadData();
    } catch (error) {
      console.error('Failed to add comment:', error);
      alert('Failed to add comment');
    }
  };

  const handleResolveComment = async (commentId: string) => {
    try {
      await collaborationAPI.resolveComment(commentId);
      await loadData();
    } catch (error) {
      console.error('Failed to resolve comment:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Collaboration</h2>
            <p className="text-gray-600 mt-1">Work together in real-time</p>
          </div>
          <button
            onClick={handleInviteCollaborator}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Invite Collaborator
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
        {/* Collaborators List */}
        <div className="lg:col-span-1">
          <h3 className="font-semibold mb-4">Team Members ({collaborators.length})</h3>
          <div className="space-y-2">
            {collaborators.map((collab) => (
              <div
                key={collab.id}
                className="flex items-center gap-3 p-3 border rounded hover:bg-gray-50"
              >
                <div className="w-10 h-10 rounded-full bg-linear-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-semibold">
                  {collab.user_email?.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm">{collab.user_email}</div>
                  <div className="text-xs text-gray-500 capitalize">{collab.role}</div>
                </div>
                {!collab.invitation_accepted && (
                  <span className="text-xs text-orange-600">Pending</span>
                )}
              </div>
            ))}
          </div>

          {/* Active Sessions */}
          {activeSessions.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                Active Now ({activeSessions.length})
              </h3>
              <div className="space-y-2">
                {activeSessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center gap-3 p-2 bg-green-50 rounded"
                  >
                    <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white text-xs">
                      {session.user_name?.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{session.user_name}</div>
                      <div className="text-xs text-gray-500">
                        Editing for {Math.floor((new Date().getTime() - new Date(session.started_at).getTime()) / 60000)}m
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Comments Section */}
        <div className="lg:col-span-2">
          <h3 className="font-semibold mb-4">Comments & Feedback ({comments.length})</h3>
          
          {/* Add Comment */}
          <div className="mb-4">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
            <button
              onClick={handleAddComment}
              disabled={!newComment.trim()}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Post Comment
            </button>
          </div>

          {/* Comments List */}
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {comments.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                No comments yet. Be the first to add feedback!
              </div>
            ) : (
              comments.map((comment) => (
                <div
                  key={comment.id}
                  className={`border rounded-lg p-4 ${
                    comment.is_resolved ? 'bg-gray-50 opacity-60' : 'bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex gap-3">
                      <div className="w-10 h-10 rounded-full bg-linear-to-br from-purple-400 to-pink-500 flex items-center justify-center text-white font-semibold">
                        {comment.user_name?.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium">{comment.user_name}</div>
                        <div className="text-sm text-gray-500">
                          {new Date(comment.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    {!comment.is_resolved && (
                      <button
                        onClick={() => handleResolveComment(comment.id)}
                        className="text-sm text-green-600 hover:text-green-700 font-medium"
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                  <p className="mt-3 text-gray-700">{comment.content}</p>
                  {comment.is_resolved && (
                    <div className="mt-2 text-xs text-green-600">
                      ✓ Resolved by {comment.resolved_by_email}
                    </div>
                  )}
                  {comment.replies && comment.replies.length > 0 && (
                    <div className="mt-3 pl-4 border-l-2 border-gray-200 space-y-2">
                      {comment.replies.map((reply) => (
                        <div key={reply.id} className="text-sm">
                          <span className="font-medium">{reply.user_name}:</span>{' '}
                          {reply.content}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
