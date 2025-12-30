from django.contrib import admin

# Core models
from .models import Form, Submission, FormTemplate, FormVersion, NotificationConfig

# Advanced models
from .models_advanced import (
    FormStep, PartialSubmission, FormABTest, TeamMember, 
    FormShare, FormAnalytics
)

# Analytics models
from .models_analytics import (
    FormHeatmapData, SessionRecording, SessionEvent, 
    DropOffAnalysis, ABTestResult
)

# Security models
from .models_security import (
    TwoFactorAuth, SSOProvider, EncryptedSubmission, 
    DataPrivacyRequest, ConsentTracking, SecurityAuditLog
)

# Mobile models (basic)
from .models_mobile import PushNotificationSubscription

# Integrations Marketplace models
from .models_integrations_marketplace import WebhookEndpoint

# AI/Emerging Tech models
from .models_emerging_tech import (
    AILayoutSuggestion, ConversationalAIConfig, ConversationSession,
    ConversationMessage, AIPersonalization, UserBehaviorProfile,
    HeatmapAnalysis, IndustryBenchmark, FormBenchmarkComparison
)

# Voice/Multimodal models
from .models_voice_multimodal import (
    VoiceFormConfig, VoiceInteraction, MultimodalInputConfig,
    OCRExtraction, QRBarcodesScan, AIAltText, ScreenReaderOptimization,
    NFCConfig, NFCScan, ARPreviewConfig, ARSession
)

# Advanced Security models
from .models_security_advanced import (
    ZeroKnowledgeEncryption, EncryptionKey, BlockchainConfig,
    BlockchainAuditEntry, ThreatDetectionConfig, ThreatEvent,
    IPBlocklist, ComplianceFramework, FormComplianceConfig,
    AdvancedComplianceScan, DataResidencyConfig, SubmissionDataLocation,
    AuditTrailConfig, AuditLogEntry, AdvancedComplianceReport
)

# Advanced Integration models
from .models_integrations_advanced import (
    WebhookTransformer, WebhookTransformLog, MarketplaceIntegration,
    MarketplaceInstallation, MarketplaceReview, FederatedFormShare,
    FederatedAccessLog, SSOConfiguration, SSOLoginEvent,
    ERPConnector, ERPSyncLog, LegacySystemBridge, GraphQLConfig,
    GraphQLQueryLog, RateLimitConfig, RateLimitEvent
)

# Advanced Mobile models
from .models_mobile_advanced import (
    OfflineSyncConfig, SyncQueue, SyncConflict, BiometricConfig,
    BiometricCredential, BiometricAuthEvent, GeolocationConfig,
    GeofenceEvent, LocationValidation, MobilePaymentConfig,
    MobilePaymentTransaction, PushNotificationConfig,
    ScheduledNotification, NotificationAnalytics
)

# Automation models
from .models_automation import (
    SmartRoutingConfig, RoutingAssignment, TeamMemberCapacity,
    ApprovalWorkflow, ApprovalRequest, ApprovalAction,
    FollowUpSequence, SequenceEnrollment, SequenceMessage,
    RuleEngine, RuleExecutionLog, CrossFormDependency,
    CrossFormLookup, FormPipeline, PipelineStage,
    FormPipelineCard, PipelineActivity
)

# UX/Design models
from .models_ux_design import (
    ThemeMarketplace, ThemePurchase, ThemeReview, EnhancedBrandGuideline,
    BrandValidation, AccessibilityAutoFix, AccessibilityFix,
    RealTimeCollabSession, CollabParticipant, CollabOperation,
    FormVersionDiff, TeamWorkspace, WorkspaceMember, WorkspaceInvite,
    EnhancedFormComment, DesignSystem, AnimationConfig, EnhancedFormTemplate
)

