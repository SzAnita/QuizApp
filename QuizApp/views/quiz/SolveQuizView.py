from django.http import HttpResponse
from django.template import loader
from django.views import View

from QuizApp.models import Question, Answer, Quiz, QuizResult, AnswerResult, QuestionResult


class SolveQuizView(View):
    def get(self, request, quiz_title, quiz_id):
        questions = Question.objects.filter(quiz_id=quiz_id).values()
        answers = Answer.objects.filter(quiz_id=quiz_id).values()
        for q in questions:
            if q['type'] != 'TY':
                q['answers'] = answers.filter(question_id=q['id']).values()
        context = {
            'questions': questions,
            'quiz_title': quiz_title,
            'quiz_id': quiz_id
        }
        if request.user.is_authenticated:
            context['user'] = 'yes'
        template = loader.get_template('solve quiz/solvequiz.html')
        return HttpResponse(template.render(context, request))

    def post(self, request, quiz_title, quiz_id):
        questions = Question.objects.filter(quiz_id=quiz_id)
        quiz_result = []
        quiz = Quiz.objects.get(id=quiz_id)
        user = request.user
        points = 0
        user_points = []
        question_max_points = []
        my_questions = []
        # loop through the questions in the quiz
        i = 1
        QuizResult(user_id=user, quiz_id=quiz, result=100).save()
        quiz_res = QuizResult.objects.filter(user_id=user, quiz_id=quiz).latest("date_time")
        for q in questions:
            my_questions.append("Q" + str(i) + ": " + q.question)
            i += 1
            result = 0
            question_max_points.append(q.points)
            # check the user's answer's correctness if the question type is Typing
            if q.type == 'TY':
                correct_answer = Answer.objects.get(question_id=q)
                user_answer = request.POST[str(q.id)]
                if correct_answer.answer.lower() == user_answer.lower():
                    question_result = [q.question, [user_answer, True]]
                    quiz_result.append(question_result)
                    result = correct_answer.point
                    user_points.append(result)
                else:
                    question_result = [q.question, [user_answer, False, correct_answer.answer]]
                    quiz_result.append(question_result)
                    user_points.append(0)
                AnswerResult(user_id=request.user, quiz_result_id=quiz_res, answer_id=correct_answer).save()
                QuestionResult(user_id=user, quiz_id=quiz, question_id=q, result=result, quiz_result_id=quiz_res).save()
            # check the user's answer's correctness if the question type is Single Choice or Multi Choice
            else:
                question_result = [q.question]
                answers = []
                for a in Answer.objects.filter(question_id=q.id):
                    if str(a.id) in request.POST.getlist(str(q.id)):
                        answers.append([a.answer, a.correct, True])
                        if a.correct:
                            result = result + a.point
                        AnswerResult(user_id=request.user, quiz_result_id=quiz_res, answer_id=a).save()
                    else:
                        answers.append([a.answer, a.correct, False])
                question_result.append(answers)
                question_result.append(result)
                quiz_result.append(question_result)
                user_points.append(result)
                QuestionResult(user_id=user, quiz_id=quiz, question_id=q, result=result, quiz_result_id=quiz_res).save()

            points += result
        quiz_res.result = (points / quiz.max_points) * 100
        quiz_res.save()
        context = {
            'user_answers': quiz_result,
            'quiz_title': quiz_title,
            'user': 'no',
            'result': points,
            'max_points': quiz.max_points,
            'percent': round((points / quiz.max_points) * 100, 2),
            'incorrect_percent': (1 - (points / quiz.max_points)) * 360,
            'question_nr': i,
            'user_points': user_points,
            'question_max_points': question_max_points,
            'questions': my_questions
        }
        if request.user.is_authenticated:
            context['user'] = 'yes'
        template = loader.get_template('quiz_result.html')
        return HttpResponse(template.render(context, request))