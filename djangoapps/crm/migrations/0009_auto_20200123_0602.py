# Generated by Django 3.0.2 on 2020-01-23 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0008_enrollment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]