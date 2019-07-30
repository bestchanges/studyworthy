# Generated by Django 2.2.3 on 2019-07-30 14:08

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('study', '0002_auto_20190709_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CourseSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateField()),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('in_progress', 'In progress'), ('finished', 'Finished'), ('cancelled', 'Cancelled')], max_length=11)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='study.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('student', 'Student'), ('trainer', 'Trainer'), ('expert', 'Expert'), ('admin', 'Admin')], max_length=7)),
                ('status', models.CharField(choices=[('possible', 'Possible'), ('active', 'Active'), ('lost', 'Lost')], max_length=8)),
                ('score', models.IntegerField()),
                ('course_session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='study.CourseSession')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('country', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('language', models.CharField(choices=[('ru', 'Russian'), ('en', 'English'), ('ua', 'Ukrainian')], max_length=2)),
                ('skype', models.CharField(max_length=100)),
                ('google_account', models.CharField(max_length=100)),
                ('github_account', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='author',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='study.UserProfile'),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
        migrations.AddField(
            model_name='participant',
            name='user_profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='study.UserProfile'),
        ),
        migrations.AddField(
            model_name='applicationform',
            name='course_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='study.CourseSession'),
        ),
        migrations.AddField(
            model_name='applicationform',
            name='user_profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='study.UserProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='participant',
            unique_together={('course_session', 'user_profile', 'role')},
        ),
    ]
