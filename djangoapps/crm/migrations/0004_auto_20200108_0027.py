# Generated by Django 3.0.2 on 2020-01-07 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_auto_20200107_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='code',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='paymentin',
            name='code',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='code',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]