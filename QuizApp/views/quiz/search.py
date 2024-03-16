from django.http import HttpResponse
from django.template import loader

from QuizApp.models import Quiz


def search(request):
    search_value = request.GET['search']
    if request.user.is_authenticated:
        context = {
            'quizzes':
                Quiz.objects.filter(title__icontains=search_value, public=True) |
                Quiz.objects.filter(title__icontains=search_value, owner_id=request.user) |
                Quiz.objects.filter(theme__icontains=search_value, public=True) |
                Quiz.objects.filter(theme__icontains=search_value, owner_id=request.user) |
                Quiz.objects.filter(description__icontains=search_value, public=True) |
                Quiz.objects.filter(description__icontains=search_value, owner_id=request.user)
        }
    else:
        context = {
            'quizzes':
                Quiz.objects.filter(title__icontains=search_value, public=True) |
                Quiz.objects.filter(theme__icontains=search_value, public=True) |
                Quiz.objects.filter(description__icontains=search_value, public=True)
        }
    context['group'] = 'true'
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))