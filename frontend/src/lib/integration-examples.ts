/**
 * Integration Examples for Interactive Features
 * This file shows how to connect frontend components with backend APIs
 */

import { featureApis } from '@/lib/api-features';
import { FormCollaborationSocket } from '@/lib/websocket';

// ========== 1. Real-Time Collaboration Integration ==========
export async function setupCollaboration(formId: string, userName: string) {
  try {
    // Join session via REST API
    const { data: session } = await featureApis.collaboration.joinSession(formId, userName);
    
    // Connect WebSocket
    const socket = new FormCollaborationSocket(formId, session.userId, userName);
    await socket.connect();
    
    // Listen for cursor updates
    socket.on('cursor_move', (message) => {
      console.log('User moved cursor:', message);
      // Update UI to show other users' cursors
    });
    
    // Listen for schema changes
    socket.on('schema_update', (message) => {
      console.log('Form schema updated:', message);
      // Update form builder UI
    });
    
    // Send cursor position
    socket.sendCursorPosition(100, 200);
    
    return socket;
  } catch (error) {
    console.error('Collaboration setup failed:', error);
    throw error;
  }
}

// ========== 2. Gamification Integration ==========
export async function trackUserAction(action: string, points: number) {
  try {
    // Award points
    await featureApis.gamification.awardPoints(action, points);
    
    // Get updated profile
    const { data: profile } = await featureApis.gamification.getProfile();
    
    // Check for new achievements
    if (profile.points >= 1000 && !profile.achievements.includes('points_master')) {
      await featureApis.gamification.unlockAchievement('points_master');
    }
    
    return profile;
  } catch (error) {
    console.error('Gamification tracking failed:', error);
  }
}

// Usage in form builder:
// trackUserAction('form_created', 50);
// trackUserAction('field_added', 10);
// trackUserAction('form_published', 100);

// ========== 3. Interactive Analytics Integration ==========
export async function loadFormAnalytics(formId: string, dateRange = '30') {
  try {
    const { data: analytics } = await featureApis.analytics.getAnalytics(formId, dateRange);
    
    // Track user interaction
    await featureApis.analytics.trackEvent(formId, 'analytics_viewed', {
      timestamp: new Date().toISOString(),
    });
    
    return analytics;
  } catch (error) {
    console.error('Analytics loading failed:', error);
    throw error;
  }
}

// Export analytics
export async function exportAnalyticsData(formId: string, format = 'csv') {
  try {
    const response = await featureApis.analytics.exportAnalytics(formId, format);
    
    // Create download link
    const url = URL.createObjectURL(response.data);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${formId}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Export failed:', error);
  }
}

// ========== 4. Workflow Integration ==========
export async function createAndExecuteWorkflow(formId: string, workflowConfig: any) {
  try {
    // Create workflow
    const { data: workflow } = await featureApis.workflow.createWorkflow({
      name: 'New Form Submission Workflow',
      description: 'Send email and webhook on form submit',
      nodes: workflowConfig.nodes,
      connections: workflowConfig.connections,
      isActive: true,
    });
    
    // Execute workflow
    const { data: execution } = await featureApis.workflow.executeWorkflow(
      workflow.id,
      { formId, testData: true }
    );
    
    console.log('Workflow executed:', execution);
    
    return { workflow, execution };
  } catch (error) {
    console.error('Workflow creation failed:', error);
    throw error;
  }
}

// ========== 5. Voice Input Integration ==========
export async function processVoiceInput(audioBlob: Blob, fieldType: string) {
  try {
    const { data: transcription } = await featureApis.voice.transcribe(audioBlob, fieldType);
    
    console.log('Transcribed:', transcription.text);
    console.log('Confidence:', transcription.confidence);
    
    return transcription.parsedValue || transcription.text;
  } catch (error) {
    console.error('Voice transcription failed:', error);
    // Fall back to browser-based speech recognition
    return null;
  }
}

// ========== 6. Chatbot Integration ==========
export async function askChatbot(message: string, formId?: string, history: any[] = []) {
  try {
    const { data: response } = await featureApis.chatbot.sendMessage(message, formId, history);
    
    // If chatbot suggests an action
    if (response.action) {
      switch (response.action.type) {
        case 'add_field':
          console.log('Chatbot suggests adding field:', response.action.data);
          break;
        case 'apply_validation':
          console.log('Chatbot suggests validation:', response.action.data);
          break;
      }
    }
    
    return response;
  } catch (error) {
    console.error('Chatbot request failed:', error);
    // Return fallback response
    return {
      message: 'Sorry, I\'m having trouble connecting. Please try again.',
      suggestions: [],
    };
  }
}

// Submit feedback
export async function submitChatbotFeedback(messageId: string, isPositive: boolean) {
  try {
    await featureApis.chatbot.submitFeedback(
      messageId,
      isPositive ? 'positive' : 'negative'
    );
  } catch (error) {
    console.error('Feedback submission failed:', error);
  }
}

