# Generated by Django 2.2.16 on 2020-10-11 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_courseproduct_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseproduct',
            name='long_description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='courseproduct',
            name='short_description',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
    ]
