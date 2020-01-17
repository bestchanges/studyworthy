# Generated by Django 3.0.2 on 2020-01-09 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20200108_0027'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseproduct',
            name='duration',
            field=models.CharField(blank=True, help_text='Например "3 мес 2 недели"', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='courseproduct',
            name='goals',
            field=models.TextField(blank=True, help_text='Что студент будет уметь после прохождения курса. Буллеты будут оформлены отдельно.', null=True),
        ),
        migrations.AddField(
            model_name='courseproduct',
            name='level',
            field=models.IntegerField(blank=True, choices=[(1, 'Beginner'), (2, 'Easy'), (3, 'Medium'), (4, 'Expert')], null=True),
        ),
        migrations.AddField(
            model_name='courseproduct',
            name='number_of_lessons',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseproduct',
            name='number_of_tasks',
            field=models.IntegerField(default=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseproduct',
            name='number_of_video_meterials',
            field=models.IntegerField(default=15),
            preserve_default=False,
        ),
    ]