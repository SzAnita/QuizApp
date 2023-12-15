from django.urls import path
from . import views
from .views import CreateQuizView, AddQuestionView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('home', views.index, name='home'),
    path('signup/', views.signup),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='index.html')),
    path('quizzes/<str:quiz_title><int:quiz_id>', views.display_quiz),
    path('quizzes/result/<str:quiz_title><int:quiz_id>', views.check_result),
    #path('user/create_quiz', views.create_quiz),
    #path('user/add_question', views.add_question),
    path('user/add_question', AddQuestionView.as_view()),
    path('user/cancel_quiz', views.cancel_quiz),
    path('user/my_quizzes', views.my_quizzes),
    path('user/create_quiz', CreateQuizView.as_view())
]
