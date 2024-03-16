from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, QueryDict, JsonResponse
from django.template import loader
from django.views import View

from QuizApp.models import Quiz, Question


class QuestionView(LoginRequiredMixin, View):
    login_url = 'QuizApp/login'

    def get(self, request, quiz_id):
        context = {
            'quiz_id': quiz_id
        }
        template = loader.get_template('add_question.html')
        return HttpResponse(template.render(context, request))

    def post(self, request):
        data = QueryDict(request.body)
        if 'method_type' in data and data['method_type'] == 'put':
            return self.put(request)
        else:
            quiz = Quiz.objects.get(id=int(request.POST['quiz_id']))
            if not Question.objects.filter(quiz_id=quiz, question__iexact=request.POST['question']).exists():
                question = Question(quiz_id=quiz, question=request.POST['question'], type=request.POST['type'])
                question.save()
                question = Question.objects.get(quiz_id=quiz, question=request.POST['question'],
                                                type=request.POST['type'])
                context = {
                    'question_id': question.id
                }
                if str(request.POST['finish']) == 'true':
                    context['title'] = quiz.title
                    return JsonResponse({'question_id': question.id, 'title': quiz.title, 'quiz_id': quiz.id},
                                        status=201)
                else:
                    return JsonResponse({'question_id': question.id}, status=201)
            else:
                return JsonResponse({'msg': 'This question already exists. Please change it'})

    def put(self, request):
        put = QueryDict(request.body)
        my_question = Question.objects.get(id=int(put.get('question_id')))
        my_question.question = put.get('question')
        my_question.save()
        return JsonResponse({}, status=200)

    def delete(self, request):
        delete = QueryDict(request.body)
        if Question.objects.filter(id=int(delete.get('question_id'))).exists():
            question = Question.objects.get(id=int(delete.get('question_id')))
            if question.quiz_id.owner_id == request.user:
                question.delete()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({}, status=401)
        else:
            return JsonResponse({'msg': "This question doesn't exist"}, status=404)