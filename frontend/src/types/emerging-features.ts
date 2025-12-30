/**
 * TypeScript types for all emerging technology features
 */

// ============================================================================
// AI & EMERGING TECH TYPES
// ============================================================================

export interface AILayoutSuggestion {
  id: string;
  form: string;
  trigger_type: 'manual' | 'scheduled' | 'auto';
  analysis_data: {
    heatmap?: Record<string, unknown>;
    dropoff_points?: string[];
    engagement_metrics?: Record<string, unknown>;
  };
  suggestions: Array<{
    type: string;
    description: string;
    confidence: number;
    impact_estimate: string;
  }>;
  status: 'pending' | 'analyzing' | 'completed' | 'error';
  ai_provider: 'openai' | 'anthropic' | 'google';
  created_at: string;
}

export interface ConversationalAIConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  ai_provider: 'openai' | 'claude' | 'gemini';
  model: string;
  personality: string;
  context_instructions: string;
  greeting_message: string;
  fallback_behavior: 'redirect_to_form' | 'show_error' | 'escalate_to_human';
  created_at: string;
}

export interface ConversationSession {
  id: string;
  form: string;
  config: string;
  session_id: string;
  user?: string;
  status: 'active' | 'completed' | 'abandoned' | 'error';
  collected_data: Record<string, unknown>;
  started_at: string;
  completed_at?: string;
  is_active: boolean;
  participants: unknown[];
  change_history: unknown[];
  crdt_enabled: boolean;
  conflict_resolution_strategy: string;
}

export interface AIPersonalization {
  id: string;
  form: string;
  user?: string;
  segment: string;
  rules: Array<{
    condition: unknown;
    modifications: unknown;
  }>;
  is_active: boolean;
}

export interface HeatmapAnalysis {
  id: string;
  form: string;
  session_count: number;
  heatmap_data: {
    clicks: Array<{ x: number; y: number; intensity: number }>;
    scrollDepth: Record<string, number>;
    fieldInteractions: Record<string, number>;
  };
  insights: Record<string, unknown>;
  created_at: string;
}

// ============================================================================
// VOICE & MULTIMODAL TYPES
// ============================================================================

export interface VoiceFormConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  transcription_engine: 'whisper' | 'google' | 'azure' | 'aws';
  language: string;
  wake_word?: string;
  auto_submit: boolean;
  voice_feedback: boolean;
  created_at: string;
}

export interface VoiceInteraction {
  id: string;
  form: string;
  session_id: string;
  audio_url: string;
  transcription: string;
  confidence_score: number;
  field_mappings: Record<string, unknown>;
  created_at: string;
}

export interface MultimodalInputConfig {
  id: string;
  form: string;
  camera_enabled: boolean;
  qr_scanner_enabled: boolean;
  barcode_scanner_enabled: boolean;
  ocr_enabled: boolean;
  nfc_enabled: boolean;
  ar_preview_enabled: boolean;
}

export interface OCRExtraction {
  id: string;
  form: string;
  image_url: string;
  extracted_text: string;
  extracted_data: Record<string, unknown>;
  confidence_score: number;
  ocr_engine: 'google_vision' | 'azure' | 'aws_textract';
  created_at: string;
}

export interface ARPreviewConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  preview_type: '3d_product' | 'furniture' | 'vehicle' | 'custom';
  model_url: string;
  scale: number;
  ar_instructions: string;
}

// ============================================================================
// SECURITY & COMPLIANCE TYPES
// ============================================================================

export interface ZeroKnowledgeEncryption {
  id: string;
  form: string;
  is_enabled: boolean;
  encryption_algorithm: 'AES-256-GCM' | 'ChaCha20-Poly1305';
  key_derivation: 'PBKDF2' | 'Argon2' | 'scrypt';
  client_side_only: boolean;
}

export interface BlockchainConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  chain_type: 'ethereum' | 'polygon' | 'hyperledger' | 'private';
  smart_contract_address?: string;
  audit_events: string[];
}

export interface ThreatDetectionConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  sql_injection_detection: boolean;
  xss_detection: boolean;
  bot_detection: boolean;
  rate_limiting: boolean;
  threat_level_threshold: 'low' | 'medium' | 'high';
}

export interface ComplianceFramework {
  id: string;
  code: 'GDPR' | 'CCPA' | 'HIPAA' | 'SOC2' | 'ISO27001';
  name: string;
  description: string;
  is_active: boolean;
  requirements: unknown[];
}

export interface AdvancedComplianceScan {
  id: string;
  form: string;
  framework: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result: 'compliant' | 'non_compliant' | 'partial' | 'needs_review';
  overall_score: number;
  checks_passed: number;
  checks_failed: number;
  issues: unknown[];
  recommendations: unknown[];
  created_at: string;
}

