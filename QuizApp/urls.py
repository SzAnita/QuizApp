from django.urls import path
import QuizApp
from QuizApp import views
from django.contrib.auth.views import LoginView, LogoutView
from QuizApp.views import quiz, index, user
from QuizApp.views.user import UserView as uv, user as u
from QuizApp.views.quiz import SolveQuizView as Solve, search as s, QuestionView as Question, my_quizzes as myq, \
    QuizView as Quiz, edit_quiz as edit, AnswerView as Answer, QuizGroupView as QuizGroup
#from QuizApp.views.quiz import search as s


urlpatterns = [
    path('home', index.index, name='home'),
    path('signup/', uv.UserView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='QuizApp/login'),
    path('logout/', LogoutView.as_view(template_name='index.html', next_page='home'), name='logout'),
    path('quizzes/<str:quiz_title><int:quiz_id>', Solve.SolveQuizView.as_view(), name='solve'),
    path('search', s.search, name='search'),
    path('user/create_quiz/question/<int:quiz_id>', Question.QuestionView.as_view(login_url='QuizApp/login'), name='create_quiz'),
    path('user/question', Question.QuestionView.as_view(login_url='QuizApp/login'), name='question'),
    path('user/my_quizzes', myq.my_quizzes, name='my_quizzes'),
    path('user/create_quiz', Quiz.QuizView.as_view(login_url='QuizApp/login'), name='quiz'),
    path('user/edit/<int:quiz_id>', edit.edit_quiz, name='edit'),
    path('user/answer', Answer.AnswerView.as_view(login_url='QuizApp/login'), name='answer'),
    path('report/<int:quiz_result_id>', u.user_report, name='user_report'),
    path('user', u.user_page, name='user'),
    path('user/quiz_group', QuizGroup.QuizGroupView.as_view(), name='quiz_group')
]
