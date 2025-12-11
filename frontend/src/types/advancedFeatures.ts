/**
 * TypeScript types for 8 new advanced features
 */

// ===== Internationalization Types =====

export interface Language {
  id: string;
  code: string;
  name: string;
  native_name: string;
  is_rtl: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FormTranslation {
  id: string;
  form: string;
  language: string;
  language_code?: string;
  language_name?: string;
  title: string;
  description: string | null;
  translated_fields: Record<string, unknown>;
  auto_translated: boolean;
  verified_by_human: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubmissionTranslation {
  id: string;
  submission: string;
  language: string;
  translated_data: Record<string, unknown>;
  created_at: string;
}

// ===== Integration Marketplace Types =====

export type IntegrationCategory = 'crm' | 'email' | 'analytics' | 'payment' | 'storage' | 'communication' | 'productivity' | 'marketing' | 'other';
export type IntegrationAuthType = 'oauth2' | 'api_key' | 'basic_auth' | 'none';

export interface IntegrationProvider {
  id: string;
  name: string;
  slug: string;
  description: string;
  logo_url: string;
  category: IntegrationCategory;
  auth_type: IntegrationAuthType;
  configuration_schema: Record<string, unknown>;
  is_active: boolean;
  popularity_score: number;
  created_at: string;
  updated_at: string;
}

export interface IntegrationConnection {
  id: string;
  user: string;
  provider: string;
  provider_name?: string;
  provider_logo?: string;
  name: string;
  credentials: Record<string, unknown>;
  is_active: boolean;
  last_sync_at: string | null;
  error_count: number;
  last_error: string | null;
  created_at: string;
  updated_at: string;
}

export type WorkflowTrigger = 'on_submission' | 'on_approval' | 'on_schedule' | 'on_status_change';

export interface IntegrationWorkflow {
  id: string;
  user: string;
  form: string;
  provider: string;
  name: string;
  description: string | null;
  trigger: WorkflowTrigger;
  trigger_conditions: Record<string, unknown>;
  actions: Array<{
    type: string;
    configuration: Record<string, unknown>;
  }>;
  field_mapping: Record<string, string>;
  is_active: boolean;
  execution_count: number;
  success_count: number;
  failure_count: number;
  last_executed_at: string | null;
  created_at: string;
  updated_at: string;
}

export type WebhookEvent = 'form_submission' | 'form_created' | 'form_updated' | 'form_deleted';

export interface WebhookEndpoint {
  id: string;
  user: string;
  form: string;
  name: string;
  url: string;
  events: WebhookEvent[];
  headers: Record<string, string>;
  payload_template: string | null;
  is_active: boolean;
  secret_key: string;
  retry_count: number;
  success_count: number;
  failure_count: number;
  last_triggered_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface WebhookLog {
  id: string;
  webhook: string;
  webhook_name?: string;
  event: string;
  payload: Record<string, unknown>;
  response_status: number | null;
  response_body: string | null;
  success: boolean;
  error_message: string | null;
  retry_count: number;
  created_at: string;
}

export interface IntegrationTemplate {
  id: string;
  provider: string;
  provider_name?: string;
  name: string;
  description: string;
  icon: string | null;
  configuration: Record<string, unknown>;
  usage_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ===== Scheduling Types =====

export type ScheduleStatus = 'pending' | 'active' | 'expired' | 'cancelled';

export interface FormSchedule {
  id: string;
  form: string;
  activation_date: string | null;
  expiration_date: string | null;
  timezone: string;
  conditional_activation: Record<string, unknown>;
  status: ScheduleStatus;
  activated_at: string | null;
  expired_at: string | null;
  created_at: string;
  updated_at: string;
}

export type RecurrencePattern = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';

export interface RecurringForm {
  id: string;
  user: string;
  template_form: string;
  template_form_title?: string;
  name: string;
  recurrence_pattern: RecurrencePattern;
  recurrence_config: Record<string, unknown>;
  start_date: string;
  end_date: string | null;
  timezone: string;
  is_active: boolean;
  last_created_at: string | null;
  next_creation_at: string | null;
  forms_created_count: number;
  created_at: string;
  updated_at: string;
}

export type LifecycleEventType = 'activation' | 'expiration' | 'recurring_creation' | 'auto_close' | 'notification_sent';

export interface FormLifecycleEvent {
  id: string;
  form: string;
  event_type: LifecycleEventType;
  triggered_by: string | null;
  triggered_by_email?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

// ===== Theme Types =====

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  error: string;
  success: string;
  warning: string;
  text_primary: string;
  text_secondary: string;
}

export interface ThemeTypography {
  font_family: string;
  font_size_base: number;
  font_size_heading: number;
  font_weight_normal: number;
  font_weight_bold: number;
  line_height: number;
}

export interface ThemeSpacing {
  unit: number;
  padding: Record<string, number>;
  margin: Record<string, number>;
}

export interface Theme {
  id: string;
  user: string;
  user_email?: string;
  name: string;
  description: string | null;
  colors: ThemeColors;
  typography: ThemeTypography;
  spacing: ThemeSpacing;
  borders: Record<string, unknown>;
  shadows: Record<string, unknown>;
  custom_css: string | null;
  custom_js: string | null;
  is_public: boolean;
  downloads_count: number;
  rating_average: number;
  rating_count: number;
  created_at: string;
  updated_at: string;
}

export interface FormTheme {
  id: string;
  form: string;
  theme: string | null;
  theme_name?: string;
  custom_colors: Record<string, string>;
  custom_typography: Record<string, unknown>;
  custom_css: string | null;
  compiled_theme?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ThemeRating {
  id: string;
  theme: string;
  user: string;
  user_email?: string;
  rating: number;
  review: string | null;
  created_at: string;
  updated_at: string;
}

export interface BrandGuideline {
  id: string;
  user: string;
  name: string;
  primary_color: string;
  secondary_color: string;
  logo_url: string | null;
  font_family: string;
  custom_rules: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

// ===== Security Types =====

export type TwoFactorMethod = 'totp' | 'sms' | 'email';

export interface TwoFactorAuth {
  id: string;
  user: string;
  method: TwoFactorMethod;
  is_enabled: boolean;
  qr_code_url?: string;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
}

export type SSOProtocol = 'saml2' | 'oauth2' | 'openid';

export interface SSOProvider {
  id: string;
  name: string;
  protocol: SSOProtocol;
  metadata_url: string | null;
  entity_id: string | null;
  sso_url: string | null;
  client_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type PrivacyRequestType = 'export' | 'delete' | 'rectify';
export type PrivacyRequestStatus = 'pending' | 'verified' | 'processing' | 'completed' | 'rejected';

export interface DataPrivacyRequest {
  id: string;
  email: string;
  request_type: PrivacyRequestType;
  status: PrivacyRequestStatus;
  description: string | null;
  verified_at: string | null;
  processed_by: string | null;
  processed_at: string | null;
  export_file_url: string | null;
  export_expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConsentTracking {
  id: string;
  submission: string;
  consent_type: string;
  consent_text: string;
  consented: boolean;
  ip_address: string | null;
  user_agent: string | null;
  revoked_at: string | null;
  created_at: string;
}

export type AuditAction = 'login' | 'logout' | 'form_create' | 'form_update' | 'form_delete' | 'submission_view' | 'data_export' | 'permission_change' | 'security_event';

export interface SecurityAuditLog {
  id: string;
  user: string | null;
  user_email?: string;
  action: AuditAction;
  resource_type: string | null;
  resource_id: string | null;
  ip_address: string | null;
  user_agent: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export type AccessControlType = 'whitelist' | 'blacklist';

export interface IPAccessControl {
  id: string;
  form: string;
  type: AccessControlType;
  ip_addresses: string[];
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ===== Collaboration Types =====

export type CollaboratorRole = 'viewer' | 'editor' | 'admin';

export interface FormCollaborator {
  id: string;
  form: string;
  user: string;
  user_email?: string;
  invited_by: string;
  invited_by_email?: string;
  role: CollaboratorRole;
  permissions: string[];
  invitation_accepted: boolean;
  last_active_at: string | null;
  created_at: string;
}

export interface FormEditSession {
  id: string;
  form: string;
  user: string;
  user_email?: string;
  user_name?: string;
  session_id: string;
  cursor_position: Record<string, unknown>;
  is_active: boolean;
  started_at: string;
  last_activity_at: string;
}

export type ChangeType = 'field_add' | 'field_edit' | 'field_delete' | 'field_move' | 'setting_change' | 'other';

export interface FormChange {
  id: string;
  form: string;
  user: string;
  user_email?: string;
  session: string;
  change_type: ChangeType;
  change_data: Record<string, unknown>;
  created_at: string;
}

export interface FormComment {
  id: string;
  form: string;
  user: string;
  user_email?: string;
  user_name?: string;
  parent_comment: string | null;
  field_id: string | null;
  content: string;
  is_resolved: boolean;
  resolved_by: string | null;
  resolved_by_email?: string;
  resolved_at: string | null;
  replies?: FormComment[];
  created_at: string;
  updated_at: string;
}

export type ReviewStatus = 'pending' | 'approved' | 'rejected' | 'changes_requested';

export interface FormReview {
  id: string;
  workflow: string;
  reviewer: string;
  reviewer_email?: string;
  status: ReviewStatus;
  comments: string | null;
  reviewed_at: string;
  created_at: string;
}

export interface FormReviewWorkflow {
  id: string;
  form: string;
  submitted_by: string;
  submitted_by_email?: string;
  reviewers: string[];
  status: ReviewStatus;
  required_approvals: number;
  current_approvals: number;
  reviews: FormReview[];
  submitted_at: string;
  created_at: string;
  updated_at: string;
}

// ===== Predictive Types =====

export type PredictionType = 'lookup' | 'calculation' | 'pattern' | 'ml_model';

export interface FieldPrediction {
  id: string;
  form: string;
  field_name: string;
  prediction_type: PredictionType;
  prediction_rules: Record<string, unknown>;
  ml_model_endpoint: string | null;
  accuracy_rate: number;
  usage_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SmartDefault {
  id: string;
  form: string;
  field_name: string;
  default_value: unknown;
  conditions: Record<string, unknown>;
  priority: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CompletionPrediction {
  id: string;
  submission: string;
  predicted_completion_time: number;
  predicted_drop_off_point: string | null;
  confidence_score: number;
  actual_completed: boolean;
  created_at: string;
}

export interface ProgressiveDisclosure {
  id: string;
  form: string;
  field_name: string;
  trigger_conditions: Record<string, unknown>;
  revealed_fields: string[];
  animation_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ===== Mobile Types =====

export interface MobileOptimization {
  id: string;
  form: string;
  one_field_per_screen: boolean;
  large_tap_targets: boolean;
  auto_advance_fields: boolean;
  numeric_keyboard_for_numbers: boolean;
  simplified_layout: boolean;
  reduced_animations: boolean;
  offline_mode_enabled: boolean;
  pwa_manifest: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface GeolocationField {
  id: string;
  submission: string;
  field_name: string;
  latitude: number;
  longitude: number;
  accuracy: number | null;
  address: string | null;
  created_at: string;
}

export type OfflineSubmissionStatus = 'pending' | 'syncing' | 'synced' | 'failed';

export interface OfflineSubmission {
  id: string;
  user: string | null;
  form: string;
  data: Record<string, unknown>;
  status: OfflineSubmissionStatus;
  sync_attempts: number;
  last_sync_attempt: string | null;
  error_message: string | null;
  synced_submission_id: string | null;
  synced_at: string | null;
  created_at: string;
}

export interface PushNotificationSubscription {
  id: string;
  user: string;
  endpoint: string;
  p256dh_key: string;
  auth_key: string;
  device_info: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type NotificationType = 'form_shared' | 'submission_received' | 'comment_added' | 'review_requested' | 'form_published' | 'other';

export interface FormNotification {
  id: string;
  user: string;
  form: string | null;
  type: NotificationType;
  title: string;
  body: string;
  data: Record<string, unknown>;
  icon: string | null;
  url: string | null;
  sent_at: string | null;
  delivered_at: string | null;
  clicked_at: string | null;
  created_at: string;
}
