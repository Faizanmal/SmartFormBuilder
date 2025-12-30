"""
Automation & Workflow Models

Features:
- Smart Form Routing
- Dynamic Approval Workflows
- Automated Follow-up Sequences
- Complex Rule Engine
- Dynamic Form Branching
- Cross-Form Dependencies
- Kanban-style Form Development
"""
from django.db import models
import uuid


# ============================================================================
# SMART FORM ROUTING
# ============================================================================

class SmartRoutingConfig(models.Model):
    """AI-based automatic routing of submissions to team members"""
    ROUTING_STRATEGIES = [
        ('round_robin', 'Round Robin'),
        ('load_balanced', 'Load Balanced'),
        ('skills_based', 'Skills Based'),
        ('priority_based', 'Priority Based'),
        ('geo_based', 'Geography Based'),
        ('ai_optimized', 'AI Optimized'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='smart_routing_config')
    
    is_enabled = models.BooleanField(default=False)
    strategy = models.CharField(max_length=30, choices=ROUTING_STRATEGIES, default='round_robin')
    
    # AI settings
    use_ai_scoring = models.BooleanField(default=False)
    ai_model_version = models.CharField(max_length=50, default='v1.0')
    
    # Routing rules
    routing_rules = models.JSONField(
        default=list,
        help_text="""
        Routing rules:
        [
            {
                "name": "High Value Leads",
                "conditions": [{"field": "budget", "operator": "gte", "value": 10000}],
                "assign_to": "senior_team",
                "priority": "high"
            }
        ]
        """
    )
    
    # Fallback
    fallback_assignee = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fallback_routing_forms'
    )
    
    # Capacity limits
    max_assignments_per_user = models.IntegerField(null=True, blank=True)
    respect_working_hours = models.BooleanField(default=True)
    
    # Notifications
    notify_assignee = models.BooleanField(default=True)
    notification_channel = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('slack', 'Slack'), ('sms', 'SMS'), ('push', 'Push')],
        default='email'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smart_routing_configs'
    
    def __str__(self):
        return f"Smart Routing for {self.form.title}"


class RoutingAssignment(models.Model):
    """Track submission assignments"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reassigned', 'Reassigned'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='routing_assignments')
    
    assigned_to = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='routing_assignments')
    assigned_by = models.CharField(max_length=50, help_text="system, manual, rule:xxx")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium'
    )
    
    # Routing metadata
    routing_rule_id = models.CharField(max_length=100, blank=True)
    routing_score = models.FloatField(default=0, help_text="AI routing score")
    routing_reason = models.TextField(blank=True)
    
    # Due date
    due_at = models.DateTimeField(null=True, blank=True)
    
    # Response
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    internal_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routing_assignments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Assignment: {self.submission.id} -> {self.assigned_to.email}"


class TeamMemberCapacity(models.Model):
    """Track team member capacity for load-balanced routing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='routing_capacity')
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='team_capacities')
    
    # Capacity settings
    max_daily_assignments = models.IntegerField(default=20)
    max_weekly_assignments = models.IntegerField(default=100)
    max_concurrent_assignments = models.IntegerField(default=10)
    
    # Current load
    current_assignments = models.IntegerField(default=0)
    daily_assignments = models.IntegerField(default=0)
    weekly_assignments = models.IntegerField(default=0)
    
    # Skills
    skills = models.JSONField(default=list)
    skill_levels = models.JSONField(default=dict)
    
    # Working hours
    working_hours = models.JSONField(
        default=dict,
        help_text="""
        {
            "timezone": "America/New_York",
            "monday": {"start": "09:00", "end": "17:00"},
            "tuesday": {"start": "09:00", "end": "17:00"},
            ...
        }
        """
    )
    
    # Availability
    is_available = models.BooleanField(default=True)
    out_of_office_until = models.DateTimeField(null=True, blank=True)
    
    # Stats
    avg_response_time_hours = models.FloatField(default=0)
    avg_completion_time_hours = models.FloatField(default=0)
    satisfaction_score = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'team_member_capacities'
        unique_together = [['user', 'form']]
    
    def __str__(self):
        return f"{self.user.email} capacity for {self.form.title}"


# ============================================================================
# DYNAMIC APPROVAL WORKFLOWS
# ============================================================================

