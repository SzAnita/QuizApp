from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View

from QuizApp.models import QuizGroup


class QuizGroupView(View, LoginRequiredMixin):
    def get(self, request):
        return JsonResponse({}, status=200)

    def post(self, request):
        if request.user.is_authenticated:
            QuizGroup(owner_id=request.user, name=request.POST['name'])
            return JsonResponse({}, status=201)
        else:
            return HttpResponseRedirect('QuizApp/login')