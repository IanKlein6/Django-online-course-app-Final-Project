# Generated by Django 4.2.4 on 2023-08-06 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0003_question_question_text_question_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='question_id',
            field=models.ForeignKey(limit_choices_to={'title__isnull': False}, on_delete=django.db.models.deletion.CASCADE, to='onlinecourse.question'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.TextField(default='Default Question Text, Please add a New One', max_length=1000),
        ),
    ]