// ========== 7. Form Submission with Metadata ==========
export async function submitFormWithTracking(
  formId: string,
  data: Record<string, any>,
  metadata: {
    device?: string;
    method?: 'manual' | 'voice' | 'auto';
    duration?: number;
  } = {}
) {
  try {
    const { data: submission } = await featureApis.submission.submit(formId, data, {
      device: metadata.device || getDeviceType(),
      method: metadata.method || 'manual',
      duration: metadata.duration || 0,
    });
    
    console.log('Form submitted:', submission);
    
    // Track completion event
    await featureApis.analytics.trackEvent(formId, 'form_submitted', {
      submissionId: submission.id,
      method: metadata.method,
    });
    
    // Award points if user is authenticated
    try {
      await featureApis.gamification.awardPoints('form_submitted', 20);
    } catch {
      // Ignore if not authenticated
    }
    
    return submission;
  } catch (error) {
    console.error('Form submission failed:', error);
    throw error;
  }
}

// Helper function
function getDeviceType(): string {
  const ua = navigator.userAgent;
  if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
    return 'Tablet';
  }
  if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
    return 'Mobile';
  }
  return 'Desktop';
}

// ========== 8. Gesture Settings Integration ==========
export async function loadGestureSettings() {
  try {
    const { data: settings } = await featureApis.gesture.getSettings();
    return settings;
  } catch (error) {
    console.error('Failed to load gesture settings:', error);
    // Return defaults
    return {
      swipeThreshold: 50,
      longPressDelay: 500,
      pinchSensitivity: 1.0,
      enabled: true,
    };
  }
}

export async function saveGestureSettings(settings: any) {
  try {
    const { data: updated } = await featureApis.gesture.updateSettings(settings);
    return updated;
  } catch (error) {
    console.error('Failed to save gesture settings:', error);
    throw error;
  }
}

// ========== 9. AR Assets Integration ==========
export async function uploadARModel(formId: string, file: File) {
  try {
    const { data: asset } = await featureApis.ar.uploadAsset(formId, file, '3d');
    console.log('AR asset uploaded:', asset);
    return asset;
  } catch (error) {
    console.error('AR upload failed:', error);
    throw error;
  }
}

export async function loadARAssets(formId: string) {
  try {
    const { data: assets } = await featureApis.ar.getAssets(formId);
    return assets;
  } catch (error) {
    console.error('Failed to load AR assets:', error);
    return [];
  }
}

// ========== Complete Example: Form Builder with All Features ==========
export class InteractiveFormBuilder {
  private formId: string;
  private collaborationSocket: FormCollaborationSocket | null = null;
  
  constructor(formId: string) {
    this.formId = formId;
  }
  
  async initialize(userName: string) {
    // 1. Load analytics
    const analytics = await loadFormAnalytics(this.formId);
    console.log('Analytics loaded:', analytics.summary);
    
    // 2. Setup collaboration
    this.collaborationSocket = await setupCollaboration(this.formId, userName);
    
    // 3. Load gamification profile
    const profile = await featureApis.gamification.getProfile();
    console.log('User level:', profile.data.level);
    
    // 4. Load workflows
    const { data: workflows } = await featureApis.workflow.listWorkflows(this.formId);
    console.log('Active workflows:', workflows.filter((w: any) => w.isActive).length);
    
    // 5. Get chatbot suggestions
    const { data: suggestions } = await featureApis.chatbot.getSuggestions(this.formId);
    console.log('Chatbot suggestions:', suggestions);
    
    return {
      analytics,
      profile: profile.data,
      workflows,
      suggestions,
    };
  }
  
  async addField(field: any) {
    // Send field update via WebSocket
    if (this.collaborationSocket) {
      this.collaborationSocket.sendSchemaUpdate({ action: 'add_field', field });
    }
    
    // Award points
    await trackUserAction('field_added', 10);
  }
  
  async saveForm() {
    // Award points
    await trackUserAction('form_saved', 25);
  }
  
  async publishForm() {
    // Award points
    await trackUserAction('form_published', 100);
    
    // Check for achievements
    const { data: profile } = await featureApis.gamification.getProfile();
    if (profile.totalForms === 1) {
      await featureApis.gamification.unlockAchievement('first_form');
    }
  }
  
  async cleanup() {
    // Disconnect WebSocket
    if (this.collaborationSocket) {
      this.collaborationSocket.disconnect();
    }
  }
}

// ========== Usage Example ==========
/*
// Initialize form builder
const builder = new InteractiveFormBuilder('form_123');
await builder.initialize('John Doe');

// Add a field
await builder.addField({
  type: 'text',
  label: 'Full Name',
  required: true,
});

// Save form
await builder.saveForm();

// Publish form
await builder.publishForm();

// Cleanup on unmount
await builder.cleanup();
*/

export default {
  setupCollaboration,
  trackUserAction,
  loadFormAnalytics,
  exportAnalyticsData,
  createAndExecuteWorkflow,
  processVoiceInput,
  askChatbot,
  submitFormWithTracking,
  loadGestureSettings,
  saveGestureSettings,
  uploadARModel,
  loadARAssets,
  InteractiveFormBuilder,
};
