# Generated by Django 4.2.4 on 2023-08-13 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0010_remove_submission_course_alter_choice_choice_text'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choice',
            old_name='question_id',
            new_name='question',
        ),
        migrations.AddField(
            model_name='question',
            name='lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='onlinecourse.lesson'),
        ),
    ]
