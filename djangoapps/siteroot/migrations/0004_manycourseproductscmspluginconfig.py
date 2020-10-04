# Generated by Django 2.2.16 on 2020-10-03 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('siteroot', '0003_coursecmspluginconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManyCourseProductsCMSPluginConfig',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='siteroot_manycourseproductscmspluginconfig', serialize=False, to='cms.CMSPlugin')),
                ('course_page_extension', models.ManyToManyField(to='siteroot.CourseProductPageExtension')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]