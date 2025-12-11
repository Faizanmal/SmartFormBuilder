/**
 * API Client for FormForge
 */
import apiClient from '@/lib/api';
import type {
  User,
  Form,
  FormSchema,
  Submission,
  FormTemplate,
  Integration,
  LoginCredentials,
  RegisterData,
  FormGenerateRequest,
  Analytics,
  AnalyticsFilters,
  AuthTokens,
  FormDraft,
  FormVariant,
  ABTest
} from '@/types';

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await apiClient.post('/auth/login/', credentials);
    return response.data;
  },

  register: async (data: RegisterData): Promise<{ user: User; tokens: AuthTokens }> => {
    const response = await apiClient.post('/users/register/', data);
    return response.data;
  },

  me: async (): Promise<User> => {
    const response = await apiClient.get('/users/me/');
    return response.data;
  },

  refreshToken: async (refresh: string): Promise<{ access: string }> => {
    const response = await apiClient.post('/auth/refresh/', { refresh });
    return response.data;
  },
};

// Forms API
export const formsApi = {
  list: async (): Promise<Form[]> => {
    const response = await apiClient.get('/forms/');
    return response.data.results || response.data;
  },

  get: async (id: string): Promise<Form> => {
    const response = await apiClient.get(`/forms/${id}/`);
    return response.data;
  },

  getBySlug: async (slug: string): Promise<Form> => {
    const response = await apiClient.get(`/public/form/${slug}/`);
    return response.data;
  },

  create: async (data: {
    title?: string;
    description?: string;
    schema_json?: FormSchema;
    prompt?: string;
    context?: string;
  }): Promise<Form> => {
    const response = await apiClient.post('/forms/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Form>): Promise<Form> => {
    const response = await apiClient.patch(`/forms/${id}/`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/forms/${id}/`);
  },

  publish: async (id: string): Promise<{ status: string; published_at: string }> => {
    const response = await apiClient.post(`/forms/${id}/publish/`);
    return response.data;
  },

  getEmbedCode: async (id: string): Promise<{ embed_code: string; hosted_link: string; slug: string }> => {
    const response = await apiClient.get(`/forms/${id}/embed/`);
    return response.data;
  },

  getAnalytics: async (id: string, filters?: AnalyticsFilters): Promise<Analytics> => {
    const response = await apiClient.get(`/forms/${id}/analytics/`, { params: filters });
    return response.data;
  },

  generate: async (request: FormGenerateRequest): Promise<FormSchema> => {
    const response = await apiClient.post('/generate/', request);
    return response.data;
  },

  // Version history
  getVersions: async (id: string): Promise<any[]> => {
    const response = await apiClient.get(`/forms/${id}/versions/`);
    return response.data;
  },

  revertToVersion: async (id: string, versionId: string): Promise<Form> => {
    const response = await apiClient.post(`/forms/${id}/revert/`, { version_id: versionId });
    return response.data;
  },
};

// Submissions API
export const submissionsApi = {
  list: async (formId: string): Promise<Submission[]> => {
    const response = await apiClient.get(`/forms/${formId}/submissions/`);
    return response.data.results || response.data;
  },

  get: async (formId: string, submissionId: string): Promise<Submission> => {
    const response = await apiClient.get(`/forms/${formId}/submissions/${submissionId}/`);
    return response.data;
  },

  // Public submission (no auth)
  submit: async (slug: string, payload: Record<string, any>): Promise<{ id: string; message: string; redirect: string }> => {
    const response = await apiClient.post(`/public/submit/${slug}/`, { payload });
    return response.data;
  },
};

// Public Form API (no auth required)
export const publicFormApi = {
  // Get form by slug for public rendering
  get: async (slug: string): Promise<Form> => {
    const response = await apiClient.get(`/public/form/${slug}/`);
    return response.data;
  },
};

// Templates API
export const templatesApi = {
  list: async (category?: string): Promise<FormTemplate[]> => {
    const params = category ? { category } : {};
    const response = await apiClient.get('/templates/', { params });
    return response.data.results || response.data;
  },

  get: async (id: string): Promise<FormTemplate> => {
    const response = await apiClient.get(`/templates/${id}/`);
    return response.data;
  },

  use: async (id: string): Promise<Form> => {
    const response = await apiClient.post(`/templates/${id}/use/`);
    return response.data;
  },
};

// Integrations API
export const integrationsApi = {
  list: async (formId?: string): Promise<Integration[]> => {
    const url = formId ? `/forms/${formId}/integrations/` : '/integrations/';
    const response = await apiClient.get(url);
    return response.data.results || response.data;
  },

  create: async (data: {
    form: string;
    integration_type: string;
    config: Record<string, any>;
    is_active?: boolean;
  }): Promise<Integration> => {
    const response = await apiClient.post('/integrations/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Integration>): Promise<Integration> => {
    const response = await apiClient.patch(`/integrations/${id}/`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/integrations/${id}/`);
  },

  test: async (id: string): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post(`/integrations/${id}/test/`);
    return response.data;
  },

  initiateGoogleOAuth: async (formId: string): Promise<{ authorization_url: string; state: string }> => {
    const response = await apiClient.get('/integrations/google_sheets_auth/', {
      params: { form_id: formId }
    });
    return response.data;
  },

  completeGoogleOAuth: async (data: { code: string; state: string; form_id: string }): Promise<Integration> => {
    const response = await apiClient.post('/integrations/google_sheets_connect/', data);
    return response.data;
  },

  getWebhookLogs: async (integrationId?: string): Promise<any[]> => {
    const url = integrationId 
      ? `/integrations/webhook-logs/?integration=${integrationId}`
      : '/integrations/webhook-logs/';
    const response = await apiClient.get(url);
    return response.data.results || response.data;
  },

  retryWebhook: async (logId: string): Promise<{ status: string }> => {
    const response = await apiClient.post(`/integrations/webhook-logs/${logId}/retry/`);
    return response.data;
  },
};

