# Generated by Django 4.2.4 on 2023-08-06 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0004_alter_choice_question_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='question_title',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='title_choices', to='onlinecourse.question'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='question_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='onlinecourse.question'),
        ),
    ]
