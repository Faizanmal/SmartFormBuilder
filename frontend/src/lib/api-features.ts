/**
 * API Integration for Interactive Features
 */
import { apiClient } from './api';

// ========== Collaboration API ==========
export interface CollaborationSession {
  id: string;
  formId: string;
  userId: string;
  userName: string;
  color: string;
  isActive: boolean;
  lastSeen: string;
}

export interface CollaborationCursor {
  userId: string;
  x: number;
  y: number;
  fieldId?: string;
}

export interface CollaborationMessage {
  id: string;
  userId: string;
  userName: string;
  message: string;
  timestamp: string;
}

export const collaborationApi = {
  // Join collaboration session
  joinSession: (formId: string, userName: string) => 
    apiClient.post<CollaborationSession>('/collaboration/join/', { formId, userName }),

  // Leave session
  leaveSession: (sessionId: string) => 
    apiClient.post('/collaboration/leave/', { sessionId }),

  // Get active sessions
  getActiveSessions: (formId: string) => 
    apiClient.get<CollaborationSession[]>(`/collaboration/sessions/${formId}/`),

  // Send chat message
  sendMessage: (sessionId: string, message: string) => 
    apiClient.post<CollaborationMessage>('/collaboration/message/', { sessionId, message }),

  // Get chat history
  getMessages: (formId: string) => 
    apiClient.get<CollaborationMessage[]>(`/collaboration/messages/${formId}/`),
};

// ========== Gamification API ==========
export interface GamificationProfile {
  userId: string;
  points: number;
  level: number;
  achievements: string[];
  streak: number;
  totalForms: number;
  dailyChallenges: Record<string, boolean>;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  unlockedAt?: string;
}

export const gamificationApi = {
  // Get user profile
  getProfile: () => 
    apiClient.get<GamificationProfile>('/gamification/profile/'),

  // Award points
  awardPoints: (action: string, points: number) => 
    apiClient.post('/gamification/award-points/', { action, points }),

  // Unlock achievement
  unlockAchievement: (achievementId: string) => 
    apiClient.post('/gamification/unlock-achievement/', { achievementId }),

  // Get leaderboard
  getLeaderboard: (limit = 10) => 
    apiClient.get<GamificationProfile[]>(`/gamification/leaderboard/?limit=${limit}`),

  // Update streak
  updateStreak: () => 
    apiClient.post('/gamification/update-streak/'),
};

// ========== Analytics API ==========
export interface FormAnalytics {
  formId: string;
  timeSeriesData: Array<{
    date: string;
    views: number;
    starts: number;
    submissions: number;
    conversionRate: number;
  }>;
  fieldAnalytics: Array<{
    fieldId: string;
    fieldLabel: string;
    type: string;
    interactions: number;
    averageTime: number;
    errorRate: number;
    dropOffRate: number;
    completionRate: number;
  }>;
  deviceData: Array<{
    device: string;
    count: number;
    percentage: number;
  }>;
  geographyData: Array<{
    country: string;
    code: string;
    count: number;
    percentage: number;
  }>;
  submissions: Array<{
    id: string;
    timestamp: string;
    device: string;
    country: string;
    duration: number;
    fields: Record<string, unknown>;
  }>;
  summary: {
    totalViews: number;
    totalStarts: number;
    totalSubmissions: number;
    conversionRate: number;
    averageCompletionTime: number;
    bounceRate: number;
  };
}

export const analyticsApi = {
  // Get form analytics
  getAnalytics: (formId: string, dateRange = '30') => 
    apiClient.get<FormAnalytics>(`/analytics/forms/${formId}/?range=${dateRange}`),

  // Track event
  trackEvent: (formId: string, event: string, data?: Record<string, unknown>) => 
    apiClient.post('/analytics/track/', { formId, event, data }),

  // Get field performance
  getFieldPerformance: (formId: string, fieldId: string) => 
    apiClient.get(`/analytics/fields/${formId}/${fieldId}/`),

  // Export analytics
  exportAnalytics: (formId: string, format = 'csv') => 
    apiClient.get(`/analytics/export/${formId}/?format=${format}`, { responseType: 'blob' }),
};

// ========== Workflow API ==========
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: Array<{
    id: string;
    type: string;
    title: string;
    position: { x: number; y: number };
    config: Record<string, unknown>;
  }>;
  connections: Array<{
    id: string;
    sourceId: string;
    sourcePort: string;
    targetId: string;
  }>;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startedAt: string;
  completedAt?: string;
  result?: Record<string, unknown>;
  error?: string;
}

