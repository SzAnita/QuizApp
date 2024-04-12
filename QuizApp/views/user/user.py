from functools import reduce

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from QuizApp.models import QuizResult, QuestionResult, Question, Answer, AnswerResult, QuizGroup


@login_required(login_url='QuizApp/login')
def user_report(request, quiz_result_id):
    # check if this quiz result exists
    if QuizResult.objects.filter(id=quiz_result_id, user_id=request.user).exists():
        quiz_result = QuizResult.objects.get(id=quiz_result_id, user_id=request.user)
        last_user_points = []
        question_max_points = []
        questions = []
        i = 1

        # get the user's last and best results by question
        for qr in QuestionResult.objects.filter(quiz_result_id__id=quiz_result.id, user_id=request.user):
            last_user_points.append(int(qr.result))
            question_max_points.append(qr.question_id.points)
            i += 1
        last_points = reduce(lambda x, y: x + y, last_user_points)

        # get the user's answers and correct answers by questions
        for q in Question.objects.filter(quiz_id=quiz_result.quiz_id):
            question = {
                'question': q.question,
                'correct_answers': [lambda arg=x: arg.answer for x in
                                    Answer.objects.filter(question_id=q, correct=True)],
                'user_answers': []
            }
            for a in AnswerResult.objects.filter(user_id=request.user, answer_id__question_id=q,
                                                 quiz_result_id=quiz_result):
                question['user_answers'].append(a.answer_id.answer)

            questions.append(question)

        context = {
            'last_user_points': last_user_points,
            'last_points': last_points,
            'question_max_points': question_max_points,
            'last_percent': quiz_result.result,
            'max_points': quiz_result.quiz_id.max_points,
            'question_nr': i,
            'more': 'false',
            'user': 'yes',
            'last_green': quiz_result.result / 100 * 360,
            'questions': questions,
            'best_user_points': 'false',
            'quiz_title': quiz_result.quiz_id.title
        }
        # check if the user has more than 1 quiz result
        if len(QuizResult.objects.filter(quiz_id=quiz_result.quiz_id.id, user_id=request.user)) > 1:
            best_user_points = []
            best_quiz_result = \
                QuizResult.objects.filter(quiz_id=quiz_result.quiz_id.id, user_id=request.user).order_by("-result")[0]

            # get user's best result by question
            for qr in QuestionResult.objects.filter(quiz_result_id=best_quiz_result).values():
                best_user_points.append(int(qr['result']))
            best_points = reduce(lambda x, y: x + y, best_user_points)
            context['best_user_points'] = best_user_points
            context['best_points'] = best_points
            context['best_percent'] = best_quiz_result.result
            context['more'] = 'true'
            context['best_green'] = best_quiz_result.result / 100 * 360

        return HttpResponse(loader.get_template("_user\\report_user.html").render(context, request))


@login_required(login_url='QuizApp/login')
def user_page(request):
    pwd = ""
    for l in range(8):
        pwd = pwd + '*'
    context = {
        'user': 'yes',
        'report': 'report',
        'quizzes': [],
        'username': request.user.username,
        'email': request.user.email,
        'password': pwd,
        'group': 'true',
        'auth': 'yes',
        'quiz_group': 'yes'
    }
    groups = []
    for g in QuizGroup.objects.filter(owner_id=request.user):
        group = {
            'id': g.id,
            'name': g.name,
            'quizzes': g.quizzes.all()
        }
        groups.append(group)
    context['groups'] = groups
    for qr in QuizResult.objects.filter(user_id=request.user):
        quiz = {
            'title': qr.quiz_id.title,
            'theme': qr.quiz_id.theme,
            'description': qr.quiz_id.description,
            'id': qr.quiz_id.id,
            'result_id': qr.id
        }
        context['quizzes'].append(quiz)

    return HttpResponse(loader.get_template('_user\page_user.html').render(context, request))
