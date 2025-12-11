/**
 * API Service for 8 new advanced features
 */

import { 
  Language, FormTranslation, SubmissionTranslation,
  IntegrationProvider, IntegrationConnection, IntegrationWorkflow, WebhookEndpoint, WebhookLog, IntegrationTemplate,
  FormSchedule, RecurringForm, FormLifecycleEvent,
  Theme, FormTheme, ThemeRating, BrandGuideline,
  TwoFactorAuth, SSOProvider, DataPrivacyRequest, ConsentTracking, SecurityAuditLog, IPAccessControl,
  FormCollaborator, FormEditSession, FormChange, FormComment, FormReviewWorkflow, FormReview,
  FieldPrediction, SmartDefault, CompletionPrediction, ProgressiveDisclosure,
  MobileOptimization, GeolocationField, OfflineSubmission, PushNotificationSubscription, FormNotification
} from '@/types/advancedFeatures';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Helper function for API calls
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options?.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// ===== Internationalization API =====

export const i18nAPI = {
  getLanguages: () => apiCall<Language[]>('/languages/'),
  
  getFormTranslations: (formId?: string) => 
    apiCall<FormTranslation[]>(formId ? `/form-translations/?form=${formId}` : '/form-translations/'),
  
  createFormTranslation: (data: Partial<FormTranslation>) =>
    apiCall<FormTranslation>('/form-translations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  autoTranslateForm: (formId: string, targetLanguage: string) =>
    apiCall<unknown>('/form-translations/auto_translate/', {
      method: 'POST',
      body: JSON.stringify({ form_id: formId, target_language: targetLanguage }),
    }),
  
  getSubmissionTranslations: (submissionId: string) =>
    apiCall<SubmissionTranslation[]>(`/submission-translations/?submission=${submissionId}`),
};

// ===== Integration Marketplace API =====

export const integrationAPI = {
  getProviders: (category?: string) =>
    apiCall<IntegrationProvider[]>(category ? `/integration-providers/?category=${category}` : '/integration-providers/'),
  
  getConnections: () =>
    apiCall<IntegrationConnection[]>('/integration-connections/'),
  
  createConnection: (data: Partial<IntegrationConnection>) =>
    apiCall<IntegrationConnection>('/integration-connections/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  testConnection: (connectionId: string) =>
    apiCall<unknown>(`/integration-connections/${connectionId}/test_connection/`, {
      method: 'POST',
    }),
  
  refreshToken: (connectionId: string) =>
    apiCall<unknown>(`/integration-connections/${connectionId}/refresh_token/`, {
      method: 'POST',
    }),
  
  getWorkflows: (formId?: string) =>
    apiCall<IntegrationWorkflow[]>(formId ? `/integration-workflows/?form=${formId}` : '/integration-workflows/'),
  
  createWorkflow: (data: Partial<IntegrationWorkflow>) =>
    apiCall<IntegrationWorkflow>('/integration-workflows/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  executeWorkflow: (workflowId: string, submissionId: string) =>
    apiCall<unknown>(`/integration-workflows/${workflowId}/execute/`, {
      method: 'POST',
      body: JSON.stringify({ submission_id: submissionId }),
    }),
  
  getWebhooks: (formId?: string) =>
    apiCall<WebhookEndpoint[]>(formId ? `/webhook-endpoints/?form=${formId}` : '/webhook-endpoints/'),
  
  createWebhook: (data: Partial<WebhookEndpoint>) =>
    apiCall<WebhookEndpoint>('/webhook-endpoints/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  testWebhook: (webhookId: string, testData: unknown) =>
    apiCall<unknown>(`/webhook-endpoints/${webhookId}/test/`, {
      method: 'POST',
      body: JSON.stringify({ test_data: testData }),
    }),
  
  getWebhookLogs: (webhookId?: string) =>
    apiCall<WebhookLog[]>(webhookId ? `/webhook-logs/?webhook=${webhookId}` : '/webhook-logs/'),
  
  getTemplates: () =>
    apiCall<IntegrationTemplate[]>('/integration-templates/'),
  
  useTemplate: (templateId: string, formId: string) =>
    apiCall<IntegrationWorkflow>(`/integration-templates/${templateId}/use/`, {
      method: 'POST',
      body: JSON.stringify({ form_id: formId }),
    }),
};

// ===== Scheduling API =====

export const schedulingAPI = {
  getSchedules: (formId?: string) =>
    apiCall<FormSchedule[]>(formId ? `/form-schedules/?form=${formId}` : '/form-schedules/'),
  
  createSchedule: (data: Partial<FormSchedule>) =>
    apiCall<FormSchedule>('/form-schedules/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  updateSchedule: (scheduleId: string, data: Partial<FormSchedule>) =>
    apiCall<FormSchedule>(`/form-schedules/${scheduleId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  activateNow: (scheduleId: string) =>
    apiCall<unknown>(`/form-schedules/${scheduleId}/activate_now/`, {
      method: 'POST',
    }),
  
  getRecurringForms: () =>
    apiCall<RecurringForm[]>('/recurring-forms/'),
  
  createRecurringForm: (data: Partial<RecurringForm>) =>
    apiCall<RecurringForm>('/recurring-forms/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getLifecycleEvents: (formId?: string) =>
    apiCall<FormLifecycleEvent[]>(formId ? `/lifecycle-events/?form=${formId}` : '/lifecycle-events/'),
};

// ===== Theme API =====

export const themeAPI = {
  getThemes: () =>
    apiCall<Theme[]>('/themes/'),
  
  getTheme: (themeId: string) =>
    apiCall<Theme>(`/themes/${themeId}/`),
  
  createTheme: (data: Partial<Theme>) =>
    apiCall<Theme>('/themes/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  updateTheme: (themeId: string, data: Partial<Theme>) =>
    apiCall<Theme>(`/themes/${themeId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  deleteTheme: (themeId: string) =>
    apiCall<void>(`/themes/${themeId}/`, {
      method: 'DELETE',
    }),
  
  validateTheme: (themeId: string) =>
    apiCall<unknown>(`/themes/${themeId}/validate/`, {
      method: 'POST',
    }),
  
  cloneTheme: (themeId: string) =>
    apiCall<Theme>(`/themes/${themeId}/clone/`, {
      method: 'POST',
    }),
  
  getFormTheme: (formId: string) =>
    apiCall<FormTheme>(`/form-themes/?form=${formId}`),
  
  setFormTheme: (data: Partial<FormTheme>) =>
    apiCall<FormTheme>('/form-themes/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  rateTheme: (data: Partial<ThemeRating>) =>
    apiCall<ThemeRating>('/theme-ratings/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getBrandGuidelines: () =>
    apiCall<BrandGuideline[]>('/brand-guidelines/'),
  
  createBrandGuideline: (data: Partial<BrandGuideline>) =>
    apiCall<BrandGuideline>('/brand-guidelines/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ===== Security API =====

export const securityAPI = {
  setup2FA: (method: 'totp' | 'sms' | 'email') =>
    apiCall<TwoFactorAuth>('/two-factor-auth/', {
      method: 'POST',
      body: JSON.stringify({ method }),
    }),
  
  verify2FA: (authId: string, code: string) =>
    apiCall<unknown>(`/two-factor-auth/${authId}/verify/`, {
      method: 'POST',
      body: JSON.stringify({ code }),
    }),
  
  disable2FA: (authId: string) =>
    apiCall<unknown>(`/two-factor-auth/${authId}/disable/`, {
      method: 'POST',
    }),
  
  getSSOProviders: () =>
    apiCall<SSOProvider[]>('/sso-providers/'),
  
  createPrivacyRequest: (data: Partial<DataPrivacyRequest>) =>
    apiCall<DataPrivacyRequest>('/privacy-requests/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  verifyPrivacyRequest: (requestId: string, token: string) =>
    apiCall<unknown>(`/privacy-requests/${requestId}/verify/`, {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),
  
  getAuditLogs: () =>
    apiCall<SecurityAuditLog[]>('/security-audit-logs/'),
  
  getIPAccessControls: (formId?: string) =>
    apiCall<IPAccessControl[]>(formId ? `/ip-access-controls/?form=${formId}` : '/ip-access-controls/'),
  
  createIPAccessControl: (data: Partial<IPAccessControl>) =>
    apiCall<IPAccessControl>('/ip-access-controls/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ===== Collaboration API =====

export const collaborationAPI = {
  getCollaborators: (formId: string) =>
    apiCall<FormCollaborator[]>(`/form-collaborators/?form=${formId}`),
  
  inviteCollaborator: (data: Partial<FormCollaborator>) =>
    apiCall<FormCollaborator>('/form-collaborators/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  acceptInvitation: (collaboratorId: string) =>
    apiCall<unknown>(`/form-collaborators/${collaboratorId}/accept/`, {
      method: 'POST',
    }),
  
  getActiveSessions: (formId: string) =>
    apiCall<FormEditSession[]>(`/form-edit-sessions/?form=${formId}`),
  
  getChanges: (formId: string) =>
    apiCall<FormChange[]>(`/form-changes/?form=${formId}`),
  
  getComments: (formId: string) =>
    apiCall<FormComment[]>(`/form-comments/?form=${formId}`),
  
  createComment: (data: Partial<FormComment>) =>
    apiCall<FormComment>('/form-comments/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  resolveComment: (commentId: string) =>
    apiCall<unknown>(`/form-comments/${commentId}/resolve/`, {
      method: 'POST',
    }),
  
  getReviewWorkflows: (formId?: string) =>
    apiCall<FormReviewWorkflow[]>(formId ? `/form-review-workflows/?form=${formId}` : '/form-review-workflows/'),
  
  createReviewWorkflow: (data: Partial<FormReviewWorkflow>) =>
    apiCall<FormReviewWorkflow>('/form-review-workflows/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  submitReview: (data: Partial<FormReview>) =>
    apiCall<FormReview>('/form-reviews/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ===== Predictive API =====

export const predictiveAPI = {
  getPredictions: (formId: string) =>
    apiCall<FieldPrediction[]>(`/field-predictions/?form=${formId}`),
  
  createPrediction: (data: Partial<FieldPrediction>) =>
    apiCall<FieldPrediction>('/field-predictions/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  predictFieldValue: (formId: string, fieldName: string, userContext: unknown) =>
    apiCall<unknown>('/field-predictions/predict/', {
      method: 'POST',
      body: JSON.stringify({ form_id: formId, field_name: fieldName, user_context: userContext }),
    }),
  
  getSmartDefaults: (formId: string) =>
    apiCall<SmartDefault[]>(`/smart-defaults/?form=${formId}`),
  
  createSmartDefault: (data: Partial<SmartDefault>) =>
    apiCall<SmartDefault>('/smart-defaults/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getProgressiveDisclosure: (formId: string) =>
    apiCall<ProgressiveDisclosure[]>(`/progressive-disclosure/?form=${formId}`),
  
  createProgressiveDisclosure: (data: Partial<ProgressiveDisclosure>) =>
    apiCall<ProgressiveDisclosure>('/progressive-disclosure/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ===== Mobile API =====

export const mobileAPI = {
  getMobileOptimization: (formId: string) =>
    apiCall<MobileOptimization>(`/mobile-optimizations/?form=${formId}`),
  
  setMobileOptimization: (data: Partial<MobileOptimization>) =>
    apiCall<MobileOptimization>('/mobile-optimizations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getOfflineSubmissions: () =>
    apiCall<OfflineSubmission[]>('/offline-submissions/'),
  
  createOfflineSubmission: (data: Partial<OfflineSubmission>) =>
    apiCall<OfflineSubmission>('/offline-submissions/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  syncOfflineSubmission: (submissionId: string) =>
    apiCall<unknown>(`/offline-submissions/${submissionId}/sync/`, {
      method: 'POST',
    }),
  
  subscribeToPush: (data: Partial<PushNotificationSubscription>) =>
    apiCall<PushNotificationSubscription>('/push-subscriptions/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getNotifications: () =>
    apiCall<FormNotification[]>('/form-notifications/'),
  
  sendNotification: (userId: string, title: string, body: string, data?: unknown) =>
    apiCall<unknown>('/form-notifications/send/', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, title, body, data }),
    }),
};
