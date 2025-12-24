/**
 * Type definitions for FormForge
 */

export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  plan: 'free' | 'starter' | 'pro' | 'business';
  created_at: string;
  updated_at: string;
}

export interface FieldValidation {
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: string;
  required?: boolean;
  accept?: string; // For file fields (e.g., 'image/*,.pdf')
  maxSize?: number; // Max file size in bytes
}

export interface ConditionalRule {
  id: string;
  fieldId: string; // The field to watch
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'is_empty' | 'is_not_empty';
  value: string;
  action: 'show' | 'hide' | 'require' | 'unrequire';
}

export interface FieldOption {
  label: string;
  value: string;
}

export interface FormField {
  id: string;
  type: 'text' | 'email' | 'phone' | 'textarea' | 'number' | 'date' | 'time' | 
        'select' | 'multiselect' | 'checkbox' | 'radio' | 'file' | 'url' | 'payment' |
        'slider' | 'rating' | 'signature' | 'calculated' | 'address' | 'heading' | 'divider';
  label: string;
  placeholder?: string;
  required?: boolean;
  validation?: FieldValidation;
  options?: FieldOption[];
  help?: string;
  
  // Payment field specific
  amount?: number;  // Amount in cents
  currency?: string;  // USD, EUR, etc.
  
  // Slider field specific
  sliderMin?: number;
  sliderMax?: number;
  sliderStep?: number;
  showValue?: boolean;
  
  // Rating field specific
  maxRating?: number;  // Default 5
  ratingIcon?: 'star' | 'heart' | 'thumbsup';
  
  // Calculated field specific
  formula?: string;  // e.g., "{field_1} * {field_2} + 100"
  displayFormat?: 'number' | 'currency' | 'percentage';
  
  // File field specific
  allowMultiple?: boolean;
  maxFiles?: number;
  
  // Address field specific
  includeCountry?: boolean;
  includeZip?: boolean;
  
  // Heading/Divider specific
  headingLevel?: 'h1' | 'h2' | 'h3' | 'h4';
  
  // Step assignment for multi-step forms
  step?: number;
  
  // Conditional logic for this field
  conditionalRules?: ConditionalRule[];
}

export interface ConditionalLogic {
  if: {
    field: string;
    operator: 'equals' | 'in' | 'contains' | 'gte' | 'lte';
    value: unknown;
  };
  show?: string[];
  hide?: string[];
}

export interface FormSettings {
  consent_text?: string;
  redirect?: string;
  integrations?: {
    google_sheets?: boolean;
    webhook?: boolean;
    email?: boolean;
    stripe?: boolean;
  };
  // Multi-step form settings
  multiStep?: boolean;
  steps?: FormStep[];
  showProgressBar?: boolean;
  allowSkip?: boolean;
  // Save & Resume settings
  allowSaveAndResume?: boolean;
  resumeExpirationDays?: number;
}

export interface FormStep {
  id: string;
  title: string;
  description?: string;
  fields: string[]; // Array of field IDs in this step
}

export interface FormSchema {
  title: string;
  description: string;
  fields: FormField[];
  logic?: ConditionalLogic[];
  settings?: FormSettings;
}

export interface Form {
  id: string;
  title: string;
  slug: string;
  description: string;
  schema_json: FormSchema;
  settings_json: FormSettings;
  published_at: string | null;
  is_active: boolean;
  views_count: number;
  submissions_count: number;
  conversion_rate: number;
  created_at: string;
  updated_at: string;
}

// Form draft for save & resume functionality
export interface FormDraft {
  id: string;
  form: string;
  form_slug?: string;
  draft_token: string;
  payload_json: Record<string, unknown>;
  current_step: number;
  email?: string;
  expires_at: string;
  is_expired: boolean;
  created_at: string;
  updated_at: string;
}

export interface Submission {
  id: string;
  form: string;
  payload_json: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
  processed_at: string | null;
  payment_status?: 'pending' | 'paid' | 'failed' | 'refunded';
  payment_id?: string;
  payment_amount?: number;
  created_at: string;
}

export interface FormTemplate {
  id: string;
  name: string;
  description: string;
  category: 'photography' | 'health' | 'fitness' | 'real_estate' | 'consulting' | 'events' | 'general';
  schema_json: FormSchema;
  thumbnail_url?: string;
  usage_count: number;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface Integration {
  id: string;
  integration_type: 'google_sheets' | 'notion' | 'webhook' | 'stripe' | 'email' | 'zapier' | 'slack';
  name: string;
  config: Record<string, unknown>;
  is_active: boolean;
  last_triggered_at: string | null;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export interface FormGenerateRequest {
  prompt: string;
  context?: string;
}

export interface Analytics {
  views: number;
  submissions: number;
  conversion_rate: number;
  recent_submissions: number;
  last_submission: string | null;
  // Enhanced analytics
  submissions_by_day?: { date: string; count: number }[];
  field_completion?: { field_id: string; field_label: string; completion_rate: number }[];
  avg_completion_time?: number; // in seconds
  drop_off_rates?: { step: number; rate: number }[];
}

export interface AnalyticsFilters {
  date_from?: string;
  date_to?: string;
  step?: number;
}

// A/B Testing types
export interface FormVariant {
  id: string;
  form_id: string;
  name: string;
  schema_json: FormSchema;
  traffic_percentage: number;
  views_count: number;
  submissions_count: number;
  conversion_rate: number;
  is_active: boolean;
  created_at: string;
}

export interface ABTest {
  id: string;
  form_id: string;
  name: string;
  status: 'draft' | 'running' | 'completed';
  variants: FormVariant[];
  winner_variant_id?: string;
  started_at?: string;
  ended_at?: string;
  created_at: string;
}
