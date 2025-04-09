# Generated by Django 5.1.7 on 2025-03-31 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adpa_events', '0002_question_document_choice_registration_response_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='adpa_events_user_groups', related_query_name='adpa_events_user', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_name='adpa_events_user_permissions', related_query_name='adpa_events_user', to='auth.permission'),
        ),
    ]
