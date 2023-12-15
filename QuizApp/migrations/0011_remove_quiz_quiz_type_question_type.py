# Generated by Django 4.2.6 on 2023-11-22 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0010_rename_answers_answer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='quiz_type',
        ),
        migrations.AddField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('TY', 'Typing'), ('SC', 'Single Choice'), ('MC', 'Multi Choice')], default='SC', max_length=2),
        ),
    ]