class ApprovalWorkflow(models.Model):
    """Multi-step approval workflow configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='approval_workflows')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    # Trigger conditions
    trigger_conditions = models.JSONField(
        default=dict,
        help_text="Conditions to trigger this workflow"
    )
    
    # Approval steps
    steps = models.JSONField(
        default=list,
        help_text="""
        Approval steps:
        [
            {
                "step": 1,
                "name": "Manager Approval",
                "type": "single|all|any",
                "approvers": ["user_id_1", "role:manager"],
                "timeout_hours": 48,
                "timeout_action": "escalate|auto_approve|auto_reject",
                "conditions": {}
            }
        ]
        """
    )
    
    # Settings
    sequential_approval = models.BooleanField(default=True, help_text="Steps must be completed in order")
    allow_self_approval = models.BooleanField(default=False)
    require_comments = models.BooleanField(default=False)
    
    # Notifications
    notify_on_pending = models.BooleanField(default=True)
    notify_on_approved = models.BooleanField(default=True)
    notify_on_rejected = models.BooleanField(default=True)
    escalation_emails = models.JSONField(default=list)
    
    # SLA
    sla_hours = models.IntegerField(null=True, blank=True)
    sla_warning_hours = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'approval_workflows'
    
    def __str__(self):
        return f"{self.name} for {self.form.title}"


class ApprovalRequest(models.Model):
    """Active approval request for a submission"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.CASCADE, related_name='requests')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='approval_requests')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_step = models.IntegerField(default=1)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    
    # History
    step_history = models.JSONField(default=list)
    
    # Final result
    final_decision = models.CharField(max_length=20, blank=True)
    final_decision_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='final_approvals'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'approval_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Approval: {self.submission.id} - {self.status}"


class ApprovalAction(models.Model):
    """Individual approval actions within a request"""
    ACTION_TYPES = [
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('request_changes', 'Request Changes'),
        ('delegate', 'Delegated'),
        ('escalate', 'Escalated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE, related_name='actions')
    
    step_number = models.IntegerField()
    approver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='approval_actions')
    
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    comments = models.TextField(blank=True)
    
    # Delegation
    delegated_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delegated_approvals'
    )
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'approval_actions'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.action} by {self.approver.email} on step {self.step_number}"


# ============================================================================
# AUTOMATED FOLLOW-UP SEQUENCES
# ============================================================================

class FollowUpSequence(models.Model):
    """Intelligent email/SMS follow-up sequences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='follow_up_sequences')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    # Trigger
    trigger_event = models.CharField(
        max_length=30,
        choices=[
            ('on_submit', 'On Submit'),
            ('on_abandon', 'On Abandon'),
            ('on_complete', 'On Complete'),
            ('on_condition', 'On Condition'),
        ]
    )
    trigger_conditions = models.JSONField(default=dict)
    
    # Sequence steps
    steps = models.JSONField(
        default=list,
        help_text="""
        Sequence steps:
        [
            {
                "step": 1,
                "delay": {"value": 1, "unit": "hours"},
                "channel": "email",
                "template_id": "uuid",
                "subject": "Thanks for your submission!",
                "conditions": {}
            }
        ]
        """
    )
    
    # Exit conditions
    exit_conditions = models.JSONField(
        default=list,
        help_text="Conditions to exit the sequence early"
    )
    
    # AI personalization
    ai_personalization = models.BooleanField(default=False)
    ai_optimal_send_time = models.BooleanField(default=False)
    
    # A/B testing
    ab_testing_enabled = models.BooleanField(default=False)
    
    # Stats
    enrollments_count = models.IntegerField(default=0)
    completions_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'follow_up_sequences'
    
    def __str__(self):
        return f"{self.name} for {self.form.title}"


class SequenceEnrollment(models.Model):
    """Track enrollment in follow-up sequences"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('exited', 'Exited'),
        ('unsubscribed', 'Unsubscribed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sequence = models.ForeignKey(FollowUpSequence, on_delete=models.CASCADE, related_name='enrollments')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='sequence_enrollments')
    
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_step = models.IntegerField(default=0)
    
    # Personalization data
    personalization_data = models.JSONField(default=dict)
    
    # Engagement
    opens_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    
    # Timing
    next_step_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    exit_reason = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sequence_enrollments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} in {self.sequence.name}"


class SequenceMessage(models.Model):
    """Track individual messages sent in sequences"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(SequenceEnrollment, on_delete=models.CASCADE, related_name='messages')
    
    step_number = models.IntegerField()
    channel = models.CharField(max_length=20)
    
    # Content
    subject = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Timing
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery
    provider_message_id = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sequence_messages'
        ordering = ['step_number']
    
    def __str__(self):
        return f"Step {self.step_number} - {self.status}"


# ============================================================================
# COMPLEX RULE ENGINE
# ============================================================================

class RuleEngine(models.Model):
    """Complex rule engine for advanced conditional logic"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='rule_engines')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    
    # Rule definition
    rules = models.JSONField(
        default=dict,
        help_text="""
        Complex rule definition:
        {
            "conditions": {
                "all": [
                    {"field": "age", "operator": "gte", "value": 18},
                    {
                        "any": [
                            {"field": "country", "operator": "in", "value": ["US", "CA"]},
                            {"field": "premium", "operator": "equals", "value": true}
                        ]
                    }
                ]
            },
            "actions": [
                {"type": "show_field", "target": "premium_options"},
                {"type": "set_value", "field": "discount", "value": 10},
                {"type": "external_lookup", "api": "pricing_api", "params": {"tier": "${plan}"}}
            ]
        }
        """
    )
    
    # External data sources
    external_lookups = models.JSONField(
        default=list,
        help_text="External APIs/databases for rule evaluation"
    )
    
    # Caching
    cache_results = models.BooleanField(default=True)
    cache_ttl_seconds = models.IntegerField(default=300)
    
    # Execution stats
    executions_count = models.IntegerField(default=0)
    last_executed_at = models.DateTimeField(null=True, blank=True)
    avg_execution_time_ms = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rule_engines'
        ordering = ['priority']
    
    def __str__(self):
        return f"{self.name} for {self.form.title}"


