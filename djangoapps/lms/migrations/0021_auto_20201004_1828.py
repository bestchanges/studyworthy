# Generated by Django 2.2.16 on 2020-10-04 15:28

import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('lms', '0020_auto_20201004_1802'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='lesson_static',
        ),
        migrations.AddField(
            model_name='course',
            name='common_content',
            field=cms.models.fields.PlaceholderField(editable=False, help_text='Content shown in each course lesson', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lesson_common_content', slotname='lesson_common_content', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='show_common_content',
            field=models.BooleanField(default=True, help_text='Display content common for all lessons across course at the bottom of lesson content'),
        ),
    ]