// ============================================================================
// INTEGRATION & AUTOMATION TYPES
// ============================================================================

export interface WebhookTransformer {
  id: string;
  name: string;
  input_format: 'json' | 'xml' | 'form_data' | 'csv';
  output_format: 'json' | 'xml' | 'form_data' | 'csv';
  transformation_template: string;
  test_payload?: unknown;
  target_url: string;
  is_active: boolean;
  http_method: string;
  trigger_events: string[];
  field_mappings: Record<string, unknown>;
}

export interface MarketplaceIntegration {
  id: string;
  name: string;
  category: string;
  description: string;
  logo_url: string;
  developer: string;
  pricing_model: 'free' | 'freemium' | 'paid';
  is_published: boolean;
  is_verified: boolean;
  install_count: number;
  installs_count: number;
  rating_average: number;
  rating: number;
  is_active: boolean;
  version: string;
}

export interface SSOConfiguration {
  id: string;
  form: string;
  provider_type: 'saml' | 'oauth' | 'oidc' | 'ldap' | 'ad';
  provider_name: string;
  is_enabled: boolean;
  client_id?: string;
  metadata_url?: string;
  auto_provision: boolean;
  protocol: string;
  entity_id: string;
  auto_create_users: boolean;
  user_attribute_mapping: Record<string, string>;
}

export interface ERPConnector {
  id: string;
  form: string;
  erp_type: 'sap' | 'oracle' | 'salesforce' | 'dynamics' | 'netsuite';
  is_enabled: boolean;
  sync_direction: 'uni' | 'bi';
  field_mappings: Record<string, string>;
}

export interface SmartRoutingConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  routing_strategy: 'round_robin' | 'load_balanced' | 'skill_based' | 'ai_based' | 'rule_based';
  strategy: string;
  rules: unknown[];
  routing_rules: unknown[];
  fallback_assignee?: string;
}

export interface ApprovalWorkflow {
  id: string;
  form: string;
  name: string;
  is_enabled: boolean;
  description: string;
  is_active: boolean;
  approval_type: 'sequential' | 'parallel';
  auto_escalate: boolean;
  steps: Array<{
    step_number: number;
    approver_type: 'user' | 'role' | 'dynamic';
    approver_id?: string;
    approval_criteria?: unknown;
  }>;
}

export interface ApprovalRequest {
  id: string;
  workflow: string;
  submission: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  current_step: number;
  created_at: string;
}

export interface RuleEngine {
  id: string;
  form: string;
  name: string;
  is_enabled: boolean;
  description: string;
  is_active: boolean;
  execution_priority: 'low' | 'medium' | 'high';
  rules: Array<{
    condition: unknown;
    actions: unknown[];
    priority: number;
  }>;
}

export interface FormPipeline {
  id: string;
  form: string;
  name: string;
  is_enabled: boolean;
  stages: string[];
}

// ============================================================================
// MOBILE & PWA TYPES
// ============================================================================

export interface OfflineSyncConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  sync_strategy: string;
  conflict_resolution: 'server_wins' | 'client_wins' | 'merge' | 'manual';
  auto_retry: boolean;
  max_retries: number;
  max_storage_mb: number;
  sync_interval_minutes: number;
}

export interface BiometricConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  supported_types: string[];
  allowed_types: string[];
  require_on_open: boolean;
  require_on_submit: boolean;
  fallback_method: 'password' | 'pin' | 'none';
  fallback_to_pin: boolean;
  enrollment_required: boolean;
  session_timeout_minutes: number;
}

export interface GeolocationConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  required: boolean;
  accuracy_threshold: number;
  enable_geofencing: boolean;
  geofencing_enabled: boolean;
  geofences: Array<{
    name: string;
    center: { lat: number; lng: number };
    radius: number;
  }>;
  allowed_zones: Array<{
    name: string;
    center: { lat: number; lng: number };
    radius: number;
  }>;
  auto_capture: boolean;
  accuracy_required: string;
}

export interface MobilePaymentConfig {
  id: string;
  form: string;
  apple_pay_enabled: boolean;
  google_pay_enabled: boolean;
  merchant_id: string;
  supported_networks: string[];
  is_enabled: boolean;
  providers: string[];
  currency: string;
  test_mode: boolean;
  allow_saved_cards: boolean;
}

export interface PushNotificationConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  vapid_public_key: string;
  notification_types: string[];
  default_priority: 'low' | 'default' | 'high';
  ttl_seconds: number;
  badge_enabled: boolean;
  sound_enabled: boolean;
  vibrate_enabled: boolean;
}

// ============================================================================
// UX & DESIGN TYPES
// ============================================================================

