# Generated by Django 4.2.17 on 2024-12-29 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buggy_forms', '0005_alter_question_options_question_order'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(fields=('form', 'order'), name='unique_question_order'),
        ),
    ]
