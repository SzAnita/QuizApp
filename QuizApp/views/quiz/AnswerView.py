from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import QueryDict, JsonResponse
from django.views import View

from QuizApp.models import Question, Answer


class AnswerView(LoginRequiredMixin, View):
    def post(self, request):
        data = QueryDict(request.body)
        if 'type' in data and data['type'] == 'put':
            return self.put(request)
        else:
            print(request.POST)
            my_question = Question.objects.get(id=int(request.POST['question_id']))
            if not Answer.objects.filter(question_id=int(request.POST['question_id']),
                                         answer__iexact=request.POST['answer']).exists():
                quiz = Question.objects.get(id=int(request.POST['question_id'])).quiz_id
                Answer(question_id=my_question, answer=request.POST['answer'], correct=request.POST['correct'],
                       point=request.POST['points'], quiz_id=quiz).save()
                my_question.points += int(request.POST['points'])
                my_question.save()
                answer_id = Answer.objects.get(question_id=my_question, answer__iexact=request.POST['answer']).id
                return JsonResponse({'answer_id': answer_id}, status=200)
            else:
                return JsonResponse({'msg': 'This answer already exists. Please change it.'})

    def put(self, request):
        put = QueryDict(request.body)
        if Answer.objects.filter(id=put['answer_id']).exists():
            answer = Answer.objects.get(id=put['answer_id'])
            answer.answer = put.get('answer')
            answer.correct = put.get('correct')
            old_points = answer.point
            answer.point = put.get('points')
            answer.save()
            if put.get('correct'):
                question = Question.objects.get(id=answer.question_id_id)
                question.points += int(put.get('points')) - old_points
                question.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({'msg': 'This answer does not exist'}, status=404)

    def delete(self, request):
        delete = QueryDict(request.body)
        if Answer.objects.filter(id=delete.get('answer_id')).exists():
            answer = Answer.objects.get(id=delete.get('answer_id'))
            if answer.question_id.quiz_id.owner_id == request.user:
                answer.delete()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({}, status=401)
        else:
            return JsonResponse({'msg': 'This answer does not exist'}, status=404)