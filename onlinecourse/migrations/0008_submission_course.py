# Generated by Django 4.2.4 on 2023-08-11 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0007_course_passing_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='course',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='onlinecourse.course'),
        ),
    ]
