# Generated by Django 4.2.6 on 2023-11-15 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0005_alter_quiz_group_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
