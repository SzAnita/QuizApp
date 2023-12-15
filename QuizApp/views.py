import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.views import View
from django.contrib.auth import login
from django.views.decorators import csrf
from django.views.decorators.http import require_POST

from .forms import *
from .models import *


def index(request):
    context = {
        'user': 'no'
    }
    quizzes = Quiz.objects.filter(public=True).values()
    if len(quizzes) > 0:
        context['quizzes'] = Quiz.objects.filter(public=True).values()
    if request.user.is_authenticated:
        context['user'] = 'yes'
    # user = User.objects.get(email='szekr3@yahoo.com')
    # user.set_password('my.Acc3')
    # user.save()
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


def signup(request):
    context = {
        'form': Signup
    }
    if request.method == 'POST':
        form = Signup(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            pwd = form.cleaned_data.get('pwd')
            name = None
            username = None
            user = User(email=email, password=pwd)
            if len(form.cleaned_data['name']) > 0:
                name = form.cleaned_data['name']
                user.name = name
            if len(form.cleaned_data['username']) > 0:
                username = form.cleaned_data['username']
                user.username = username
            if not User.objects.filter(email=email).exists():
                try:
                    validate_password(pwd, user)
                    user.set_password(pwd)
                    user.save()
                    login(request, form.get_user())
                    request.session['email'] = email
                    request.session.modified = True
                    return HttpResponseRedirect('../index')
                except ValidationError as e:
                    form.add_error('pwd', e)
                    context['form'] = form
        else:
            context['form'] = form
    template = loader.get_template('signup.html')
    return HttpResponse(template.render(context, request))


def display_quiz(request, quiz_title, quiz_id):
    questions = Question.objects.filter(quiz_id=quiz_id).values()
    answers = Answer.objects.filter(quiz_id=quiz_id).values()
    for q in questions:
        if q['type'] != 'TY':
            q['answers'] = answers.filter(question_id=q['id']).values()
    context = {
        'questions': questions,
        'quiz_title': quiz_title,
        'quiz_id': quiz_id
    }
    template = loader.get_template('solvequiz.html')
    return HttpResponse(template.render(context, request))


@require_POST
def check_result(request, quiz_title, quiz_id):
    questions = Question.objects.filter(quiz_id=quiz_id)
    quiz_result = []
    quiz = Quiz.objects.get(id=quiz_id)
    user = request.user
    if request.user.is_authenticated:
        user = User.objects.get(email=request.session['email'])
    points = 0
    for q in questions:
        result = 0
        if q.type == 'TY':
            correct_answer = Answer.objects.get(question_id=q.id).answer
            user_answer = request.POST[str(q.id)]
            if correct_answer.lower() == user_answer.lower():
                question_result = [q.question, [user_answer, True]]
                quiz_result.append(question_result)
                result = 1
            else:
                question_result = [q.question, [user_answer, False, correct_answer]]
                quiz_result.append(question_result)
            QuestionResult(user_id=user, quiz_id=quiz, question_id=q, result=result)
        else:
            question_result = [Question.objects.get(id=q.id).question]
            answers = []
            for a in Answer.objects.filter(question_id=q.id).values():
                if str(a['id']) in request.POST.getlist(str(q.id)):
                    answers.append([a['answer'], a['correct'], True])
                    if a['correct']:
                        result = result + 1
                    answers.append([a['answer'], a['correct'], False])
            question_result.append(answers)
            question_result.append(result)
            quiz_result.append(question_result)
            QuestionResult(user_id=user, quiz_id=quiz, question_id=q, result=result).save()
        points += result
    QuizResult(user_id=user, quiz_id=quiz, result=points / quiz.max_points * 100).save()
    context = {
        'user_answers': quiz_result,
        'quiz_title': quiz_title,
        'user': 'no'
    }
    if request.user.is_authenticated:
        context['user'] = 'yes'
    template = loader.get_template('quiz_result.html')
    return HttpResponse(template.render(context, request))


class CreateQuizView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'user': 'yes'
        }
        template = loader.get_template('create_quiz.html')
        return HttpResponse(template.render(context, request))

    def post(self, request):
        user = request.user
        Quiz(owner_id=user, title=request.POST['title'], theme=request.POST['theme'],
             description=request.POST['description']).save()
        print(request.user.username)
        print(request.user.email)
        quiz_id = Quiz.objects.get(owner_id__email=request.user.email, title=request.POST['title']).id
        return HttpResponse(json.dumps(quiz_id))


class AddQuestionView(LoginRequiredMixin, View):
    def post(self, request):
        quiz = Quiz.objects.get(id=int(request.POST['quiz_id']))
        question = Question(quiz_id=quiz, question=request.POST['question'], type=request.POST['type'])
        question.save()
        question_id = Question.objects.get(quiz_id=quiz, question=request.POST['question'], type=request.POST['type'])
        for answer in json.loads(request.POST.getlist('answers[]')[0]):
            Answer(question_id=question_id, quiz_id=quiz, answer=answer['answer'], correct=answer['correct']).save()
        if str(request.POST['finish']) == 'true':
            context = {
                'title': Quiz.title,
                'theme': Quiz.theme,
                'description': Quiz.description
            }
            questions = Question.objects.filter(quiz_id=quiz).values()
            for q in questions:
                q['answers'] = Answer.objects.filter(question_id=q['id']).values()
            context['questions'] = questions
            template = loader.get_template('quiz_created.html')
            return HttpResponse(json.dumps(context))
        else:
            return HttpResponse(json.dumps('success'))

@require_POST
def add_question(request):
    quiz = Quiz.objects.get(id=int(request.GET['quiz_id']))
    question = Question(quiz_id=quiz, question=request.POST['question'], type=request.GET['type'])
    question.save()
    question_id = Question.objects.get(quiz_id=quiz, question=request.GET['question'], type=request.GET['type'])
    for answer in json.loads(request.GET.getlist('answers[]')[0]):
        Answer(question_id=question_id, quiz_id=quiz, answer=answer['answer'], correct=answer['correct']).save()
    if str(request.GET['finish']) == 'true':
        context = {
            'title': Quiz.title,
            'theme': Quiz.theme,
            'description': Quiz.description
        }
        questions = Question.objects.filter(quiz_id=quiz).values()
        for q in questions:
            q['answers'] = Answer.objects.filter(question_id=q['id']).values()
        context['questions'] = questions
        template = loader.get_template('quiz_created.html')
        return HttpResponse(json.dumps(context))
    else:
        return HttpResponse(json.dumps('success'))


def cancel_quiz(request):
    Quiz.objects.get(id=request.GET['quiz']).delete()
    return HttpResponse(json.dumps('success'))


@login_required()
def my_quizzes(request):
    #if 'email' in request.session:
        context = {
            'quizzes': Quiz.objects.filter(owner_id=request.user)
        }
        template = loader.get_template('my_quizzes.html')
        return HttpResponse(template.render(context, request))
    # else:
    #     template = loader.get_template('not_a_user.html')
    #     return HttpResponse(template.render)
