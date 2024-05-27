from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, QueryDict, HttpResponse
from django.template import loader
from django.views import View
from django.views.generic.base import TemplateResponseMixin, TemplateView

from QuizApp.models import QuizGroup, Quiz


class QuizGroupView(LoginRequiredMixin, TemplateView, View):
    template_name = 'quiz/quiz-group.html'
    def get(self, request):
        context = {
            'groups': QuizGroup.objects.filter(owner_id=request.user),
            'auth': 'yes',
            'my_groups': 'yes',
        }
        return self.render_to_response(context)

    def post(self, request):
        if not QuizGroup.objects.filter(owner_id=request.user, name=request.POST['group']).exists():
            QuizGroup(owner_id=request.user, name=request.POST['group']).save()
            group = QuizGroup.objects.get(owner_id=request.user, name=request.POST['group'])
            return JsonResponse({'group_id': group.id, 'group_name': group.name}, status=201)
        else:
            return JsonResponse({'msg': "You already have a quiz group with this name."}, status=406)

    def put(self, request):
        put = QueryDict(request.body)
        if hasattr(request, 'PUT'):
            put = request.PUT
        if put['type'] == 'add' or put['type'] == 'remove':
            if Quiz.objects.filter(id=put['quiz_id']).exists():
                quiz = Quiz.objects.get(id=put['quiz_id'])
                if put['type'] == 'add':
                    status = 400
                    data = {'msg': 'This quiz is already in the quiz groups'}
                    for g in put.getlist('groups[]'):
                        if QuizGroup.objects.filter(owner_id=request.user, name=g).exists():
                            quiz_group = QuizGroup.objects.get(owner_id=request.user, name=g)
                            if not QuizGroup.objects.filter(owner_id=request.user, name=g, quizzes__id=quiz.id).exists():
                                quiz_group.quizzes.add(quiz)
                                quiz_group.save()
                                status = 200
                        else:
                            data['msg'] = "This quiz group doesn't exist"
                            status = 404
                    return JsonResponse(data, status=status)
                elif put['type'] == 'remove':
                    if QuizGroup.objects.filter(owner_id=request.user, id=put['group_id']).exists():
                        quiz_group = QuizGroup.objects.get(owner_id=request.user, id=put['group_id'])
                        quiz_group.quizzes.remove(quiz)
                        return JsonResponse({}, status=200)
                    else:
                        return JsonResponse({"msg": "This quiz group doesn't exist"}, status=404)
            else:
                return JsonResponse({"msg": "This quiz doesn't exist"}, status=404)
        elif put['type'] == 'name':
            if QuizGroup.objects.filter(owner_id=request.user, name=put['old_name']).exists():
                group = QuizGroup.objects.get(owner_id=request.user, name=put['old_name'])
                if not QuizGroup.objects.filter(owner_id=request.user, name=put['new_name']).exists():
                    group.name = put['new_name']
                    group.save()
                    return JsonResponse({}, status=200)
                else:
                    return JsonResponse({"msg": "You already have a quiz group with this name."}, status=409)
            else:
                return JsonResponse({"msg": "This quiz group doesn't exist"}, status=404)

    def delete(self, request):
        delete = QueryDict(request.body)
        if hasattr(request, 'DELETE'):
            delete = request.DELETE
        if QuizGroup.objects.filter(id=int(delete['group_id'])).exists():
            group = QuizGroup.objects.get(id=int(delete['group_id']))
            if group.owner_id == request.user:
                group.delete()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({}, status=401)
        else:
            return JsonResponse({'msg': "This group doesn't exist"}, status=404)

