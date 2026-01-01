"""
Automation and Workflow Service

Features:
- Smart submission routing
- Multi-step approvals
- Automated follow-ups
- Advanced rule engine
- Cross-form dependencies
- Kanban pipeline management
"""
import json
import operator
from typing import Dict, Any, List, Optional
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


class SmartRoutingService:
    """AI-powered submission routing"""
    
    def __init__(self):
        from .enhanced_ai_service import EnhancedAIService
        self.ai_service = EnhancedAIService()
    
    def route_submission(
        self,
        form,
        submission,
        submission_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Route a submission to the appropriate team member(s)
        
        Args:
            form: Form instance
            submission: Submission instance
            submission_data: Submission data
        
        Returns:
            Routing decision with assigned team members
        """
        from forms.models_automation import (
            SmartRoutingConfig,
        )
        
        try:
            config = SmartRoutingConfig.objects.get(form=form, is_enabled=True)
        except SmartRoutingConfig.DoesNotExist:
            return {'routed': False, 'reason': 'No routing config'}
        
        # Get routing strategy
        strategy = config.routing_strategy
        
        if strategy == 'round_robin':
            assignment = self._route_round_robin(config, submission)
        elif strategy == 'load_balanced':
            assignment = self._route_load_balanced(config, submission)
        elif strategy == 'skill_based':
            assignment = self._route_skill_based(config, submission, submission_data)
        elif strategy == 'ai_based':
            assignment = self._route_ai_based(config, submission, submission_data)
        elif strategy == 'rule_based':
            assignment = self._route_rule_based(config, submission, submission_data)
        else:
            return {'routed': False, 'reason': f'Unknown strategy: {strategy}'}
        
        if assignment:
            return {
                'routed': True,
                'assignment_id': str(assignment.id),
                'assigned_to': [
                    {'id': str(m.id), 'name': m.name if hasattr(m, 'name') else str(m)}
                    for m in assignment.assigned_members.all()
                ],
                'strategy': strategy,
                'reason': assignment.routing_reason,
            }
        
        return {'routed': False, 'reason': 'No suitable assignee found'}
    
    def _route_round_robin(self, config, submission) -> Optional['RoutingAssignment']:
        """Route using round-robin strategy"""
        from forms.models_automation import RoutingAssignment
        from forms.models_advanced import TeamMember
        
        # Get team members for this form
        team_members = TeamMember.objects.filter(
            form=config.form,
            is_active=True
        ).order_by('id')
        
        if not team_members.exists():
            return None
        
        # Get last assignment
        last_assignment = RoutingAssignment.objects.filter(
            config=config
        ).order_by('-created_at').first()
        
        if last_assignment and last_assignment.assigned_members.exists():
            last_member_id = last_assignment.assigned_members.first().id
            # Find next member
            next_members = team_members.filter(id__gt=last_member_id)
            if next_members.exists():
                next_member = next_members.first()
            else:
                next_member = team_members.first()
        else:
            next_member = team_members.first()
        
        # Create assignment
        assignment = RoutingAssignment.objects.create(
            config=config,
            submission=submission,
            routing_reason='Round-robin assignment',
        )
        assignment.assigned_members.add(next_member)
        
        return assignment
    
    def _route_load_balanced(self, config, submission) -> Optional['RoutingAssignment']:
        """Route based on current workload"""
        from forms.models_automation import RoutingAssignment, TeamMemberCapacity
        from forms.models_advanced import TeamMember
        
        team_members = TeamMember.objects.filter(
            form=config.form,
            is_active=True
        )
        
        if not team_members.exists():
            return None
        
        # Get current workload for each member
        member_workloads = []
        for member in team_members:
            # Count pending assignments
            pending_count = RoutingAssignment.objects.filter(
                assigned_members=member,
                status__in=['pending', 'in_progress'],
            ).count()
            
            # Get capacity if defined
            try:
                capacity = TeamMemberCapacity.objects.get(
                    config=config,
                    team_member=member,
                )
                max_capacity = capacity.max_assignments
                available = max_capacity - pending_count
            except TeamMemberCapacity.DoesNotExist:
                available = 100 - pending_count  # Default capacity
            
            member_workloads.append({
                'member': member,
                'pending': pending_count,
                'available': available,
            })
        
        # Sort by availability (most available first)
        member_workloads.sort(key=lambda x: x['available'], reverse=True)
        
        if member_workloads and member_workloads[0]['available'] > 0:
            best_member = member_workloads[0]['member']
            
            assignment = RoutingAssignment.objects.create(
                config=config,
                submission=submission,
                routing_reason=f'Load-balanced: {member_workloads[0]["pending"]} current assignments',
            )
            assignment.assigned_members.add(best_member)
            
            return assignment
        
        return None
    
    def _route_skill_based(
        self,
        config,
        submission,
        submission_data: Dict,
    ) -> Optional['RoutingAssignment']:
        """Route based on required skills"""
        from forms.models_automation import RoutingAssignment, TeamMemberCapacity
        from forms.models_advanced import TeamMember
        
        # Determine required skills from submission
        required_skills = self._extract_required_skills(config, submission_data)
        
        team_members = TeamMember.objects.filter(
            form=config.form,
            is_active=True,
        )
        
        # Score members by skill match
        scored_members = []
        for member in team_members:
            try:
                capacity = TeamMemberCapacity.objects.get(
                    config=config,
                    team_member=member,
                )
                member_skills = capacity.skills or []
            except TeamMemberCapacity.DoesNotExist:
                member_skills = []
            
            # Calculate skill match score
            if required_skills:
                match_count = len(set(member_skills) & set(required_skills))
                score = match_count / len(required_skills)
            else:
                score = 1.0
            
            scored_members.append({
                'member': member,
                'score': score,
                'skills': member_skills,
            })
        
        # Sort by score
        scored_members.sort(key=lambda x: x['score'], reverse=True)
        
        if scored_members and scored_members[0]['score'] > 0:
            best_member = scored_members[0]['member']
            
            assignment = RoutingAssignment.objects.create(
                config=config,
                submission=submission,
                routing_reason=f'Skill match: {scored_members[0]["score"]*100:.0f}%',
            )
            assignment.assigned_members.add(best_member)
            
            return assignment
        
        return None
    
    def _route_ai_based(
        self,
        config,
        submission,
        submission_data: Dict,
    ) -> Optional['RoutingAssignment']:
        """Route using AI analysis"""
        from forms.models_automation import RoutingAssignment, TeamMemberCapacity
        from forms.models_advanced import TeamMember
        
        team_members = TeamMember.objects.filter(
            form=config.form,
            is_active=True,
        )
        
        if not team_members.exists():
            return None
        
        # Get team member profiles
        member_profiles = []
        for member in team_members:
            try:
                capacity = TeamMemberCapacity.objects.get(
                    config=config,
                    team_member=member,
                )
                profile = {
                    'id': str(member.id),
                    'name': getattr(member, 'name', str(member)),
                    'skills': capacity.skills or [],
                    'specializations': capacity.specializations or [],
                    'current_load': RoutingAssignment.objects.filter(
                        assigned_members=member,
                        status='pending',
                    ).count(),
                }
            except TeamMemberCapacity.DoesNotExist:
                profile = {
                    'id': str(member.id),
                    'name': getattr(member, 'name', str(member)),
                    'skills': [],
                    'current_load': 0,
                }
            member_profiles.append(profile)
        
        # Use AI to determine best assignment
        prompt = f"""Analyze this form submission and recommend the best team member to handle it.

Submission Data:
{json.dumps(submission_data, indent=2)[:1000]}

Team Members:
{json.dumps(member_profiles, indent=2)}

Consider:
1. Required skills based on submission content
2. Current workload (lower is better)
3. Specializations that match the submission
4. Urgency indicators in the submission

Return JSON with your recommendation:
{{
    "recommended_member_id": "...",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation"
}}
"""
        
        response = self.ai_service.generate_completion(
            prompt=prompt,
            system_prompt="You are a workflow optimization expert. Make intelligent routing decisions.",
            max_tokens=300,
        )
        
        if response.get('content'):
            try:
                content = response['content']
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    recommendation = json.loads(content[start:end])
                    
                    member_id = recommendation.get('recommended_member_id')
                    if member_id:
                        try:
                            member = team_members.get(id=member_id)
                            
                            assignment = RoutingAssignment.objects.create(
                                config=config,
                                submission=submission,
                                routing_reason=f"AI: {recommendation.get('reason', 'AI recommendation')}",
                            )
                            assignment.assigned_members.add(member)
                            
                            return assignment
                        except TeamMember.DoesNotExist:
                            pass
            except json.JSONDecodeError:
                pass
        
        # Fallback to load-balanced
        return self._route_load_balanced(config, submission)
    
    def _route_rule_based(
        self,
        config,
        submission,
        submission_data: Dict,
    ) -> Optional['RoutingAssignment']:
        """Route based on configured rules"""
        from forms.models_automation import RoutingAssignment
        from forms.models_advanced import TeamMember
        
        rules = config.routing_rules or []
        
        for rule in rules:
            if self._evaluate_routing_rule(rule, submission_data):
                # Rule matched, assign to specified member(s)
                member_ids = rule.get('assign_to', [])
                if member_ids:
                    members = TeamMember.objects.filter(
                        id__in=member_ids,
                        form=config.form,
                        is_active=True,
                    )
                    
                    if members.exists():
                        assignment = RoutingAssignment.objects.create(
                            config=config,
                            submission=submission,
                            routing_reason=f"Rule: {rule.get('name', 'Matched rule')}",
                        )
                        assignment.assigned_members.set(members)
                        
                        return assignment
        
        # No rules matched, use fallback
        return self._route_round_robin(config, submission)
    
    def _evaluate_routing_rule(self, rule: Dict, data: Dict) -> bool:
        """Evaluate a routing rule against submission data"""
        conditions = rule.get('conditions', [])
        logic = rule.get('logic', 'and')  # and/or
        
        if not conditions:
            return False
        
        results = []
        for condition in conditions:
            field = condition.get('field')
            op = condition.get('operator')
            value = condition.get('value')
            
            actual_value = data.get(field)
            
            if op == 'equals':
                results.append(actual_value == value)
            elif op == 'not_equals':
                results.append(actual_value != value)
            elif op == 'contains':
                results.append(value in str(actual_value) if actual_value else False)
            elif op == 'greater_than':
                results.append(float(actual_value or 0) > float(value))
            elif op == 'less_than':
                results.append(float(actual_value or 0) < float(value))
        
        if logic == 'and':
            return all(results)
        else:
            return any(results)
    
    def _extract_required_skills(self, config, data: Dict) -> List[str]:
        """Extract required skills from submission data"""
        skill_mappings = config.skill_requirements or {}
        required = set()
        
        for field, mappings in skill_mappings.items():
            value = data.get(field)
            if value and value in mappings:
                required.update(mappings[value])
        
        return list(required)


class ApprovalWorkflowService:
    """Multi-step approval workflow management"""
    
    def create_approval_request(
        self,
        form,
        submission,
        workflow_type: str = 'sequential',
    ) -> Dict[str, Any]:
        """
        Create an approval request for a submission
        
        Args:
            form: Form instance
            submission: Submission instance
            workflow_type: 'sequential' or 'parallel'
        
        Returns:
            Approval request details
        """
        from forms.models_automation import ApprovalWorkflow, ApprovalRequest
        
        # Get workflow config
        try:
            workflow = ApprovalWorkflow.objects.get(form=form, is_enabled=True)
        except ApprovalWorkflow.DoesNotExist:
            return {'created': False, 'reason': 'No approval workflow configured'}
        
        # Check if approval is required based on conditions
        if workflow.conditions:
            submission_data = submission.payload_json
            if not self._check_approval_conditions(workflow.conditions, submission_data):
                return {
                    'created': False,
                    'reason': 'Approval not required based on conditions',
                    'auto_approved': True,
                }
        
        # Create approval request
        request = ApprovalRequest.objects.create(
            workflow=workflow,
            submission=submission,
            current_step=1,
        )
        
        # Notify first approver(s)
        self._notify_approvers(request, 1)
        
        return {
            'created': True,
            'request_id': str(request.id),
            'workflow': workflow.name,
            'total_steps': workflow.total_steps,
            'current_step': 1,
        }
    
    def process_approval_action(
        self,
        request_id: str,
        approver,
        action: str,
        comments: str = '',
    ) -> Dict[str, Any]:
        """
        Process an approval action (approve/reject/request_changes)
        
        Args:
            request_id: Approval request ID
            approver: User performing the action
            action: 'approve', 'reject', or 'request_changes'
            comments: Optional comments
        
        Returns:
            Updated approval status
        """
        from forms.models_automation import ApprovalRequest, ApprovalAction
        
        try:
            request = ApprovalRequest.objects.get(id=request_id)
        except ApprovalRequest.DoesNotExist:
            return {'success': False, 'error': 'Request not found'}
        
        workflow = request.workflow
        current_step = request.current_step
        
        # Verify approver is authorized for this step
        step_config = workflow.steps.get(str(current_step), {})
        authorized_approvers = step_config.get('approvers', [])
        
        approver_id = str(approver.id) if hasattr(approver, 'id') else str(approver)
        if authorized_approvers and approver_id not in authorized_approvers:
            return {'success': False, 'error': 'Not authorized to approve this step'}
        
        # Record action
        ApprovalAction.objects.create(
            request=request,
            step=current_step,
            approver_id=approver_id,
            action=action,
            comments=comments,
        )
        
        if action == 'approve':
            if current_step >= workflow.total_steps:
                # Final approval
                request.status = 'approved'
                request.completed_at = timezone.now()
                request.save()
                
                # Trigger post-approval actions
                self._execute_post_approval(request)
                
                return {
                    'success': True,
                    'status': 'approved',
                    'message': 'Request fully approved',
                }
            else:
                # Move to next step
                request.current_step = current_step + 1
                request.save()
                
                # Notify next approvers
                self._notify_approvers(request, current_step + 1)
                
                return {
                    'success': True,
                    'status': 'pending',
                    'current_step': current_step + 1,
                    'message': f'Approved step {current_step}, moved to step {current_step + 1}',
                }
        
        elif action == 'reject':
            request.status = 'rejected'
            request.completed_at = timezone.now()
            request.save()
            
            # Notify submitter
            self._notify_rejection(request, comments)
            
            return {
                'success': True,
                'status': 'rejected',
                'message': 'Request rejected',
            }
        
        elif action == 'request_changes':
            request.status = 'changes_requested'
            request.save()
            
            # Notify submitter
            self._notify_changes_requested(request, comments)
            
            return {
                'success': True,
                'status': 'changes_requested',
                'message': 'Changes requested from submitter',
            }
        
        return {'success': False, 'error': f'Unknown action: {action}'}
    
    def _check_approval_conditions(self, conditions: Dict, data: Dict) -> bool:
        """Check if approval is required based on conditions"""
        # Example conditions:
        # {"amount": {"operator": "greater_than", "value": 1000}}
        
        for field, condition in conditions.items():
            value = data.get(field)
            op = condition.get('operator')
            expected = condition.get('value')
            
            if op == 'greater_than' and float(value or 0) > float(expected):
                return True
            elif op == 'less_than' and float(value or 0) < float(expected):
                return True
            elif op == 'equals' and value == expected:
                return True
            elif op == 'contains' and expected in str(value):
                return True
        
        return False
    
    def _notify_approvers(self, request, step: int):
        """Notify approvers for a step"""
        workflow = request.workflow
        step_config = workflow.steps.get(str(step), {})
        approver_ids = step_config.get('approvers', [])
        
        from users.models import CustomUser
        
        for approver_id in approver_ids:
            try:
                user = CustomUser.objects.get(id=approver_id)
                
                send_mail(
                    subject=f'Approval Required: {workflow.form.title}',
                    message=f'''
You have a pending approval request.

Form: {workflow.form.title}
Step: {step} of {workflow.total_steps}
Request ID: {request.id}

Please log in to review and take action.
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except CustomUser.DoesNotExist:
                pass
    
    def _notify_rejection(self, request, comments: str):
        """Notify submitter of rejection"""
        # Implementation depends on how submissions track submitter
        pass
    
    def _notify_changes_requested(self, request, comments: str):
        """Notify submitter that changes are requested"""
        pass
    
    def _execute_post_approval(self, request):
        """Execute post-approval actions"""
        workflow = request.workflow
        actions = workflow.post_approval_actions or []
        
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'webhook':
                self._trigger_webhook(action, request)
            elif action_type == 'email':
                self._send_notification_email(action, request)
            elif action_type == 'integration':
                self._trigger_integration(action, request)
    
    def _trigger_webhook(self, action: Dict, request):
        """Trigger a webhook"""
        import requests
        
        url = action.get('url')
        if url:
            try:
                requests.post(
                    url,
                    json={
                        'event': 'approval_completed',
                        'request_id': str(request.id),
                        'submission_id': str(request.submission.id),
                        'status': request.status,
                    },
                    timeout=10,
                )
            except:
                pass
    
    def _send_notification_email(self, action: Dict, request):
        """Send notification email"""
        recipients = action.get('recipients', [])
        subject = action.get('subject', 'Approval Completed')
        
        send_mail(
            subject=subject,
            message=f'Approval request {request.id} has been completed with status: {request.status}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=True,
        )
    
    def _trigger_integration(self, action: Dict, request):
        """Trigger an integration"""
        # Placeholder for integration triggers
        pass


class RuleEngineService:
    """Complex conditional logic rule engine"""
    
    OPERATORS = {
        'equals': operator.eq,
        'not_equals': operator.ne,
        'greater_than': operator.gt,
        'less_than': operator.lt,
        'greater_equal': operator.ge,
        'less_equal': operator.le,
        'contains': lambda a, b: b in str(a) if a else False,
        'not_contains': lambda a, b: b not in str(a) if a else True,
        'starts_with': lambda a, b: str(a).startswith(b) if a else False,
        'ends_with': lambda a, b: str(a).endswith(b) if a else False,
        'is_empty': lambda a, _: not a,
        'is_not_empty': lambda a, _: bool(a),
        'in_list': lambda a, b: a in b if isinstance(b, list) else False,
        'not_in_list': lambda a, b: a not in b if isinstance(b, list) else True,
        'matches_regex': lambda a, b: bool(__import__('re').match(b, str(a))) if a else False,
    }
    
    def __init__(self):
        self.execution_log = []
    
    def evaluate_rules(
        self,
        form,
        data: Dict[str, Any],
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate all rules for a form against provided data
        
        Args:
            form: Form instance
            data: Data to evaluate against
            context: Additional context (user, time, etc.)
        
        Returns:
            Evaluation results with triggered actions
        """
        from forms.models_automation import RuleEngine, RuleExecutionLog
        
        rules = RuleEngine.objects.filter(
            form=form,
            is_enabled=True,
        ).order_by('priority')
        
        results = {
            'rules_evaluated': 0,
            'rules_triggered': 0,
            'actions_executed': [],
            'field_modifications': {},
            'errors': [],
        }
        
        full_context = {
            'data': data,
            'form': {'id': str(form.id), 'title': form.title},
            'timestamp': timezone.now().isoformat(),
            **(context or {}),
        }
        
        for rule in rules:
            results['rules_evaluated'] += 1
            
            try:
                triggered = self._evaluate_rule(rule, data, full_context)
                
                if triggered:
                    results['rules_triggered'] += 1
                    
                    # Execute actions
                    actions = self._execute_rule_actions(rule, data, full_context)
                    results['actions_executed'].extend(actions)
                    
                    # Apply field modifications
                    for mod in actions:
                        if mod.get('type') == 'field_modification':
                            results['field_modifications'].update(mod.get('modifications', {}))
                    
                    # Log execution
                    RuleExecutionLog.objects.create(
                        rule=rule,
                        trigger_data=data,
                        result='success',
                        actions_executed=actions,
                    )
                    
                    # Check if rule should stop further evaluation
                    if rule.stop_on_trigger:
                        break
                        
            except Exception as e:
                results['errors'].append({
                    'rule': rule.name,
                    'error': str(e),
                })
                
                RuleExecutionLog.objects.create(
                    rule=rule,
                    trigger_data=data,
                    result='error',
                    error_message=str(e),
                )
        
        return results
    
    def _evaluate_rule(
        self,
        rule,
        data: Dict,
        context: Dict,
    ) -> bool:
        """Evaluate a single rule"""
        conditions = rule.conditions
        logic = rule.condition_logic  # 'and', 'or', 'custom'
        
        if not conditions:
            return False
        
        results = []
        
        for condition in conditions:
            field = condition.get('field')
            op = condition.get('operator')
            expected = condition.get('value')
            
            # Get actual value (support nested paths)
            actual = self._get_nested_value(data, field)
            
            # Get operator function
            op_func = self.OPERATORS.get(op)
            
            if op_func:
                try:
                    # Type conversion for numeric comparisons
                    if op in ['greater_than', 'less_than', 'greater_equal', 'less_equal']:
                        actual = float(actual) if actual else 0
                        expected = float(expected)
                    
                    result = op_func(actual, expected)
                    results.append(result)
                except (ValueError, TypeError):
                    results.append(False)
            else:
                results.append(False)
        
        if logic == 'and':
            return all(results)
        elif logic == 'or':
            return any(results)
        elif logic == 'custom' and rule.custom_logic:
            return self._evaluate_custom_logic(rule.custom_logic, results)
        
        return all(results)
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dict using dot notation"""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    def _evaluate_custom_logic(self, logic: str, results: List[bool]) -> bool:
        """
        Evaluate custom logic expression
        Example: "(1 AND 2) OR (3 AND 4)"
        """
        # Replace numbers with actual results
        expression = logic
        for i, result in enumerate(results, 1):
            expression = expression.replace(str(i), str(result))
        
        # Replace logic operators
        expression = expression.replace('AND', 'and').replace('OR', 'or').replace('NOT', 'not')
        
        try:
            return eval(expression)
        except:
            return False
    
    def _execute_rule_actions(
        self,
        rule,
        data: Dict,
        context: Dict,
    ) -> List[Dict]:
        """Execute actions for a triggered rule"""
        actions = rule.actions
        executed = []
        
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'set_field':
                field = action.get('field')
                value = self._resolve_value(action.get('value'), data, context)
                executed.append({
                    'type': 'field_modification',
                    'modifications': {field: value},
                })
            
            elif action_type == 'show_field':
                executed.append({
                    'type': 'visibility',
                    'field': action.get('field'),
                    'visible': True,
                })
            
            elif action_type == 'hide_field':
                executed.append({
                    'type': 'visibility',
                    'field': action.get('field'),
                    'visible': False,
                })
            
            elif action_type == 'require_field':
                executed.append({
                    'type': 'validation',
                    'field': action.get('field'),
                    'required': True,
                })
            
            elif action_type == 'validate':
                executed.append({
                    'type': 'custom_validation',
                    'field': action.get('field'),
                    'validation': action.get('validation'),
                    'message': action.get('message'),
                })
            
            elif action_type == 'send_notification':
                executed.append({
                    'type': 'notification',
                    'channel': action.get('channel', 'email'),
                    'recipient': action.get('recipient'),
                    'message': self._resolve_value(action.get('message'), data, context),
                })
            
            elif action_type == 'webhook':
                executed.append({
                    'type': 'webhook',
                    'url': action.get('url'),
                    'method': action.get('method', 'POST'),
                    'payload': action.get('payload'),
                })
            
            elif action_type == 'calculate':
                field = action.get('field')
                formula = action.get('formula')
                value = self._calculate_formula(formula, data)
                executed.append({
                    'type': 'field_modification',
                    'modifications': {field: value},
                })
        
        return executed
    
    def _resolve_value(self, value: Any, data: Dict, context: Dict) -> Any:
        """Resolve a value that might contain references"""
        if not isinstance(value, str):
            return value
        
        # Check for field references: {{field_name}}
        import re
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_ref(match):
            ref = match.group(1).strip()
            return str(self._get_nested_value(data, ref) or '')
        
        return re.sub(pattern, replace_ref, value)
    
    def _calculate_formula(self, formula: str, data: Dict) -> Any:
        """Calculate a formula expression"""
        # Replace field references with values
        import re
        
        pattern = r'\[([^\]]+)\]'
        
        def replace_field(match):
            field = match.group(1)
            value = self._get_nested_value(data, field)
            return str(float(value) if value else 0)
        
        expression = re.sub(pattern, replace_field, formula)
        
        try:
            # Safe evaluation (only math operations)
            allowed_names = {"__builtins__": {}}
            return eval(expression, allowed_names)
        except:
            return 0


class FollowUpService:
    """Automated follow-up sequence service"""
    
    def enroll_in_sequence(
        self,
        submission,
        sequence_id: str = None,
    ) -> Dict[str, Any]:
        """
        Enroll a submission in a follow-up sequence
        
        Args:
            submission: Submission instance
            sequence_id: Optional specific sequence ID
        
        Returns:
            Enrollment details
        """
        from forms.models_automation import FollowUpSequence, SequenceEnrollment
        
        form = submission.form
        
        # Get sequence
        if sequence_id:
            try:
                sequence = FollowUpSequence.objects.get(id=sequence_id, form=form)
            except FollowUpSequence.DoesNotExist:
                return {'enrolled': False, 'error': 'Sequence not found'}
        else:
            # Get default sequence for form
            sequence = FollowUpSequence.objects.filter(
                form=form,
                is_enabled=True,
            ).first()
            
            if not sequence:
                return {'enrolled': False, 'error': 'No sequence configured'}
        
        # Check enrollment conditions
        if sequence.enrollment_conditions:
            if not self._check_enrollment_conditions(
                sequence.enrollment_conditions,
                submission.payload_json
            ):
                return {
                    'enrolled': False,
                    'reason': 'Does not meet enrollment conditions',
                }
        
        # Create enrollment
        enrollment = SequenceEnrollment.objects.create(
            sequence=sequence,
            submission=submission,
            contact_data=self._extract_contact_data(submission),
        )
        
        # Schedule first message
        self._schedule_next_message(enrollment)
        
        return {
            'enrolled': True,
            'enrollment_id': str(enrollment.id),
            'sequence': sequence.name,
            'total_steps': sequence.steps.count() if hasattr(sequence, 'steps') else len(sequence.messages or []),
        }
    
    def _check_enrollment_conditions(self, conditions: Dict, data: Dict) -> bool:
        """Check if submission meets enrollment conditions"""
        for field, condition in conditions.items():
            value = data.get(field)
            op = condition.get('operator', 'equals')
            expected = condition.get('value')
            
            if op == 'equals' and value != expected:
                return False
            elif op == 'not_equals' and value == expected:
                return False
            elif op == 'exists' and not value:
                return False
        
        return True
    
    def _extract_contact_data(self, submission) -> Dict:
        """Extract contact information from submission"""
        data = submission.payload_json
        contact = {}
        
        # Common email field names
        email_fields = ['email', 'e-mail', 'emailAddress', 'email_address', 'contact_email']
        for field in email_fields:
            if field in data:
                contact['email'] = data[field]
                break
        
        # Common name fields
        name_fields = ['name', 'full_name', 'fullName', 'first_name', 'firstName']
        for field in name_fields:
            if field in data:
                contact['name'] = data[field]
                break
        
        # Phone
        phone_fields = ['phone', 'telephone', 'mobile', 'phone_number']
        for field in phone_fields:
            if field in data:
                contact['phone'] = data[field]
                break
        
        return contact
    
    def _schedule_next_message(self, enrollment):
        """Schedule the next message in the sequence"""
        from forms.models_automation import SequenceMessage
        
        sequence = enrollment.sequence
        current_step = enrollment.current_step
        
        messages = sequence.messages or []
        
        if current_step >= len(messages):
            # Sequence complete
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
            enrollment.save()
            return
        
        message_config = messages[current_step]
        delay_minutes = message_config.get('delay_minutes', 0)
        
        # Calculate send time
        send_at = timezone.now() + timedelta(minutes=delay_minutes)
        
        # Create scheduled message
        SequenceMessage.objects.create(
            enrollment=enrollment,
            step=current_step + 1,
            scheduled_for=send_at,
            channel=message_config.get('channel', 'email'),
            subject=message_config.get('subject', ''),
            content=message_config.get('content', ''),
        )
    
    def process_scheduled_messages(self):
        """Process due scheduled messages (called by Celery task)"""
        from forms.models_automation import SequenceMessage
        
        due_messages = SequenceMessage.objects.filter(
            status='pending',
            scheduled_for__lte=timezone.now(),
        ).select_related('enrollment')
        
        for message in due_messages:
            try:
                self._send_sequence_message(message)
                message.status = 'sent'
                message.sent_at = timezone.now()
                message.save()
                
                # Update enrollment
                enrollment = message.enrollment
                enrollment.current_step = message.step
                enrollment.messages_sent += 1
                enrollment.save()
                
                # Schedule next message
                self._schedule_next_message(enrollment)
                
            except Exception as e:
                message.status = 'failed'
                message.error_message = str(e)
                message.save()
    
    def _send_sequence_message(self, message):
        """Send a sequence message"""
        enrollment = message.enrollment
        contact = enrollment.contact_data
        
        # Personalize content
        content = self._personalize_content(
            message.content,
            contact,
            enrollment.submission.payload_json
        )
        subject = self._personalize_content(
            message.subject,
            contact,
            enrollment.submission.payload_json
        )
        
        if message.channel == 'email':
            if contact.get('email'):
                send_mail(
                    subject=subject,
                    message=content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contact['email']],
                    fail_silently=False,
                )
        elif message.channel == 'sms':
            # SMS integration placeholder
            pass
    
    def _personalize_content(self, content: str, contact: Dict, data: Dict) -> str:
        """Personalize message content with contact/submission data"""
        import re
        
        # Replace {{field}} placeholders
        def replace_placeholder(match):
            key = match.group(1).strip()
            return str(contact.get(key) or data.get(key) or '')
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_placeholder, content)


class KanbanPipelineService:
    """Kanban-style pipeline management for submissions"""
    
    def create_pipeline_card(
        self,
        pipeline,
        submission,
        stage: str = None,
    ) -> Dict[str, Any]:
        """
        Create a pipeline card for a submission
        
        Args:
            pipeline: FormPipeline instance
            submission: Submission instance
            stage: Optional initial stage
        
        Returns:
            Created card details
        """
        from forms.models_automation import FormPipelineCard, PipelineStage
        
        # Get initial stage if not specified
        if not stage:
            initial_stage = PipelineStage.objects.filter(
                pipeline=pipeline
            ).order_by('order').first()
            
            if not initial_stage:
                return {'created': False, 'error': 'No stages defined'}
            
            stage_obj = initial_stage
        else:
            try:
                stage_obj = PipelineStage.objects.get(pipeline=pipeline, id=stage)
            except PipelineStage.DoesNotExist:
                return {'created': False, 'error': 'Stage not found'}
        
        # Get position
        last_card = FormPipelineCard.objects.filter(
            pipeline=pipeline,
            current_stage=stage_obj,
        ).order_by('-position').first()
        
        position = (last_card.position + 1) if last_card else 0
        
        # Create card
        card = FormPipelineCard.objects.create(
            pipeline=pipeline,
            submission=submission,
            current_stage=stage_obj,
            position=position,
            title=self._generate_card_title(submission),
            data=submission.payload_json,
        )
        
        return {
            'created': True,
            'card_id': str(card.id),
            'stage': stage_obj.name,
            'position': position,
        }
    
    def move_card(
        self,
        card_id: str,
        new_stage_id: str,
        new_position: int = None,
        user=None,
    ) -> Dict[str, Any]:
        """
        Move a card to a new stage or position
        
        Args:
            card_id: Card ID
            new_stage_id: Target stage ID
            new_position: Optional new position in stage
            user: User performing the move
        
        Returns:
            Updated card details
        """
        from forms.models_automation import FormPipelineCard, PipelineStage, PipelineActivity
        
        try:
            card = FormPipelineCard.objects.get(id=card_id)
        except FormPipelineCard.DoesNotExist:
            return {'success': False, 'error': 'Card not found'}
        
        try:
            new_stage = PipelineStage.objects.get(id=new_stage_id)
        except PipelineStage.DoesNotExist:
            return {'success': False, 'error': 'Stage not found'}
        
        old_stage = card.current_stage
        old_position = card.position
        
        # Update card
        card.current_stage = new_stage
        
        if new_position is not None:
            # Reorder other cards
            FormPipelineCard.objects.filter(
                pipeline=card.pipeline,
                current_stage=new_stage,
                position__gte=new_position,
            ).update(position=F('position') + 1)
            
            card.position = new_position
        else:
            # Add to end
            last_card = FormPipelineCard.objects.filter(
                pipeline=card.pipeline,
                current_stage=new_stage,
            ).order_by('-position').first()
            
            card.position = (last_card.position + 1) if last_card else 0
        
        card.save()
        
        # Log activity
        PipelineActivity.objects.create(
            card=card,
            activity_type='stage_change',
            from_stage=old_stage,
            to_stage=new_stage,
            user_id=str(user.id) if user else None,
        )
        
        # Execute stage triggers
        self._execute_stage_triggers(card, new_stage)
        
        return {
            'success': True,
            'card_id': str(card.id),
            'old_stage': old_stage.name,
            'new_stage': new_stage.name,
            'position': card.position,
        }
    
    def get_pipeline_view(self, pipeline) -> Dict[str, Any]:
        """
        Get complete pipeline view with all stages and cards
        
        Args:
            pipeline: FormPipeline instance
        
        Returns:
            Pipeline structure with cards
        """
        from forms.models_automation import PipelineStage, FormPipelineCard
        
        stages = PipelineStage.objects.filter(
            pipeline=pipeline
        ).order_by('order')
        
        pipeline_view = {
            'id': str(pipeline.id),
            'name': pipeline.name,
            'stages': [],
        }
        
        for stage in stages:
            cards = FormPipelineCard.objects.filter(
                pipeline=pipeline,
                current_stage=stage,
            ).order_by('position')
            
            stage_data = {
                'id': str(stage.id),
                'name': stage.name,
                'color': stage.color,
                'limit': stage.wip_limit,
                'cards': [
                    {
                        'id': str(card.id),
                        'title': card.title,
                        'position': card.position,
                        'submission_id': str(card.submission.id),
                        'created_at': card.created_at.isoformat(),
                        'assigned_to': list(card.assigned_to.values_list('id', flat=True)),
                        'labels': card.labels or [],
                    }
                    for card in cards
                ],
            }
            
            pipeline_view['stages'].append(stage_data)
        
        return pipeline_view
    
    def _generate_card_title(self, submission) -> str:
        """Generate a card title from submission data"""
        data = submission.payload_json
        
        # Try common title fields
        title_fields = ['title', 'name', 'subject', 'full_name', 'email']
        for field in title_fields:
            if field in data and data[field]:
                return str(data[field])[:100]
        
        # Fallback to submission ID
        return f"Submission #{str(submission.id)[:8]}"
    
    def _execute_stage_triggers(self, card, stage):
        """Execute triggers when card enters a stage"""
        triggers = stage.triggers or {}
        
        for trigger_type, config in triggers.items():
            if trigger_type == 'webhook':
                self._trigger_webhook(config, card)
            elif trigger_type == 'email':
                self._send_stage_email(config, card)
            elif trigger_type == 'assign':
                self._auto_assign(config, card)
    
    def _trigger_webhook(self, config: Dict, card):
        """Trigger webhook for stage"""
        import requests
        
        url = config.get('url')
        if url:
            try:
                requests.post(
                    url,
                    json={
                        'event': 'card_stage_change',
                        'card_id': str(card.id),
                        'stage': card.current_stage.name,
                        'data': card.data,
                    },
                    timeout=10,
                )
            except:
                pass
    
    def _send_stage_email(self, config: Dict, card):
        """Send email notification for stage"""
        recipients = config.get('recipients', [])
        subject = config.get('subject', f'Card moved to {card.current_stage.name}')
        
        if recipients:
            send_mail(
                subject=subject,
                message=f'Card "{card.title}" has been moved to stage: {card.current_stage.name}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True,
            )
    
    def _auto_assign(self, config: Dict, card):
        """Auto-assign card based on config"""
        from users.models import CustomUser
        
        user_ids = config.get('users', [])
        
        for user_id in user_ids:
            try:
                user = CustomUser.objects.get(id=user_id)
                card.assigned_to.add(user)
            except CustomUser.DoesNotExist:
                pass
