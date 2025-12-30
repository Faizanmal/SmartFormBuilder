"""
Serializers for new advanced features
"""
from rest_framework import serializers
from forms.models_new_features import *


# Field Dependencies
class FieldDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDependency
        fields = '__all__'


class ExternalAPIProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalAPIProvider
        fields = '__all__'


# Bulk Actions
class BulkActionSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BulkAction
        fields = '__all__'
    
    def get_progress_percentage(self, obj):
        if obj.total_submissions == 0:
            return 0
        return round((obj.processed_submissions / obj.total_submissions) * 100, 2)


# Spam Detection
# class SpamDetectionConfigSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SpamDetectionConfig
#         fields = '__all__'


# class SpamDetectionLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SpamDetectionLog
#         fields = '__all__'


# External Validation
class ExternalValidationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalValidationRule
        fields = '__all__'


# Form Testing
class FormTestSuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormTestSuite
        fields = '__all__'


class FormTestRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormTestRun
        fields = '__all__'


class FormPreviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormPreviewSession
        fields = '__all__'


# Workflow Pipeline
class WorkflowPipelineSerializer(serializers.ModelSerializer):
    stages = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowPipeline
        fields = '__all__'
    
    def get_stages(self, obj):
        return WorkflowStageSerializer(obj.stage_definitions.all(), many=True).data


class WorkflowStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStage
        fields = '__all__'


class SubmissionWorkflowStatusSerializer(serializers.ModelSerializer):
    current_stage_name = serializers.CharField(source='current_stage.name', read_only=True)
    assigned_to_email = serializers.CharField(source='assigned_to.email', read_only=True)
    
    class Meta:
        model = SubmissionWorkflowStatus
        fields = '__all__'


class WorkflowStageTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStageTransition
        fields = '__all__'


# Optimization Recommendations
# class FormOptimizationRecommendationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FormOptimizationRecommendation
#         fields = '__all__'


# class FormBenchmarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FormBenchmark
#         fields = '__all__'


# class OptimizationReportSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OptimizationReport
#         fields = '__all__'


# Scheduled Reports
# class ScheduledReportSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ScheduledReport
#         fields = '__all__'


# class ReportExecutionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReportExecution
#         fields = '__all__'


# Submission Comments
class SubmissionCommentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SubmissionComment
        fields = '__all__'
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class SubmissionNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionNote
        fields = '__all__'


# Form Cloning
class FormCloneSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormClone
        fields = '__all__'


class CustomFormTemplateSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomFormTemplate
        fields = '__all__'
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TemplateFavorite.objects.filter(
                user=request.user,
                template=obj
            ).exists()
        return False


class TemplateFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateFavorite
        fields = '__all__'
