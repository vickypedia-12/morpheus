# Generated by Django 4.2.17 on 2024-12-29 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buggy_forms', '0002_question_choices_alter_question_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='selected_options',
            field=models.JSONField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='answer',
            name='text_answer',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='choices',
            field=models.TextField(blank=True, help_text='Enter the choices for the Dropdown or CheckBox separated by Comma', null=True),
        ),
    ]
