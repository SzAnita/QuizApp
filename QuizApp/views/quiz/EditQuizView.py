from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView


from QuizApp.models import Quiz, Question, Answer

class EditQuizView(LoginRequiredMixin, TemplateView):
    template_name = 'quiz\edit.html'
    def get(self, request, quiz_id):
        if Quiz.objects.filter(id=quiz_id).exists():
            quiz = Quiz.objects.get(id=quiz_id)
            if request.user == quiz.owner_id:
                context = {
                    'quiz_id': quiz_id,
                    'title': quiz.title,
                    'theme': quiz.theme,
                    'description': quiz.description,
                    'user': 'yes',
                    'auth': 'yes'
                }
                questions = []
                for q in Question.objects.filter(quiz_id=quiz):
                    question = {
                        'id': q.id,
                        'question': q.question,
                        'type': q.type,
                        'points': q.points
                    }
                    answers = []
                    for a in Answer.objects.filter(question_id=q.id):
                        answer = {
                            'id': a.id,
                            'answer': a.answer,
                            'correct': a.correct,
                            'point': a.point
                        }
                        answers.append(answer)
                    question['answers'] = answers
                    questions.append(question)
                context['questions'] = questions
                return self.render_to_response(context)
            else:
                return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponseRedirect(reverse('home'))
