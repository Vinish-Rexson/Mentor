# Generated by Django 5.1.1 on 2024-10-20 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentor', '0008_alter_student1_profile_picture'),
        ('mentor_admin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='mentor_admins',
            field=models.ManyToManyField(blank=True, related_name='shared_sessions', to='mentor_admin.mentoradmin'),
        ),
    ]
