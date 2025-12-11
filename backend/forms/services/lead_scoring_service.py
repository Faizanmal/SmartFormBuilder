"""
Lead scoring and management service
"""


class LeadScoringService:
    """Service for scoring and managing leads"""
    
    # Default scoring rules
    DEFAULT_SCORING_RULES = {
        'email_domain': {
            'business_domains': 10,  # Corporate email domains
            'free_domains': -5,  # Free email services
        },
        'phone_provided': 15,
        'company_name_provided': 20,
        'budget_range': {
            'high': 30,
            'medium': 15,
            'low': 5,
        },
        'urgency': {
            'immediate': 25,
            'this_month': 15,
            'this_quarter': 5,
            'exploring': 0,
        },
        'referral': 20,
        'form_completion_speed': {
            'fast': 10,  # Completed in < 2 minutes
            'medium': 5,
            'slow': 0,
        },
    }
    
    @staticmethod
    def calculate_lead_score(submission, scoring_rules=None):
        """Calculate lead score based on submission data"""
        from forms.models_advanced import LeadScore
        
        if scoring_rules is None:
            scoring_rules = LeadScoringService.DEFAULT_SCORING_RULES
        
        payload = submission.payload_json
        score_breakdown = {}
        total_score = 0
        
        # Email domain scoring
        email = payload.get('email', '')
        if email:
            domain = email.split('@')[-1].lower()
            business_domains = ['company.com', 'corp.com', 'inc.com', 'ltd.com']
            free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            
            if any(bd in domain for bd in business_domains):
                score = scoring_rules['email_domain']['business_domains']
                total_score += score
                score_breakdown['email_domain'] = score
            elif domain in free_domains:
                score = scoring_rules['email_domain']['free_domains']
                total_score += score
                score_breakdown['email_domain'] = score
        
        # Phone provided
        if payload.get('phone'):
            score = scoring_rules['phone_provided']
            total_score += score
            score_breakdown['phone_provided'] = score
        
        # Company name
        if payload.get('company') or payload.get('company_name'):
            score = scoring_rules['company_name_provided']
            total_score += score
            score_breakdown['company_name'] = score
        
        # Budget range
        budget = payload.get('budget', '').lower()
        for budget_key, score in scoring_rules['budget_range'].items():
            if budget_key in budget:
                total_score += score
                score_breakdown['budget'] = score
                break
        
        # Urgency
        urgency = payload.get('urgency', '').lower()
        for urgency_key, score in scoring_rules['urgency'].items():
            if urgency_key in urgency:
                total_score += score
                score_breakdown['urgency'] = score
                break
        
        # Referral
        if payload.get('referral_source') or payload.get('how_did_you_hear'):
            score = scoring_rules['referral']
            total_score += score
            score_breakdown['referral'] = score
        
        # Determine quality
        if total_score >= 80:
            quality = 'qualified'
        elif total_score >= 50:
            quality = 'hot'
        elif total_score >= 25:
            quality = 'warm'
        else:
            quality = 'cold'
        
        # Create or update lead score
        lead_score, created = LeadScore.objects.update_or_create(
            submission=submission,
            defaults={
                'total_score': total_score,
                'score_breakdown': score_breakdown,
                'quality': quality,
            }
        )
        
        return lead_score
    
    @staticmethod
    def auto_assign_lead(lead_score, team_members=None):
        """Automatically assign lead to team member based on round-robin or load"""
        if not team_members:
            return None
        
        # Simple round-robin assignment
        # In production, could use more sophisticated logic like:
        # - Assign based on lead territory
        # - Assign based on team member availability
        # - Assign based on current workload
        
        from forms.models_advanced import LeadScore
        
        # Get team member with fewest assigned leads
        team_member_loads = []
        for member in team_members:
            load = LeadScore.objects.filter(
                assigned_to=member,
                follow_up_status__in=['pending', 'contacted', 'negotiating']
            ).count()
            team_member_loads.append((member, load))
        
        # Sort by load and assign to member with least load
        team_member_loads.sort(key=lambda x: x[1])
        assigned_to = team_member_loads[0][0]
        
        lead_score.assigned_to = assigned_to
        lead_score.save()
        
        return assigned_to
    
    @staticmethod
    def get_lead_analytics(user, date_from=None, date_to=None):
        """Get lead analytics for a user"""
        from forms.models_advanced import LeadScore
        from django.db.models import Count
        from forms.models import Form
        
        # Get all forms for user
        forms = Form.objects.filter(user=user)
        
        # Query leads
        leads = LeadScore.objects.filter(submission__form__in=forms)
        
        if date_from:
            leads = leads.filter(created_at__gte=date_from)
        if date_to:
            leads = leads.filter(created_at__lte=date_to)
        
        # Calculate metrics
        total_leads = leads.count()
        
        quality_breakdown = leads.values('quality').annotate(count=Count('id'))
        status_breakdown = leads.values('follow_up_status').annotate(count=Count('id'))
        
        average_score = leads.aggregate(avg_score=Count('total_score'))['avg_score'] or 0
        
        conversion_rate = 0
        if total_leads > 0:
            won_leads = leads.filter(follow_up_status='won').count()
            conversion_rate = (won_leads / total_leads) * 100
        
        return {
            'total_leads': total_leads,
            'quality_breakdown': list(quality_breakdown),
            'status_breakdown': list(status_breakdown),
            'average_score': average_score,
            'conversion_rate': round(conversion_rate, 2),
        }
