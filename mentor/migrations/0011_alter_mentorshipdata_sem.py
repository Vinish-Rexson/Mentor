# Generated by Django 5.1.1 on 2024-10-21 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentor', '0010_mentorshipdata_sem_alter_mentorshipdata_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentorshipdata',
            name='sem',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]