export interface ThemeMarketplace {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string;
  preview_url: string;
  category: string;
  is_published: boolean;
  is_featured: boolean;
  price: number;
  rating_average: number;
  is_premium: boolean;
  rating: number;
  downloads: number;
  author: string;
  is_installed: boolean;
}

export interface EnhancedBrandGuideline {
  id: string;
  name: string;
  primary_color: string;
  is_active: boolean;
  color_palette: Record<string, string>;
  typography: Record<string, unknown>;
  spacing: Record<string, unknown>;
  border_radius: Record<string, unknown>;
  auto_apply: boolean;
  enforce_compliance: boolean;
  secondary_color: string;
  accent_color: string;
  primary_font: string;
  logo_url: string;
  is_default: boolean;
}

export interface AccessibilityAutoFix {
  id: string;
  form: string;
  is_enabled: boolean;
  auto_apply: boolean;
  target_level: 'A' | 'AA' | 'AAA';
  fixes_applied: unknown[];
}

export interface RealTimeCollabSession {
  id: string;
  form: string;
  session_id: string;
  is_active: boolean;
  participant_count: number;
  started_at: string;
}

export interface TeamWorkspace {
  id: string;
  name: string;
  description: string;
  owner: string;
  member_count: number;
  form_count: number;
  created_at: string;
  is_active: boolean;
  tags: string[];
}

export interface EnhancedFormTemplate {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string;
  category: string;
  is_public: boolean;
  is_featured: boolean;
  use_count: number;
  rating_average: number;
  usage_count: number;
  rating: number;
}

export interface DesignSystem {
  id: string;
  edge_locations: string[];
  functions: string[];
  name: string;
  owner: string;
  is_published: boolean;
  version: string;
  components: unknown;
  tokens: unknown;
}
// ============================================================================
// PERFORMANCE & SCALABILITY TYPES
// ============================================================================

export interface EdgeComputingConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  provider: string;
  edge_functions: string[];
  edge_locations: string[];
  functions: string[];
}

export interface CDNConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  provider: 'cloudflare' | 'cloudfront' | 'fastly' | 'akamai';
  cache_ttl: number;
  cache_hit_ratio: number;
  custom_domain: string;
  asset_types_to_cache: string[];
  cache_ttl_seconds: number;
  compression_enabled: boolean;
  image_optimization: boolean;
  purge_on_update: boolean;
}

export interface PerformanceMonitor {
  id: string;
  form: string;
  is_enabled: boolean;
  track_lcp: boolean;
  track_fid: boolean;
  track_cls: boolean;
  track_ttfb: boolean;
  enable_alerts: boolean;
  lcp: number;
  fid: number;
  cls: number;
  ttfb: number;
  load_time: number;
  bundle_size: number;
  bottlenecks: unknown[];
}

export interface LoadTestConfig {
  id: string;
  form: string;
  name: string;
  test_type: 'load' | 'stress' | 'spike' | 'endurance';
  key: string;
  scopes: string[];
  is_active: boolean;
  rate_limit_per_minute: number;
  rate_limit: { requests_per_hour: number };
}

export interface AutoScalingConfig {
  id: string;
  form: string;
  is_enabled: boolean;
  min_instances: number;
  max_instances: number;
  current_instances: number;
  scale_up_threshold: number;
  scale_down_threshold: number;
}

export interface Plugin {
  id: string;
  name: string;
  description: string;
  category: string;
  is_published: boolean;
  install_count: number;
  rating_average: number;
  is_enabled: boolean;
  version: string;
  author: string;
  manifest_url: string;
}

// ============================================================================
// DEVELOPER EXPERIENCE TYPES
// ============================================================================

export interface APIVersion {
  id: string;
  version: string;
  status: 'active' | 'deprecated' | 'sunset';
  release_date: string;
  sunset_date?: string;
  changelog: unknown[];
  active_consumers: number;
}

export interface FormsAPIKey {
  id: string;
  name: string;
  key_prefix: string;
  key: string;
  scopes: string[];
  is_active: boolean;
  rate_limit_per_minute: number;
  rate_limit: { requests_per_hour: number };
  expires_at?: string;
  last_used_at?: string;
  created_at: string;
}

export interface Plugin {
  id: string;
  name: string;
  description: string;
  category: string;
  is_published: boolean;
  install_count: number;
  rating_average: number;
}

export interface WebhookSigningKey {
  id: string;
  form: string;
  key_id: string;
  algorithm: 'HS256' | 'HS512' | 'RS256';
  is_active: boolean;
  created_at: string;
}

export interface DeveloperPortal {
  id: string;
  title: string;
  description: string;
  documentation_url: string;
  api_reference_url: string;
  is_public: boolean;
}
