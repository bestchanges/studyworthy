# Generated by Django 2.2.3 on 2019-07-30 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0004_auto_20190730_1500'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='parentId',
            new_name='parent',
        ),
    ]