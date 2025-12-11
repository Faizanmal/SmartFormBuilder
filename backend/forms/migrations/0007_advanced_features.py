# Generated migration for all new advanced features

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0006_automation_features'),
        ('users', '0001_initial'),
    ]

    operations = [
        # Internationalization models
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, help_text="ISO 639-1 language code")),
                ('name', models.CharField(max_length=100)),
                ('native_name', models.CharField(max_length=100)),
                ('is_rtl', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('flag_emoji', models.CharField(max_length=10, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'languages',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FormTranslation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True)),
                ('schema_translations', models.JSONField(default=dict)),
                ('auto_translated', models.BooleanField(default=False)),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='forms.form')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forms.language')),
            ],
            options={
                'db_table': 'form_translations',
                'ordering': ['-created_at'],
            },
        ),
        
        # Integration Marketplace models
        migrations.CreateModel(
            name='IntegrationProvider',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('category', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('logo_url', models.URLField(blank=True)),
                ('api_base_url', models.URLField()),
                ('auth_type', models.CharField(max_length=20, default='api_key')),
                ('documentation_url', models.URLField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_premium', models.BooleanField(default=False)),
                ('popularity_score', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'integration_providers',
            },
        ),
        
        # Form Scheduling models
        migrations.CreateModel(
            name='FormSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('timezone', models.CharField(max_length=100, default='UTC')),
                ('max_submissions', models.IntegerField(null=True, blank=True)),
                ('auto_archive', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=20, default='pending')),
                ('activation_type', models.CharField(max_length=20, default='scheduled')),
                ('conditional_activation', models.JSONField(default=dict, blank=True)),
                ('notification_settings', models.JSONField(default=dict)),
                ('activated_at', models.DateTimeField(null=True, blank=True)),
                ('expired_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='forms.form')),
            ],
            options={
                'db_table': 'form_schedules',
            },
        ),
        
        # Theme models
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('is_premium', models.BooleanField(default=False)),
                ('colors', models.JSONField(default=dict)),
                ('typography', models.JSONField(default=dict)),
                ('layout', models.JSONField(default=dict)),
                ('components', models.JSONField(default=dict)),
                ('custom_css', models.TextField(blank=True)),
                ('custom_js', models.TextField(blank=True)),
                ('preview_image_url', models.URLField(blank=True)),
                ('downloads_count', models.IntegerField(default=0)),
                ('rating_average', models.DecimalField(max_digits=3, decimal_places=2, default=0.00)),
                ('rating_count', models.IntegerField(default=0)),
                ('brand_guidelines', models.JSONField(default=dict, blank=True)),
                ('enforce_guidelines', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='users.user')),
            ],
            options={
                'db_table': 'themes',
            },
        ),
        
        # Security models
        migrations.CreateModel(
            name='TwoFactorAuth',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_enabled', models.BooleanField(default=False)),
                ('method', models.CharField(max_length=20, default='totp')),
                ('secret_key', models.CharField(max_length=100, blank=True)),
                ('backup_codes', models.JSONField(default=list)),
                ('phone_number', models.CharField(max_length=20, blank=True)),
                ('verified_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='two_factor', to='users.user')),
            ],
            options={
                'db_table': 'two_factor_auth',
            },
        ),
        
        # Collaboration models
        migrations.CreateModel(
            name='FormCollaborator',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(max_length=20)),
                ('permissions', models.JSONField(default=dict)),
                ('invitation_accepted', models.BooleanField(default=False)),
                ('last_active_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborators', to='forms.form')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborative_forms', to='users.user')),
                ('invited_by', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invited_collaborators', to='users.user')),
            ],
            options={
                'db_table': 'form_collaborators',
            },
        ),
        
        # Mobile Optimization models
        migrations.CreateModel(
            name='MobileOptimization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('touch_enabled', models.BooleanField(default=True)),
                ('button_size', models.CharField(max_length=20, default='large')),
                ('swipe_gestures_enabled', models.BooleanField(default=True)),
                ('camera_enabled', models.BooleanField(default=False)),
                ('qr_scanner_enabled', models.BooleanField(default=False)),
                ('offline_mode_enabled', models.BooleanField(default=True)),
                ('cache_strategy', models.CharField(max_length=50, default='network_first')),
                ('max_cache_size_mb', models.IntegerField(default=50)),
                ('push_notifications_enabled', models.BooleanField(default=False)),
                ('notification_events', models.JSONField(default=list)),
                ('geolocation_enabled', models.BooleanField(default=False)),
                ('auto_detect_location', models.BooleanField(default=False)),
                ('location_accuracy', models.CharField(max_length=20, default='medium')),
                ('single_column_layout', models.BooleanField(default=True)),
                ('fixed_header', models.BooleanField(default=True)),
                ('progress_indicator_style', models.CharField(max_length=20, default='bar')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mobile_optimization', to='forms.form')),
            ],
            options={
                'db_table': 'mobile_optimizations',
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='formtranslation',
            index=models.Index(fields=['form', 'language'], name='form_trans_idx'),
        ),
    ]
