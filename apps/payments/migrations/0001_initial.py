import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded')], db_index=True, default='PENDING', max_length=10)),
                ('reference', models.CharField(db_index=True, help_text='Unique reference issued by the payment gateway.', max_length=100, unique=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='payment', to='applications.visaapplication')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'db_table': 'payments_payment',
                'indexes': [models.Index(fields=['status', 'paid_at'], name='idx_payment_status_paid')],
                'constraints': [models.UniqueConstraint(fields=('reference',), name='uq_payment_reference')],
            },
        ),
    ]
