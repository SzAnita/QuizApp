# Generated by Django 4.2.1 on 2024-03-22 10:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizApp', '0026_remove_answerresult_user_choice_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='group_id',
        ),
        migrations.AddField(
            model_name='quiz',
            name='groups',
            field=models.ManyToManyField(to='QuizApp.quizgroup'),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 22, 10, 53, 14, 846761, tzinfo=datetime.timezone.utc)),
        ),
    ]
