# Generated by Django 2.2.16 on 2020-10-11 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='common_content',
        ),
        migrations.RemoveField(
            model_name='course',
            name='flow_content',
        ),
        migrations.RemoveField(
            model_name='course',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='lesson_content',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='show_common_content',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='support_content',
        ),
        migrations.AddField(
            model_name='lesson',
            name='brief',
            field=models.TextField(default='', help_text='Описание содержимого урока', max_length=5000),
        ),
    ]
