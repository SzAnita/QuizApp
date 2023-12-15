from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(max_length=100, null=False, unique=True)
    password = models.CharField(max_length=90, null=False,
                                validators=[MinLengthValidator(6, 'the password must be at least 6 characters long')])
    name = models.CharField(max_length=70, null=True)
    username = models.CharField(null=True, unique=True, max_length=30)

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return self.email


class QuizGroup(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    owner_id = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    owner_id = models.ForeignKey('User', on_delete=models.CASCADE)
    group_id = models.ForeignKey('QuizGroup', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100, null=False)
    theme = models.CharField(max_length=40, null=True)
    description = models.CharField(max_length=255, null=True)
    public = models.BooleanField(default=False)
    max_points = models.IntegerField(default=10)

    def __str__(self):
        return self.title


class Question(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    quiz_id = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)

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
    result = models.DecimalField(decimal_places=2, max_digits=5, null=True)

    def __str__(self):
        return self.question_id.question + ': ' + str(self.result)


class QuizResult(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    quiz_id = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    result = models.DecimalField(decimal_places=2, max_digits=5, null=True)

    def __str__(self):
        return str(self.result) + '%'
