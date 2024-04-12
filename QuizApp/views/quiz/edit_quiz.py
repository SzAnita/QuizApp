from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from QuizApp.models import Quiz, Question, Answer


@login_required(login_url='QuizApp/login')
def edit_quiz(request, quiz_id):
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
        template = loader.get_template('quiz\edit.html')
        return HttpResponse(template.render(context, request))
