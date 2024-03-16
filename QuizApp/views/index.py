from django.http import HttpResponse
from django.template import loader

from QuizApp.models import Quiz, QuizResult


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
    for qr in QuizResult.objects.all():
        if qr.id == 5:
            qr.delete()
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))