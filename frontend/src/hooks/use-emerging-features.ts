/**
 * API Hooks for Emerging Technology Features
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import type * as Types from '@/types/emerging-features';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ============================================================================
// AI & EMERGING TECH HOOKS
// ============================================================================

export const useAILayoutSuggestions = (formId: string) => {
  return useQuery({
    queryKey: ['ai-layout-suggestions', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.AILayoutSuggestion[]>(
        `${API_BASE_URL}/forms/${formId}/ai-layout-suggestions/`
      );
      return data;
    },
  });
};

export const useGenerateAILayoutSuggestion = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, triggerType }: { formId: string; triggerType: string }) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/forms/${formId}/ai-layout-suggestions/generate/`,
        { trigger_type: triggerType }
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ai-layout-suggestions', variables.formId] });
    },
  });
};

export const useConversationalAIConfig = (formId: string) => {
  return useQuery({
    queryKey: ['conversational-ai-config', formId],
    queryFn: async () => {
      const { data} = await axios.get<Types.ConversationalAIConfig>(
        `${API_BASE_URL}/forms/${formId}/conversational-ai-config/`
      );
      return data;
    },
  });
};

export const useUpdateConversationalAIConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.ConversationalAIConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/conversational-ai-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversational-ai-config', variables.formId] });
    },
  });
};

export const useConversationSessions = (formId: string) => {
  return useQuery({
    queryKey: ['conversation-sessions', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.ConversationSession[]>(
        `${API_BASE_URL}/forms/${formId}/conversation-sessions/`
      );
      return data;
    },
  });
};

export const useAIPersonalizations = (formId: string) => {
  return useQuery({
    queryKey: ['ai-personalizations', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.AIPersonalization[]>(
        `${API_BASE_URL}/forms/${formId}/ai-personalizations/`
      );
      return data;
    },
  });
};

export const useCreateAIPersonalization = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, personalization }: { formId: string; personalization: Partial<Types.AIPersonalization> }) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/forms/${formId}/ai-personalizations/`,
        personalization
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ai-personalizations', variables.formId] });
    },
  });
};

export const useHeatmapAnalysis = (formId: string) => {
  return useQuery({
    queryKey: ['heatmap-analysis', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.HeatmapAnalysis>(
        `${API_BASE_URL}/forms/${formId}/heatmap-analysis/`
      );
      return data;
    },
  });
};

// ============================================================================
// VOICE & MULTIMODAL HOOKS
// ============================================================================

export const useVoiceFormConfig = (formId: string) => {
  return useQuery({
    queryKey: ['voice-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.VoiceFormConfig>(
        `${API_BASE_URL}/forms/${formId}/voice-config/`
      );
      return data;
    },
  });
};

export const useUpdateVoiceConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.VoiceFormConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/voice-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['voice-config', variables.formId] });
    },
  });
};

export const useTranscribeVoice = () => {
  return useMutation({
    mutationFn: async ({ formId, audioBlob }: { formId: string; audioBlob: Blob }) => {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      const { data } = await axios.post(
        `${API_BASE_URL}/forms/${formId}/voice-transcribe/`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      return data;
    },
  });
};

export const useMultimodalConfig = (formId: string) => {
  return useQuery({
    queryKey: ['multimodal-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.MultimodalInputConfig>(
        `${API_BASE_URL}/forms/${formId}/multimodal-config/`
      );
      return data;
    },
  });
};

export const useUpdateMultimodalConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.MultimodalInputConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/multimodal-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['multimodal-config', variables.formId] });
    },
  });
};

export const useOCRExtract = () => {
  return useMutation({
    mutationFn: async ({ formId, image }: { formId: string; image: File }) => {
      const formData = new FormData();
      formData.append('image', image);
      const { data } = await axios.post<Types.OCRExtraction>(
        `${API_BASE_URL}/forms/${formId}/ocr-extract/`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      return data;
    },
  });
};

export const useARPreviewConfig = (formId: string) => {
  return useQuery({
    queryKey: ['ar-preview-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.ARPreviewConfig>(
        `${API_BASE_URL}/forms/${formId}/ar-preview-config/`
      );
      return data;
    },
  });
};

// ============================================================================
// SECURITY & COMPLIANCE HOOKS
// ============================================================================

export const useZeroKnowledgeEncryption = (formId: string) => {
  return useQuery({
    queryKey: ['zero-knowledge-encryption', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.ZeroKnowledgeEncryption>(
        `${API_BASE_URL}/forms/${formId}/zero-knowledge-encryption/`
      );
      return data;
    },
  });
};

export const useUpdateZeroKnowledgeEncryption = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.ZeroKnowledgeEncryption> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/zero-knowledge-encryption/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['zero-knowledge-encryption', variables.formId] });
    },
  });
};

export const useBlockchainConfig = (formId: string) => {
  return useQuery({
    queryKey: ['blockchain-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.BlockchainConfig>(
        `${API_BASE_URL}/forms/${formId}/blockchain-config/`
      );
      return data;
    },
  });
};

export const useUpdateBlockchainConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.BlockchainConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/blockchain-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['blockchain-config', variables.formId] });
    },
  });
};

export const useThreatDetectionConfig = (formId: string) => {
  return useQuery({
    queryKey: ['threat-detection-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.ThreatDetectionConfig>(
        `${API_BASE_URL}/forms/${formId}/threat-detection-config/`
      );
      return data;
    },
  });
};

export const useComplianceFrameworks = () => {
  return useQuery({
    queryKey: ['compliance-frameworks'],
    queryFn: async () => {
      const { data } = await axios.get<Types.ComplianceFramework[]>(
        `${API_BASE_URL}/compliance-frameworks/`
      );
      return data;
    },
  });
};

export const useComplianceScans = (formId: string) => {
  return useQuery({
    queryKey: ['compliance-scans', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.AdvancedComplianceScan[]>(
        `${API_BASE_URL}/forms/${formId}/compliance-scans/`
      );
      return data;
    },
  });
};

export const useRunComplianceScan = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, frameworkId }: { formId: string; frameworkId: string }) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/forms/${formId}/compliance-scans/run/`,
        { framework_id: frameworkId }
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['compliance-scans', variables.formId] });
    },
  });
};

// ============================================================================
// INTEGRATION & AUTOMATION HOOKS
// ============================================================================

export const useWebhookTransformers = () => {
  return useQuery({
    queryKey: ['webhook-transformers'],
    queryFn: async () => {
      const { data } = await axios.get<Types.WebhookTransformer[]>(
        `${API_BASE_URL}/webhook-transformers/`
      );
      return data;
    },
  });
};

export const useCreateWebhookTransformer = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (transformer: Partial<Types.WebhookTransformer>) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/webhook-transformers/`,
        transformer
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhook-transformers'] });
    },
  });
};

export const useMarketplaceIntegrations = (category?: string) => {
  return useQuery({
    queryKey: ['marketplace-integrations', category],
    queryFn: async () => {
      const params = category ? { category } : {};
      const { data } = await axios.get<Types.MarketplaceIntegration[]>(
        `${API_BASE_URL}/marketplace-integrations/`,
        { params }
      );
      return data;
    },
  });
};

export const useInstallMarketplaceIntegration = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ integrationId, formId }: { integrationId: string; formId: string }) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/marketplace-integrations/${integrationId}/install/`,
        { form_id: formId }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['marketplace-integrations'] });
    },
  });
};

export const useSSOConfigurations = (formId: string) => {
  return useQuery({
    queryKey: ['sso-configurations', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.SSOConfiguration[]>(
        `${API_BASE_URL}/forms/${formId}/sso-configurations/`
      );
      return data;
    },
  });
};

export const useCreateSSOConfiguration = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.SSOConfiguration> }) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/forms/${formId}/sso-configurations/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['sso-configurations', variables.formId] });
    },
  });
};

export const useSmartRoutingConfig = (formId: string) => {
  return useQuery({
    queryKey: ['smart-routing-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.SmartRoutingConfig>(
        `${API_BASE_URL}/forms/${formId}/smart-routing-config/`
      );
      return data;
    },
  });
};

export const useUpdateSmartRoutingConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.SmartRoutingConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/smart-routing-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['smart-routing-config', variables.formId] });
    },
  });
};

export const useApprovalWorkflows = (formId: string) => {
  return useQuery({
    queryKey: ['approval-workflows', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.ApprovalWorkflow[]>(
        `${API_BASE_URL}/forms/${formId}/approval-workflows/`
      );
      return data;
    },
  });
};

export const useCreateApprovalWorkflow = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, workflow }: { formId: string; workflow: Partial<Types.ApprovalWorkflow> }) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/forms/${formId}/approval-workflows/`,
        workflow
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['approval-workflows', variables.formId] });
    },
  });
};

export const useRuleEngines = (formId: string) => {
  return useQuery({
    queryKey: ['rule-engines', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.RuleEngine[]>(
        `${API_BASE_URL}/forms/${formId}/rule-engines/`
      );
      return data;
    },
  });
};

export const useUpdateRuleEngine = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, engineId, config }: { formId: string; engineId: string; config: Partial<Types.RuleEngine> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/rule-engines/${engineId}/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['rule-engines', variables.formId] });
    },
  });
};

export const useFormPipelines = (formId: string) => {
  return useQuery({
    queryKey: ['form-pipelines', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.FormPipeline[]>(
        `${API_BASE_URL}/forms/${formId}/pipelines/`
      );
      return data;
    },
  });
};

// ============================================================================
// MOBILE & PWA HOOKS
// ============================================================================

export const useOfflineSyncConfig = (formId: string) => {
  return useQuery({
    queryKey: ['offline-sync-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.OfflineSyncConfig>(
        `${API_BASE_URL}/forms/${formId}/offline-sync-config/`
      );
      return data;
    },
  });
};

export const useBiometricConfig = (formId: string) => {
  return useQuery({
    queryKey: ['biometric-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.BiometricConfig>(
        `${API_BASE_URL}/forms/${formId}/biometric-config/`
      );
      return data;
    },
  });
};

export const useGeolocationConfig = (formId: string) => {
  return useQuery({
    queryKey: ['geolocation-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.GeolocationConfig>(
        `${API_BASE_URL}/forms/${formId}/geolocation-config/`
      );
      return data;
    },
  });
};

export const useMobilePaymentConfig = (formId: string) => {
  return useQuery({
    queryKey: ['mobile-payment-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.MobilePaymentConfig>(
        `${API_BASE_URL}/forms/${formId}/mobile-payment-config/`
      );
      return data;
    },
  });
};

export const usePushNotificationConfig = (formId: string) => {
  return useQuery({
    queryKey: ['push-notification-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.PushNotificationConfig>(
        `${API_BASE_URL}/forms/${formId}/push-notification-config/`
      );
      return data;
    },
  });
};

export const useUpdateOfflineSyncConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.OfflineSyncConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/offline-sync-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['offline-sync-config', variables.formId] });
    },
  });
};

export const useUpdateBiometricConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.BiometricConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/biometric-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['biometric-config', variables.formId] });
    },
  });
};

export const useUpdateMobilePaymentConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.MobilePaymentConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/mobile-payment-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['mobile-payment-config', variables.formId] });
    },
  });
};

// ============================================================================
// UX & DESIGN HOOKS
// ============================================================================

export const useThemeMarketplace = (category?: string) => {
  return useQuery({
    queryKey: ['theme-marketplace', category],
    queryFn: async () => {
      const params = category ? { category } : {};
      const { data } = await axios.get<Types.ThemeMarketplace[]>(
        `${API_BASE_URL}/theme-marketplace/`,
        { params }
      );
      return data;
    },
  });
};

export const useBrandGuidelines = () => {
  return useQuery({
    queryKey: ['brand-guidelines'],
    queryFn: async () => {
      const { data } = await axios.get<Types.EnhancedBrandGuideline[]>(
        `${API_BASE_URL}/brand-guidelines/`
      );
      return data;
    },
  });
};

export const useAccessibilityAutoFix = (formId: string) => {
  return useQuery({
    queryKey: ['accessibility-auto-fix', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.AccessibilityAutoFix>(
        `${API_BASE_URL}/forms/${formId}/accessibility-auto-fix/`
      );
      return data;
    },
  });
};

export const useRealTimeCollabSession = (formId: string) => {
  return useQuery({
    queryKey: ['realtime-collab-session', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.RealTimeCollabSession>(
        `${API_BASE_URL}/forms/${formId}/realtime-collab-session/`
      );
      return data;
    },
  });
};

export const useTeamWorkspaces = () => {
  return useQuery({
    queryKey: ['team-workspaces'],
    queryFn: async () => {
      const { data } = await axios.get<Types.TeamWorkspace[]>(
        `${API_BASE_URL}/team-workspaces/`
      );
      return data;
    },
  });
};
export const useUpdateBrandGuideline = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ guidelineId, guideline }: { guidelineId: string; guideline: Partial<Types.EnhancedBrandGuideline> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/brand-guidelines/${guidelineId}/`,
        guideline
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-guidelines'] });
    },
  });
};
export const useFormTemplates = (category?: string) => {
  return useQuery({
    queryKey: ['form-templates', category],
    queryFn: async () => {
      const params = category ? { category } : {};
      const { data } = await axios.get<Types.EnhancedFormTemplate[]>(
        `${API_BASE_URL}/form-templates/`,
        { params }
      );
      return data;
    },
  });
};

export const useDesignSystems = () => {
  return useQuery({
    queryKey: ['design-systems'],
    queryFn: async () => {
      const { data } = await axios.get<Types.DesignSystem[]>(
        `${API_BASE_URL}/design-systems/`
      );
      return data;
    },
  });
};

// ============================================================================
// PERFORMANCE & SCALABILITY HOOKS
// ============================================================================

export const useEdgeComputingConfig = (formId: string) => {
  return useQuery({
    queryKey: ['edge-computing-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.EdgeComputingConfig>(
        `${API_BASE_URL}/forms/${formId}/edge-computing-config/`
      );
      return data;
    },
  });
};

export const useUpdateEdgeComputingConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, config }: { formId: string; config: Partial<Types.EdgeComputingConfig> }) => {
      const { data } = await axios.patch(
        `${API_BASE_URL}/forms/${formId}/edge-computing-config/`,
        config
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['edge-computing-config', variables.formId] });
    },
  });
};

export const useCDNConfig = (formId: string) => {
  return useQuery({
    queryKey: ['cdn-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.CDNConfig>(
        `${API_BASE_URL}/forms/${formId}/cdn-config/`
      );
      return data;
    },
  });
};

export const usePerformanceMonitor = (formId: string) => {
  return useQuery({
    queryKey: ['performance-monitor', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.PerformanceMonitor>(
        `${API_BASE_URL}/forms/${formId}/performance-monitor/`
      );
      return data;
    },
  });
};

export const useLoadTestConfigs = (formId: string) => {
  return useQuery({
    queryKey: ['load-test-configs', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.LoadTestConfig[]>(
        `${API_BASE_URL}/forms/${formId}/load-test-configs/`
      );
      return data;
    },
  });
};

export const useAutoScalingConfig = (formId: string) => {
  return useQuery({
    queryKey: ['auto-scaling-config', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.AutoScalingConfig>(
        `${API_BASE_URL}/forms/${formId}/auto-scaling-config/`
      );
      return data;
    },
  });
};

// ============================================================================
// DEVELOPER EXPERIENCE HOOKS
// ============================================================================

export const useAPIVersions = () => {
  return useQuery({
    queryKey: ['api-versions'],
    queryFn: async () => {
      const { data } = await axios.get<Types.APIVersion[]>(
        `${API_BASE_URL}/api-versions/`
      );
      return data;
    },
  });
};

export const useAPIKeys = () => {
  return useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      const { data } = await axios.get<Types.FormsAPIKey[]>(
        `${API_BASE_URL}/api-keys/`
      );
      return data;
    },
  });
};

export const useCreateAPIKey = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (apiKey: Partial<Types.FormsAPIKey>) => {
      const { data } = await axios.post(
        `${API_BASE_URL}/api-keys/`,
        apiKey
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });
};

export const usePlugins = (category?: string) => {
  return useQuery({
    queryKey: ['plugins', category],
    queryFn: async () => {
      const params = category ? { category } : {};
      const { data } = await axios.get<Types.Plugin[]>(
        `${API_BASE_URL}/plugins/`,
        { params }
      );
      return data;
    },
  });
};

export const useWebhookSigningKeys = (formId: string) => {
  return useQuery({
    queryKey: ['webhook-signing-keys', formId],
    queryFn: async () => {
      const { data } = await axios.get<Types.WebhookSigningKey[]>(
        `${API_BASE_URL}/forms/${formId}/webhook-signing-keys/`
      );
      return data;
    },
  });
};

export const useDeveloperPortals = () => {
  return useQuery({
    queryKey: ['developer-portals'],
    queryFn: async () => {
      const { data } = await axios.get<Types.DeveloperPortal[]>(
        `${API_BASE_URL}/developer-portals/`
      );
      return data;
    },
  });
};
