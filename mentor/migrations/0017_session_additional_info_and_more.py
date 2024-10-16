# Generated by Django 5.1.1 on 2024-10-10 16:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentor', '0016_remove_session_date_remove_session_time_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='additional_info',
            field=models.JSONField(default=dict),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['mentor'], name='mentor_sess_mentor__30dd8a_idx'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['created_at'], name='mentor_sess_created_6bf683_idx'),
        ),
    ]