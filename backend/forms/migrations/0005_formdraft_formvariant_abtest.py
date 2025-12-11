# Generated migration for FormDraft, FormVariant, and ABTest models

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0004_conversational_reporting'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormDraft',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('draft_token', models.CharField(db_index=True, max_length=64, unique=True)),
                ('payload_json', models.JSONField(default=dict, help_text='Partial submission data')),
                ('current_step', models.IntegerField(default=0, help_text='Current step in multi-step form')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, help_text='Email to send resume link', max_length=254)),
                ('expires_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drafts', to='forms.form')),
            ],
            options={
                'db_table': 'form_drafts',
            },
        ),
        migrations.CreateModel(
            name='FormVariant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('schema_json', models.JSONField(help_text='Variant form schema')),
                ('traffic_percentage', models.IntegerField(default=50, help_text='Percentage of traffic to this variant')),
                ('views_count', models.IntegerField(default=0)),
                ('submissions_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='forms.form')),
            ],
            options={
                'db_table': 'form_variants',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ABTest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('running', 'Running'), ('paused', 'Paused'), ('completed', 'Completed')], default='draft', max_length=20)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ab_tests', to='forms.form')),
                ('winner_variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='won_tests', to='forms.formvariant')),
            ],
            options={
                'db_table': 'ab_tests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='formdraft',
            index=models.Index(fields=['draft_token'], name='form_drafts_draft_t_0a9e08_idx'),
        ),
        migrations.AddIndex(
            model_name='formdraft',
            index=models.Index(fields=['form', 'expires_at'], name='form_drafts_form_id_e77c43_idx'),
        ),
    ]
