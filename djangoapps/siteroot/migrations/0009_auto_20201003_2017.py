# Generated by Django 2.2.16 on 2020-10-03 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siteroot', '0008_auto_20201003_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manycourseproductpageextensioncmspluginconfigg',
            name='course_page_extensions',
            field=models.ManyToManyField(blank=True, null=True, to='siteroot.CourseProductPageExtension'),
        ),
    ]