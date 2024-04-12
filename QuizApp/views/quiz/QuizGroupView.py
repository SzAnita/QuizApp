from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect, QueryDict, HttpResponse
from django.template import loader
from django.views import View

from QuizApp.models import QuizGroup, Quiz


class QuizGroupView(View, LoginRequiredMixin):
    def get(self, request):
        context = {
            'groups': QuizGroup.objects.filter(owner_id=request.user),
            'auth': 'yes',
            'my_groups': 'yes'
        }
        template = loader.get_template('quiz/quiz-group.html')
        return HttpResponse(template.render(context, request))

    def post(self, request):
        if request.user.is_authenticated:
            QuizGroup(owner_id=request.user, name=request.POST['group']).save()
            group = QuizGroup(owner_id=request.user, name=request.POST['group'])
            return JsonResponse({'group_id': group.id, 'group_name': group.name}, status=201)
        else:
            return HttpResponseRedirect('QuizApp/login')

    def put(self, request):
        put = QueryDict(request.body)
        if (put['type'] == 'add' or put['type'] == 'remove') and  Quiz.objects.filter(id=put['quiz_id']).exists():
            quiz = Quiz.objects.get(id=put['quiz_id'])
            if put['type'] == 'add':
                quiz_group = QuizGroup.objects.get(owner_id=request.user, name=put['group'])
                if not QuizGroup.objects.filter(owner_id=request.user, name=put['group'], quizzes__id=quiz.id).exists():
                    quiz_group.quizzes.add(quiz)
                    quiz_group.save()

                    return JsonResponse({}, status=200)
                else:
                    return JsonResponse({}, status=400)
            elif put['type'] == 'remove':
                quiz_group = QuizGroup.objects.get(owner_id=request.user, id=put['group_id'])
                quiz_group.quizzes.remove(quiz)
                return JsonResponse({}, status=200)
        elif put['type'] == 'name':
            group = QuizGroup.objects.get(owner_id=request.user, name=put['old_name'])
            group.name = put['new_name']
            group.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({}, status=404)