export const workflowApi = {
  // List workflows
  listWorkflows: (formId: string) => 
    apiClient.get<Workflow[]>(`/workflows/?formId=${formId}`),

  // Get workflow
  getWorkflow: (workflowId: string) => 
    apiClient.get<Workflow>(`/workflows/${workflowId}/`),

  // Create workflow
  createWorkflow: (workflow: Partial<Workflow>) => 
    apiClient.post<Workflow>('/workflows/', workflow),

  // Update workflow
  updateWorkflow: (workflowId: string, workflow: Partial<Workflow>) => 
    apiClient.put<Workflow>(`/workflows/${workflowId}/`, workflow),

  // Delete workflow
  deleteWorkflow: (workflowId: string) => 
    apiClient.delete(`/workflows/${workflowId}/`),

  // Execute workflow
  executeWorkflow: (workflowId: string, data?: Record<string, unknown>) => 
    apiClient.post<WorkflowExecution>(`/workflows/${workflowId}/execute/`, { data }),

  // Get execution history
  getExecutionHistory: (workflowId: string) => 
    apiClient.get<WorkflowExecution[]>(`/workflows/${workflowId}/executions/`),
};

// ========== Voice API ==========
export interface VoiceTranscription {
  text: string;
  confidence: number;
  fieldId?: string;
  parsedValue?: string;
}

export const voiceApi = {
  // Process voice input (server-side speech-to-text)
  transcribe: (audioBlob: Blob, fieldType?: string) => {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    if (fieldType) formData.append('fieldType', fieldType);
    
    return apiClient.post<VoiceTranscription>('/voice/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Parse voice command
  parseCommand: (text: string, context?: Record<string, unknown>) => 
    apiClient.post('/voice/parse/', { text, context }),

  // Get voice settings
  getSettings: () => 
    apiClient.get('/voice/settings/'),

  // Update voice settings
  updateSettings: (settings: Record<string, unknown>) => 
    apiClient.put('/voice/settings/', settings),
};

// ========== Chatbot API ==========
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  message: string;
  suggestions?: string[];
  action?: {
    type: string;
    data: Record<string, unknown>;
  };
}

export const chatbotApi = {
  // Send message
  sendMessage: (message: string, formId?: string, history?: ChatMessage[]) => 
    apiClient.post<ChatResponse>('/chatbot/message/', { message, formId, history }),

  // Get suggestions
  getSuggestions: (formId: string, context?: string) => 
    apiClient.get<string[]>(`/chatbot/suggestions/?formId=${formId}&context=${context}`),

  // Submit feedback
  submitFeedback: (messageId: string, feedback: 'positive' | 'negative') => 
    apiClient.post('/chatbot/feedback/', { messageId, feedback }),
};

// ========== Form Submission API ==========
export interface FormSubmission {
  id: string;
  formId: string;
  data: Record<string, unknown>;
  device: string;
  location?: {
    country: string;
    city: string;
  };
  duration: number;
  method: 'manual' | 'voice' | 'auto';
  createdAt: string;
}

export const submissionApi = {
  // Submit form
  submit: (formId: string, data: Record<string, unknown>, metadata?: {
    device?: string;
    method?: string;
    duration?: number;
  }) => 
    apiClient.post<FormSubmission>(`/forms/${formId}/submit/`, {
      ...data,
      _metadata: metadata,
    }),

  // Get submission
  getSubmission: (submissionId: string) => 
    apiClient.get<FormSubmission>(`/submissions/${submissionId}/`),

  // List submissions
  listSubmissions: (formId: string, params?: {
    limit?: number;
    offset?: number;
    method?: string;
  }) => 
    apiClient.get<{ results: FormSubmission[]; count: number }>(`/submissions/?formId=${formId}`, { params }),
};

// ========== Gesture Settings API ==========
export interface GestureSettings {
  swipeThreshold: number;
  longPressDelay: number;
  pinchSensitivity: number;
  enabled: boolean;
}

export const gestureApi = {
  // Get settings
  getSettings: () => 
    apiClient.get<GestureSettings>('/settings/gestures/'),

  // Update settings
  updateSettings: (settings: Partial<GestureSettings>) => 
    apiClient.put<GestureSettings>('/settings/gestures/', settings),
};

// ========== AR/VR API ==========
export interface ARAsset {
  id: string;
  formId: string;
  type: '2d' | '3d' | 'ar';
  modelUrl?: string;
  textureUrl?: string;
  metadata: Record<string, unknown>;
}

export const arApi = {
  // Get AR assets
  getAssets: (formId: string) => 
    apiClient.get<ARAsset[]>(`/ar/assets/?formId=${formId}`),

  // Upload AR asset
  uploadAsset: (formId: string, file: File, type: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('formId', formId);
    formData.append('type', type);
    
    return apiClient.post<ARAsset>('/ar/assets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Delete asset
  deleteAsset: (assetId: string) => 
    apiClient.delete(`/ar/assets/${assetId}/`),
};

// Export all APIs
export const featureApis = {
  collaboration: collaborationApi,
  gamification: gamificationApi,
  analytics: analyticsApi,
  workflow: workflowApi,
  voice: voiceApi,
  chatbot: chatbotApi,
  submission: submissionApi,
  gesture: gestureApi,
  ar: arApi,
};

export default featureApis;
