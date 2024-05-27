from django import utils
from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from QuizAppSettings import  settings
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(max_length=40, null=False, unique=True)
    password = models.CharField(max_length=90, null=False,
                                validators=[MinLengthValidator(6, 'the password must be at least 6 characters long')])
    name = models.CharField(max_length=70, null=True)
    username = models.CharField(null=True, unique=True, max_length=20)

    def __str__(self):
            return f'{self.username}, {self.email}'


class Quiz(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    owner_id = models.ForeignKey('User', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    theme = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=255, null=True)
    public = models.BooleanField(default=False)
    max_points = models.IntegerField(default=10)

    def __str__(self):
        return self.title


class QuizGroup(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    owner_id = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    public = models.BooleanField(default=False)
    quizzes = models.ManyToManyField(Quiz, related_name='quizgroup')

    def __str__(self):
        quizzes = ""
        for q in self.quizzes.all():
            quizzes = quizzes + q.__str__() + ", "
        return self.name + ":\n"+quizzes


class Question(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    quiz_id = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    points = models.IntegerField(default=0, null=False)

    class QuizTypeChoice(models.TextChoices):
        TYPING = 'TY',
        SINGLE_CHOICE = 'SC',
        MULTI_CHOICE = 'MC',

    type = models.CharField(max_length=2, choices=QuizTypeChoice.choices, default='TY', null=True)

    def __str__(self):
        return self.question


class Answer(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    quiz_id = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    question_id = models.ForeignKey("Question", on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)
    point = models.IntegerField(default=1, null=False)

    def __str__(self):
        answer = self.answer
        correct = self.correct
        my_str = "{} is {}".format(answer, correct)
        return my_str


class QuestionResult(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    user_id = models.ForeignKey('User', models.CASCADE, null=True)
    quiz_id = models.ForeignKey('Quiz', models.CASCADE)
    question_id = models.ForeignKey('Question', models.CASCADE)
    quiz_result_id = models.ForeignKey('QuizResult', models.CASCADE)
    result = models.DecimalField(decimal_places=2, max_digits=5, null=True)

    def __str__(self):
        return self.question_id.question + ': ' + str(self.result)


class QuizResult(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    quiz_id = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    result = models.DecimalField(decimal_places=2, max_digits=5, null=True)
    date_time = models.DateTimeField(default=utils.timezone.now())

    def __str__(self):
        return str(self.result) + '%'


class AnswerResult(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    quiz_result_id = models.ForeignKey('QuizResult', on_delete=models.CASCADE)
    answer_id = models.ForeignKey('Answer', on_delete=models.CASCADE)
