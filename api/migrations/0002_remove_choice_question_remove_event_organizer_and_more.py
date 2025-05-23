# Generated by Django 5.1.7 on 2025-04-07 13:18

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adpa_events', '0004_remove_registration_event_remove_registration_user_and_more'),
        ('api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='choice',
            name='question',
        ),
        migrations.RemoveField(
            model_name='event',
            name='organizer',
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='event',
            field=models.ForeignKey(help_text='Event being registered for', on_delete=django.db.models.deletion.CASCADE, related_name='api_registrations', to='adpa_events.event'),
        ),
        migrations.RemoveField(
            model_name='survey',
            name='event',
        ),
        migrations.RemoveField(
            model_name='question',
            name='survey',
        ),
        migrations.AlterUniqueTogether(
            name='response',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='response',
            name='survey',
        ),
        migrations.RemoveField(
            model_name='response',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='eventregistration',
            options={'ordering': ['-registration_date'], 'verbose_name': 'Event Registration', 'verbose_name_plural': 'Event Registrations'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='attended',
            field=models.BooleanField(default=False, help_text='Whether the user attended the event'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='registration_date',
            field=models.DateTimeField(auto_now_add=True, help_text='When the registration was made'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='user',
            field=models.ForeignKey(help_text='User who registered', on_delete=django.db.models.deletion.CASCADE, related_name='api_event_registrations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Date when user account was created', verbose_name='date joined'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(help_text="User's email address (used as username)", max_length=254, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(help_text="User's first name", max_length=30, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active', verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_member',
            field=models.BooleanField(default=False, help_text='Designates special membership status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site', verbose_name='staff status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(help_text="User's last name", max_length=30, verbose_name='last name'),
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Survey',
        ),
        migrations.DeleteModel(
            name='Response',
        ),
    ]
