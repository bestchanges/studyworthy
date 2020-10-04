# Generated by Django 2.2.16 on 2020-10-04 14:13

import cms.models.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('lms', '0013_lesson_flow_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='flow_content',
        ),
        migrations.AddField(
            model_name='lesson',
            name='content',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', slotname='lesson_content', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='support_content',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='support_content', slotname='support_content', to='cms.Placeholder'),
        ),
    ]
