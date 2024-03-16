from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, QueryDict
from django.template import loader
from django.views import View

from QuizApp.models import Quiz, QuizGroup


class QuizView(LoginRequiredMixin, View):

    def get(self, request):
        context = {'auth': 'yes'}
        template = loader.get_template('create quiz\create_quiz.html')
        return HttpResponse(template.render(context, request))

    def post(self, request):
        user = request.user
        if len(Quiz.objects.filter(owner_id=user, title__iexact=request.POST['title'])) == 0:
            Quiz(owner_id=user, title=request.POST['title'], theme=request.POST['theme'],
                 description=request.POST['description'], public=request.POST['status']).save()
            quiz_id = Quiz.objects.get(owner_id__email=request.user.email, title=request.POST['title']).id
            return JsonResponse({'quiz_id': quiz_id}, status=200)
        else:
            return JsonResponse({'quiz_id': 'exists'}, status=200)

    def put(self, request):
        put = QueryDict(request.body)
        quiz = Quiz.objects.get(id=put['quiz_id'])
        if 'quiz_group' in put:
            quiz.group_id = QuizGroup.objects.get(owner_id=request.user, name=put['group'])
            quiz.save()
            return JsonResponse({}, status=200)
        else:
            quiz.title = put['title']
            quiz.theme = put['theme']
            quiz.description = put['description']
            quiz.save()
            return JsonResponse({}, status=200)

    # ok
    def delete(self, request):
        delete = QueryDict(request.body)
        if Quiz.objects.filter(id=delete['quiz_id']).exists():
            if Quiz.objects.get(id=delete['quiz_id']).owner_id == request.user:
                Quiz.objects.get(id=delete['quiz_id']).delete()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({}, status=401)
        else:
            return JsonResponse({'msg': 'This quiz does not exist'}, status=404)