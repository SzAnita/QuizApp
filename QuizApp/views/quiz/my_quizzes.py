from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from QuizApp.models import Quiz, QuizGroup


@login_required(login_url='QuizApp/login')
def my_quizzes(request):
    context = {
        'quizzes': Quiz.objects.filter(owner_id=request.user),
        'user': 'my_quizzes',
        'group': 'true',
        'auth': 'yes',
        'groups': QuizGroup.objects.filter(owner_id=request.user)
    }
    template = loader.get_template('quiz\my_quizzes.html')
    return HttpResponse(template.render(context, request))