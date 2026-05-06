import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualified_amount', models.IntegerField(choices=[
                    (3000, 'KES 3,000'), (5000, 'KES 5,000'),
                    (10000, 'KES 10,000'), (20000, 'KES 20,000'),
                ])),
                ('requested_amount', models.IntegerField(choices=[
                    (3000, 'KES 3,000'), (5000, 'KES 5,000'),
                    (10000, 'KES 10,000'), (20000, 'KES 20,000'),
                ])),
                ('deposit_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('reason', models.TextField()),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending Review'),
                        ('under_review', 'Under Review'),
                        ('approved', 'Approved'),
                        ('rejected', 'Rejected'),
                        ('deposit_pending', 'Awaiting Deposit'),
                        ('deposit_paid', 'Deposit Paid - Awaiting Disbursement'),
                        ('disbursed', 'Disbursed'),
                        ('repaid', 'Repaid'),
                    ],
                    default='pending',
                    max_length=30,
                )),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('disbursed_at', models.DateTimeField(blank=True, null=True)),
                ('repaid_at', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('repayment_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('repayment_reference', models.CharField(blank=True, max_length=100)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='loan_applications',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
    ]