// Form Drafts API - Save and Resume
export const draftsApi = {
  // Get draft by token (public)
  get: async (token: string): Promise<FormDraft> => {
    const response = await apiClient.get(`/public/draft/token/${token}/`);
    return response.data;
  },

  // Save or update draft (public)
  save: async (slug: string, data: {
    payload: Record<string, any>;
    current_step?: number;
    email?: string;
    draft_token?: string;
  }): Promise<FormDraft> => {
    const response = await apiClient.post(`/public/draft/${slug}/`, data);
    return response.data;
  },

  // Send resume link via email
  sendResumeLink: async (token: string, email: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/public/draft/token/${token}/send-link/`, { email });
    return response.data;
  },
};

// A/B Testing API
export const abTestApi = {
  // List all A/B tests for a form
  list: async (formId: string): Promise<ABTest[]> => {
    const response = await apiClient.get(`/forms/${formId}/ab-tests/`);
    return response.data.results || response.data;
  },

  // Get single A/B test
  get: async (formId: string, testId: string): Promise<ABTest> => {
    const response = await apiClient.get(`/forms/${formId}/ab-tests/${testId}/`);
    return response.data;
  },

  // Create A/B test
  create: async (formId: string, data: { name: string; description?: string }): Promise<ABTest> => {
    const response = await apiClient.post(`/forms/${formId}/ab-tests/`, data);
    return response.data;
  },

  // Start A/B test
  start: async (formId: string, testId: string): Promise<ABTest> => {
    const response = await apiClient.post(`/forms/${formId}/ab-tests/${testId}/start/`);
    return response.data;
  },

  // End A/B test
  end: async (formId: string, testId: string): Promise<ABTest> => {
    const response = await apiClient.post(`/forms/${formId}/ab-tests/${testId}/end/`);
    return response.data;
  },

  // Create variant
  createVariant: async (formId: string, data: {
    name: string;
    schema_json: FormSchema;
    traffic_percentage?: number;
  }): Promise<FormVariant> => {
    const response = await apiClient.post(`/forms/${formId}/variants/`, data);
    return response.data;
  },

  // Update variant
  updateVariant: async (formId: string, variantId: string, data: Partial<FormVariant>): Promise<FormVariant> => {
    const response = await apiClient.patch(`/forms/${formId}/variants/${variantId}/`, data);
    return response.data;
  },

  // Delete variant
  deleteVariant: async (formId: string, variantId: string): Promise<void> => {
    await apiClient.delete(`/forms/${formId}/variants/${variantId}/`);
  },
};
