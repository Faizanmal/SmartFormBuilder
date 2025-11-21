"""
Automated reporting service for scheduled analytics reports
"""
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import timedelta
import json


class ReportingService:
    """Service for generating and scheduling reports"""
    
    @staticmethod
    def generate_form_report(form, date_from, date_to, report_type='summary'):
        """
        Generate comprehensive report for a form
        
        Args:
            form: Form instance
            date_from: Start date
            date_to: End date
            report_type: 'summary', 'detailed', 'export'
            
        Returns:
            Report data dictionary
        """
        from forms.services.analytics_service import FormAnalyticsService
        from forms.models import Submission
        
        # Gather analytics data
        funnel = FormAnalyticsService.get_funnel_analytics(form, date_from, date_to)
        field_analytics = FormAnalyticsService.get_field_analytics(form, date_from, date_to)
        device_analytics = FormAnalyticsService.get_device_analytics(form, date_from, date_to)
        geo_analytics = FormAnalyticsService.get_geographic_analytics(form, date_from, date_to)
        time_series = FormAnalyticsService.get_time_series_data(form, date_from, date_to)
        
        # Get submission stats
        submissions = Submission.objects.filter(
            form=form,
            created_at__gte=date_from,
            created_at__lte=date_to
        )
        
        total_submissions = submissions.count()
        
        # Calculate trends
        previous_period_start = date_from - (date_to - date_from)
        previous_submissions = Submission.objects.filter(
            form=form,
            created_at__gte=previous_period_start,
            created_at__lt=date_from
        ).count()
        
        if previous_submissions > 0:
            trend = ((total_submissions - previous_submissions) / previous_submissions) * 100
        else:
            trend = 0 if total_submissions == 0 else 100
        
        report = {
            'form': {
                'id': str(form.id),
                'title': form.title,
                'slug': form.slug,
            },
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat(),
            },
            'summary': {
                'total_views': funnel['views'],
                'total_starts': funnel['starts'],
                'total_submissions': total_submissions,
                'conversion_rate': funnel['overall_conversion'],
                'trend': round(trend, 2),
            },
            'funnel': funnel,
            'field_analytics': field_analytics,
            'devices': device_analytics,
            'geography': geo_analytics,
            'time_series': time_series,
            'generated_at': timezone.now().isoformat(),
        }
        
        return report
    
    @staticmethod
    def send_report_email(report, recipients, include_charts=True):
        """
        Send report via email
        
        Args:
            report: Report data
            recipients: List of email addresses
            include_charts: Whether to include visualizations
        """
        from django.conf import settings
        
        subject = f"Form Report: {report['form']['title']} - {report['period']['from']} to {report['period']['to']}"
        
        # Render HTML email
        html_content = ReportingService._render_report_html(report, include_charts)
        text_content = ReportingService._render_report_text(report)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_content, "text/html")
        
        # Attach JSON data
        json_data = json.dumps(report, indent=2)
        email.attach('report_data.json', json_data, 'application/json')
        
        email.send()
    
    @staticmethod
    def _render_report_html(report, include_charts=True):
        """Render report as HTML"""
        context = {
            'report': report,
            'include_charts': include_charts,
        }
        return render_to_string('emails/analytics_report.html', context)
    
    @staticmethod
    def _render_report_text(report):
        """Render report as plain text"""
        summary = report['summary']
        funnel = report['funnel']
        
        text = f"""
Form Analytics Report
=====================

Form: {report['form']['title']}
Period: {report['period']['from']} to {report['period']['to']}

SUMMARY
-------
Total Views: {summary['total_views']}
Total Submissions: {summary['total_submissions']}
Conversion Rate: {summary['conversion_rate']}%
Trend: {summary['trend']:+.1f}%

CONVERSION FUNNEL
-----------------
Views: {funnel['views']}
Started: {funnel['starts']} ({funnel['view_to_start_rate']}%)
Submitted: {funnel['submits']} ({funnel['start_to_submit_rate']}%)

Drop-off Analysis:
- At Start: {funnel['drop_off_at_start']} users
- After Start: {funnel['drop_off_after_start']} users

DEVICES
-------
"""
        for device in report['devices']:
            text += f"- {device['device_type'].title()}: {device['count']} ({device['percentage']}%)\n"
        
        text += f"\n\nFull report attached as JSON.\n"
        
        return text
    
    @staticmethod
    def schedule_report(form, schedule_type, recipients, report_options=None):
        """
        Schedule a recurring report
        
        Args:
            form: Form instance
            schedule_type: 'daily', 'weekly', 'monthly'
            recipients: List of email addresses
            report_options: Additional options (charts, format, etc.)
            
        Returns:
            ScheduledReport instance
        """
        from forms.models_advanced import ScheduledReport
        
        scheduled_report = ScheduledReport.objects.create(
            form=form,
            schedule_type=schedule_type,
            recipients=recipients,
            report_options=report_options or {},
            next_run=ReportingService._calculate_next_run(schedule_type),
            is_active=True
        )
        
        return scheduled_report
    
    @staticmethod
    def _calculate_next_run(schedule_type):
        """Calculate next run time based on schedule type"""
        now = timezone.now()
        
        if schedule_type == 'daily':
            # Run at 8 AM next day
            next_run = now.replace(hour=8, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif schedule_type == 'weekly':
            # Run on Monday at 8 AM
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=8, minute=0, second=0, microsecond=0)
        
        elif schedule_type == 'monthly':
            # Run on 1st of next month at 8 AM
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=1, hour=8, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month + 1, day=1, hour=8, minute=0, second=0, microsecond=0)
        
        else:
            next_run = now + timedelta(days=1)
        
        return next_run
    
    @staticmethod
    def export_to_bi_format(report, format_type='csv'):
        """
        Export report data for BI tools
        
        Args:
            report: Report data
            format_type: 'csv', 'json', 'tableau', 'powerbi'
            
        Returns:
            Formatted data
        """
        if format_type == 'csv':
            return ReportingService._export_to_csv(report)
        elif format_type == 'json':
            return json.dumps(report, indent=2)
        elif format_type == 'tableau':
            return ReportingService._export_to_tableau(report)
        elif format_type == 'powerbi':
            return ReportingService._export_to_powerbi(report)
        else:
            return json.dumps(report, indent=2)
    
    @staticmethod
    def _export_to_csv(report):
        """Export to CSV format"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write summary
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Views', report['summary']['total_views']])
        writer.writerow(['Total Submissions', report['summary']['total_submissions']])
        writer.writerow(['Conversion Rate', f"{report['summary']['conversion_rate']}%"])
        writer.writerow([])
        
        # Write time series
        writer.writerow(['Date', 'Views', 'Submissions'])
        for item in report['time_series']['views']:
            submissions_count = next(
                (s['count'] for s in report['time_series']['submissions'] if s['period'] == item['period']),
                0
            )
            writer.writerow([item['period'], item['count'], submissions_count])
        
        return output.getvalue()
    
    @staticmethod
    def _export_to_tableau(report):
        """Export in Tableau-compatible format"""
        # Flatten data for Tableau
        tableau_data = {
            'form_id': report['form']['id'],
            'form_title': report['form']['title'],
            'metrics': [
                {
                    'date': item['period'],
                    'metric': 'views',
                    'value': item['count']
                }
                for item in report['time_series']['views']
            ] + [
                {
                    'date': item['period'],
                    'metric': 'submissions',
                    'value': item['count']
                }
                for item in report['time_series']['submissions']
            ]
        }
        return json.dumps(tableau_data, indent=2)
    
    @staticmethod
    def _export_to_powerbi(report):
        """Export in Power BI compatible format"""
        # Similar to Tableau but with Power BI conventions
        return ReportingService._export_to_tableau(report)