# Performance models
from .models_performance_scalability import (
    EdgeComputingConfig, IntelligentPreloadConfig, PreloadPrediction,
    DatabaseOptimizationConfig, QueryAnalysis, CDNConfig, CDNPurgeLog,
    MultiRegionConfig, RegionHealth, PerformanceMonitor,
    PerformanceSnapshot, EnhancedPerformanceAlert, LoadTestConfig,
    LoadTestRun, ResourceOptimization, AutoScalingConfig, ScalingEvent
)

# Developer Experience models
from .models_developer_experience import (
    APIVersion, FormsAPIKey, APIUsageLog, Plugin, PluginVersion,
    PluginInstallation, CustomFieldType, WebhookSigningKey,
    WebhookDelivery, SDKGenerator, DeveloperPortal, APIPlayground,
    CodeSample, ErrorCode, Changelog, RateLimitTier, DeveloperFeedback
)


# =====================
# Core Model Admin
# =====================

admin.site.register(Form)
admin.site.register(Submission)
admin.site.register(FormVersion)
admin.site.register(NotificationConfig)
admin.site.register(FormTemplate)

# Advanced models
admin.site.register(FormStep)
admin.site.register(PartialSubmission)
admin.site.register(FormABTest)
admin.site.register(TeamMember)
admin.site.register(FormShare)
admin.site.register(FormAnalytics)

# Analytics models
admin.site.register(FormHeatmapData)
admin.site.register(SessionRecording)
admin.site.register(SessionEvent)
admin.site.register(DropOffAnalysis)
admin.site.register(ABTestResult)

# Security models
admin.site.register(TwoFactorAuth)
admin.site.register(SSOProvider)
admin.site.register(EncryptedSubmission)
admin.site.register(DataPrivacyRequest)
admin.site.register(ConsentTracking)
admin.site.register(SecurityAuditLog)

# AI/Emerging Tech models
admin.site.register(AILayoutSuggestion)
admin.site.register(ConversationalAIConfig)
admin.site.register(ConversationSession)
admin.site.register(ConversationMessage)
admin.site.register(AIPersonalization)
admin.site.register(UserBehaviorProfile)
admin.site.register(HeatmapAnalysis)
admin.site.register(IndustryBenchmark)
admin.site.register(FormBenchmarkComparison)

# Voice/Multimodal models
admin.site.register(VoiceFormConfig)
admin.site.register(VoiceInteraction)
admin.site.register(MultimodalInputConfig)
admin.site.register(OCRExtraction)
admin.site.register(QRBarcodesScan)
admin.site.register(AIAltText)
admin.site.register(ScreenReaderOptimization)
admin.site.register(NFCConfig)
admin.site.register(NFCScan)
admin.site.register(ARPreviewConfig)
admin.site.register(ARSession)

# Advanced Security models
admin.site.register(ZeroKnowledgeEncryption)
admin.site.register(EncryptionKey)
admin.site.register(BlockchainConfig)
admin.site.register(BlockchainAuditEntry)
admin.site.register(ThreatDetectionConfig)
admin.site.register(ThreatEvent)
admin.site.register(IPBlocklist)
admin.site.register(ComplianceFramework)
admin.site.register(FormComplianceConfig)
admin.site.register(AdvancedComplianceScan)
admin.site.register(DataResidencyConfig)
admin.site.register(SubmissionDataLocation)
admin.site.register(AuditTrailConfig)
admin.site.register(AuditLogEntry)
admin.site.register(AdvancedComplianceReport)

# Advanced Integration models
admin.site.register(WebhookTransformer)
admin.site.register(WebhookTransformLog)
admin.site.register(MarketplaceIntegration)
admin.site.register(MarketplaceInstallation)
admin.site.register(MarketplaceReview)
admin.site.register(FederatedFormShare)
admin.site.register(FederatedAccessLog)
admin.site.register(SSOConfiguration)
admin.site.register(SSOLoginEvent)
admin.site.register(ERPConnector)
admin.site.register(ERPSyncLog)
admin.site.register(LegacySystemBridge)
admin.site.register(GraphQLConfig)
admin.site.register(GraphQLQueryLog)
admin.site.register(RateLimitConfig)
admin.site.register(RateLimitEvent)

