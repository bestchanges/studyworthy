# Generated by Django 2.2.16 on 2020-10-01 23:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0002_auto_20201002_0241'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='code',
            field=models.CharField(default=uuid.uuid4, max_length=250, unique=True),
        ),
    ]