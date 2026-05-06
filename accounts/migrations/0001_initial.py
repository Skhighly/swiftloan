from django.db import migrations, models
import accounts.models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('full_name', models.CharField(blank=True, max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('onboarding_step', models.CharField(
                    choices=[
                        ('registered', 'Registered'),
                        ('profile', 'Profile Submitted'),
                        ('id_upload', 'ID Uploaded'),
                        ('verification', 'Verification'),
                        ('job_info', 'Job Info Submitted'),
                        ('complete', 'Onboarding Complete'),
                    ],
                    default='registered',
                    max_length=20,
                )),
                ('groups', models.ManyToManyField(
                    blank=True,
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.group',
                    verbose_name='groups',
                )),
                ('user_permissions', models.ManyToManyField(
                    blank=True,
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.permission',
                    verbose_name='user permissions',
                )),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', accounts.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_front', models.ImageField(blank=True, null=True, upload_to='id_documents/front/')),
                ('id_back', models.ImageField(blank=True, null=True, upload_to='id_documents/back/')),
                ('mpesa_number', models.CharField(blank=True, max_length=15)),
                ('kra_pin', models.CharField(blank=True, max_length=20)),
                ('job_title', models.CharField(blank=True, max_length=100)),
                ('employer_name', models.CharField(blank=True, max_length=200)),
                ('monthly_income', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile',
                    to='accounts.user',
                )),
            ],
        ),
    ]