class RuleExecutionLog(models.Model):
    """Log of rule engine executions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(RuleEngine, on_delete=models.CASCADE, related_name='execution_logs')
    session_id = models.CharField(max_length=100)
    
    # Input
    input_data = models.JSONField()
    
    # Evaluation
    conditions_evaluated = models.JSONField(default=dict)
    conditions_result = models.BooleanField()
    
    # Actions
    actions_executed = models.JSONField(default=list)
    actions_results = models.JSONField(default=list)
    
    # Performance
    execution_time_ms = models.FloatField()
    external_calls_count = models.IntegerField(default=0)
    
    # Errors
    had_errors = models.BooleanField(default=False)
    error_messages = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rule_execution_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rule {self.rule.name} - {'Pass' if self.conditions_result else 'Fail'}"


# ============================================================================
# CROSS-FORM DEPENDENCIES
# ============================================================================

class CrossFormDependency(models.Model):
    """Dependencies between forms for data sharing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    source_form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='dependencies_as_source'
    )
    target_form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='dependencies_as_target'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    # Link key
    link_field_source = models.CharField(max_length=100, help_text="Field in source form for linking")
    link_field_target = models.CharField(max_length=100, help_text="Field in target form for linking")
    
    # Data mapping
    field_mappings = models.JSONField(
        default=dict,
        help_text="Map source fields to target fields"
    )
    
    # Behavior
    auto_populate = models.BooleanField(default=True)
    populate_on = models.CharField(
        max_length=30,
        choices=[('load', 'On Load'), ('blur', 'On Blur'), ('submit', 'On Submit')],
        default='blur'
    )
    
    # Validation
    require_match = models.BooleanField(default=False, help_text="Require matching source submission")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cross_form_dependencies'
    
    def __str__(self):
        return f"{self.source_form.title} -> {self.target_form.title}"


class CrossFormLookup(models.Model):
    """Log of cross-form data lookups"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dependency = models.ForeignKey(CrossFormDependency, on_delete=models.CASCADE, related_name='lookups')
    
    session_id = models.CharField(max_length=100)
    lookup_value = models.TextField()
    
    # Result
    found = models.BooleanField()
    source_submission = models.ForeignKey(
        'forms.Submission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    populated_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cross_form_lookups'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Lookup: {self.lookup_value[:50]} - {'Found' if self.found else 'Not Found'}"


# ============================================================================
# FORM DEVELOPMENT PIPELINE (Kanban)
# ============================================================================

class FormPipeline(models.Model):
    """Kanban-style form development pipeline"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey('users.Team', on_delete=models.CASCADE, related_name='form_pipelines')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    # Settings
    require_review = models.BooleanField(default=True)
    auto_archive_days = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_pipelines'
    
    def __str__(self):
        return self.name


class PipelineStage(models.Model):
    """Stages in a form development pipeline"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(FormPipeline, on_delete=models.CASCADE, related_name='stages')
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    
    order = models.IntegerField()
    
    # Stage behavior
    is_initial = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    
    # Automations
    auto_assign_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    require_approval = models.BooleanField(default=False)
    
    # Limits
    wip_limit = models.IntegerField(null=True, blank=True, help_text="Work-in-progress limit")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pipeline_stages'
        ordering = ['order']
        unique_together = [['pipeline', 'order']]
    
    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"


class FormPipelineCard(models.Model):
    """Form card in the pipeline"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='pipeline_card')
    pipeline = models.ForeignKey(FormPipeline, on_delete=models.CASCADE, related_name='cards')
    stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE, related_name='cards')
    
    # Position
    position = models.IntegerField(default=0)
    
    # Assignment
    assignee = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Due date
    due_date = models.DateField(null=True, blank=True)
    
    # Priority
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium'
    )
    
    # Labels
    labels = models.JSONField(default=list)
    
    # Time tracking
    time_in_stage_hours = models.FloatField(default=0)
    stage_entered_at = models.DateTimeField(auto_now_add=True)
    
    # History
    stage_history = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_pipeline_cards'
        ordering = ['position']
    
    def __str__(self):
        return f"{self.form.title} in {self.stage.name}"


class PipelineActivity(models.Model):
    """Activity log for pipeline cards"""
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('stage_changed', 'Stage Changed'),
        ('assigned', 'Assigned'),
        ('due_date_set', 'Due Date Set'),
        ('commented', 'Commented'),
        ('label_added', 'Label Added'),
        ('label_removed', 'Label Removed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(FormPipelineCard, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    details = models.JSONField(default=dict)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pipeline_activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.activity_type} on {self.card.form.title}"
