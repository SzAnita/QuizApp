from django.http import HttpResponse
from django.template import loader

from QuizApp.models import Quiz, QuizResult, QuizGroup, User


def index(request):
    context = {
        'auth': 'no',
        'group': 'false'
    }
    quizzes = Quiz.objects.filter(public=True).values()
    if len(quizzes) > 0:
        context['quizzes'] = Quiz.objects.filter(public=True).values()
    if request.user.is_authenticated:
        context['auth'] = 'yes'
        context['group'] = 'true'
        context['groups'] = QuizGroup.objects.filter(owner_id=request.user)
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))
