# Generated by Django 2.2.16 on 2020-10-04 13:35

import cms.models.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('lms', '0012_auto_20201004_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='flow_content',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, slotname='lesson_content', to='cms.Placeholder'),
        ),
    ]