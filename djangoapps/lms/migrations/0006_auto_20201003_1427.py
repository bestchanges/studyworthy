# Generated by Django 2.2.16 on 2020-10-03 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0005_auto_20201002_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='long_description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='course',
            name='short_description',
            field=models.CharField(default='', max_length=250),
        ),
    ]