# Advanced Mobile models
admin.site.register(OfflineSyncConfig)
admin.site.register(SyncQueue)
admin.site.register(SyncConflict)
admin.site.register(BiometricConfig)
admin.site.register(BiometricCredential)
admin.site.register(BiometricAuthEvent)
admin.site.register(GeolocationConfig)
admin.site.register(GeofenceEvent)
admin.site.register(LocationValidation)
admin.site.register(MobilePaymentConfig)
admin.site.register(MobilePaymentTransaction)
admin.site.register(PushNotificationConfig)
admin.site.register(ScheduledNotification)
admin.site.register(NotificationAnalytics)

# Automation models
admin.site.register(SmartRoutingConfig)
admin.site.register(RoutingAssignment)
admin.site.register(TeamMemberCapacity)
admin.site.register(ApprovalWorkflow)
admin.site.register(ApprovalRequest)
admin.site.register(ApprovalAction)
admin.site.register(FollowUpSequence)
admin.site.register(SequenceEnrollment)
admin.site.register(SequenceMessage)
admin.site.register(RuleEngine)
admin.site.register(RuleExecutionLog)
admin.site.register(CrossFormDependency)
admin.site.register(CrossFormLookup)
admin.site.register(FormPipeline)
admin.site.register(PipelineStage)
admin.site.register(FormPipelineCard)
admin.site.register(PipelineActivity)

# UX/Design models
admin.site.register(ThemeMarketplace)
admin.site.register(ThemePurchase)
admin.site.register(ThemeReview)
admin.site.register(EnhancedBrandGuideline)
admin.site.register(BrandValidation)
admin.site.register(AccessibilityAutoFix)
admin.site.register(AccessibilityFix)
admin.site.register(RealTimeCollabSession)
admin.site.register(CollabParticipant)
admin.site.register(CollabOperation)
admin.site.register(FormVersionDiff)
admin.site.register(TeamWorkspace)
admin.site.register(WorkspaceMember)
admin.site.register(WorkspaceInvite)
admin.site.register(EnhancedFormComment)
admin.site.register(DesignSystem)
admin.site.register(AnimationConfig)
admin.site.register(EnhancedFormTemplate)

# Performance models
admin.site.register(EdgeComputingConfig)
admin.site.register(IntelligentPreloadConfig)
admin.site.register(PreloadPrediction)
admin.site.register(DatabaseOptimizationConfig)
admin.site.register(QueryAnalysis)
admin.site.register(CDNConfig)
admin.site.register(CDNPurgeLog)
admin.site.register(MultiRegionConfig)
admin.site.register(RegionHealth)
admin.site.register(PerformanceMonitor)
admin.site.register(PerformanceSnapshot)
admin.site.register(EnhancedPerformanceAlert)
admin.site.register(LoadTestConfig)
admin.site.register(LoadTestRun)
admin.site.register(ResourceOptimization)
admin.site.register(AutoScalingConfig)
admin.site.register(ScalingEvent)

# Developer Experience models
admin.site.register(APIVersion)
admin.site.register(FormsAPIKey)
admin.site.register(APIUsageLog)
admin.site.register(Plugin)
admin.site.register(PluginVersion)
admin.site.register(PluginInstallation)
admin.site.register(CustomFieldType)
admin.site.register(WebhookSigningKey)
admin.site.register(WebhookDelivery)
admin.site.register(SDKGenerator)
admin.site.register(DeveloperPortal)
admin.site.register(APIPlayground)
admin.site.register(CodeSample)
admin.site.register(ErrorCode)
admin.site.register(Changelog)
admin.site.register(RateLimitTier)
admin.site.register(DeveloperFeedback)

# Additional models
admin.site.register(PushNotificationSubscription)
admin.site.register(WebhookEndpoint)
