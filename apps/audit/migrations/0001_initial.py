import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('applications', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_status', models.CharField(blank=True, default='', help_text='Status before the transition; empty string for the initial insert.', max_length=20)),
                ('new_status', models.CharField(max_length=20)),
                ('reason', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(blank=True, help_text='The user who triggered the transition, or NULL for SYSTEM actions.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_actions', to=settings.AUTH_USER_MODEL)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='audit_logs', to='applications.visaapplication')),
            ],
            options={
                'verbose_name': 'Application Audit Log',
                'verbose_name_plural': 'Application Audit Logs',
                'db_table': 'audit_applicationauditlog',
                'indexes': [models.Index(fields=['application', 'timestamp'], name='idx_audit_app_timestamp'), models.Index(fields=['actor', 'timestamp'], name='idx_audit_actor_timestamp')],
            },
        ),
    ]
