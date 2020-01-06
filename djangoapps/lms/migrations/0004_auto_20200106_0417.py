# Generated by Django 3.0.2 on 2020-01-06 01:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0003_person_avatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='code',
            field=models.CharField(default='2020-01-06 01:17:13.538869+00:00', max_length=36, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='unit',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='lms.Unit'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='decision_deadline_days',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='max_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='pass_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='unit',
            unique_together={('course', 'slug'), ('course', 'order')},
        ),
    ]
