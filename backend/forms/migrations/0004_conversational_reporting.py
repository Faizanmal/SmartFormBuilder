# Generated migration for conversational forms and reporting

from django.db import migrations, models
import django.contrib.postgres.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0003_advanced_features'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversationalSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_token', models.CharField(max_length=255, unique=True)),
                ('conversation_history', models.JSONField(default=list, help_text='List of Q&A pairs')),
                ('collected_data', models.JSONField(default=dict, help_text='Data collected so far')),
                ('current_field_id', models.CharField(blank=True, max_length=255)),
                ('is_complete', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='conversational_sessions', to='forms.form')),
            ],
            options={
                'db_table': 'conversational_sessions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ScheduledReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('schedule_type', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], max_length=20)),
                ('recipients', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), help_text='Email addresses to send reports to', size=None)),
                ('report_options', models.JSONField(default=dict, help_text='Chart types, metrics to include, etc.')),
                ('is_active', models.BooleanField(default=True)),
                ('next_run', models.DateTimeField(help_text='When to send next report')),
                ('last_run', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='scheduled_reports', to='forms.form')),
            ],
            options={
                'db_table': 'scheduled_reports',
                'ordering': ['next_run'],
            },
        ),
    ]
