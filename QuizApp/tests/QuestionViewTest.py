import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizAppSettings.settings')
django.setup()

from django.test import TestCase, RequestFactory
from QuizApp.models import User, Quiz, Question
from django.urls import reverse
from QuizApp.views.quiz.QuestionView import QuestionView


class QuestionViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="anita", email="anita@yahoo.com",
                                             password="test_user")

    def test_add_question_unique_in_quiz(self):
        """
        A user can't add the same question twice to the same quiz
        """
        Quiz(owner_id=self.user, title="TestQuiz").save()
        quiz = Quiz.objects.get(owner_id=self.user, title="TestQuiz")
        Question(quiz_id=quiz, question="3+5=", type='SC').save()

        # POST request with already existing question for quiz
        request1 = self.factory.post(reverse('question'),
                                     {"quiz_id": quiz.id, "question": "3+5=", "type": "SC", "finish": False})
        request1.user = self.user
        response1 = QuestionView.as_view()(request1)
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response1.content, b'{"msg": "This question already exists. Please change it"}')
        self.assertEqual(len(Question.objects.filter(quiz_id=quiz, question="3+5=")), 1)

        # POST request with not yet existing question for the quiz
        request2 = self.factory.post(reverse('question'),
                                     {"quiz_id": quiz.id, "question": "4+7=", "type": "SC", "finish": False})
        request2.user = self.user
        response2 = QuestionView.as_view()(request2)

        # Assertions about the responses' status and content
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(Question.objects.filter(quiz_id=quiz, question="4+7=", type='SC').exists(), True)

    def test_edit_question_exists(self):
        """
        User can only edit existing questions
        """
        request = self.factory.put(reverse('question'))
        request.user = self.user
        request.PUT = {'question_id': "-1", "question": "test"}
        response = QuestionView.as_view()(request)
        self.assertEqual(Question.objects.filter(id=-1).exists(), False)
        self.assertEqual(response.status_code, 404)

    def test_edit_question_owned(self):
        """
        User can only edit questions that are his/her own
        """
        # setup question to be updated
        Quiz(owner_id=self.user, title='TestQuiz').save()
        quiz = Quiz.objects.get(owner_id=self.user, title='TestQuiz')
        Question(quiz_id=quiz, question="3+5=", type='SC').save()
        question = Question.objects.get(quiz_id=quiz, question="3+5=")

        # setup request
        request = self.factory.put(reverse('question'))
        request.PUT = {"question_id": question.id, "question": "9-3="}
        request.user = User.objects.create_user(username="Luke", email="luke@yahoo.com", password='luke')
        response1 = QuestionView.as_view()(request)
        self.assertEqual(response1.status_code, 401)

        request.user = self.user
        response2 = QuestionView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

        question.refresh_from_db()
        self.assertEqual(question.question, "9-3=")

    def test_edited_question_unique(self):
        """
        Edited question has to be different from the other questions in the quiz
        """
        # setup question to be updated
        Quiz(owner_id=self.user, title='TestQuiz').save()
        quiz = Quiz.objects.get(owner_id=self.user, title='TestQuiz')
        Question(quiz_id=quiz, question="3+5=", type='SC').save()
        question = Question.objects.get(quiz_id=quiz, question="3+5=")
        Question(quiz_id=quiz, question="9-3=").save()

        # setup request
        request = self.factory.put(reverse('question'))
        request.PUT = {"question_id": question.id, "question": "9-3="}
        request.user = self.user
        response1 = QuestionView.as_view()(request)
        self.assertEqual(response1.status_code, 406)
        self.assertEqual(response1.content, b'{"msg": "This question already exists"}')

        request.PUT['question'] = '9+3='
        response2 = QuestionView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

    def test_delete_question_exists(self):
        """"
        User can only delete existing question
        """
        request = self.factory.delete(reverse('question'))
        request.user = self.user
        request.DELETE = {'question_id': "-1"}
        response = QuestionView.as_view()(request)
        self.assertEqual(Quiz.objects.filter(id=-1).exists(), False)
        self.assertEqual(response.status_code, 404)

    def test_delete_question_owned(self):
        """
        User can only delete his/her own questions
        """

        # setup question to be deleted
        Quiz(owner_id=self.user, title='TestQuiz').save()
        quiz = Quiz.objects.get(owner_id=self.user, title='TestQuiz')
        Question(quiz_id=quiz, question="3+5=").save()
        question = Question.objects.get(quiz_id=quiz, question="3+5=")

        # setup request
        request = self.factory.delete(reverse('question'))
        request.DELETE = {"question_id": question.id}
        request.user = User.objects.create_user(username="Luke", email="luke@yahoo.com", password='luke')
        response1 = QuestionView.as_view()(request)
        self.assertEqual(response1.status_code, 401)

        request.user = self.user
        response2 = QuestionView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

        self.assertEqual(Question.objects.filter(quiz_id__owner_id=request.user, question="3+5=").exists(), False)
