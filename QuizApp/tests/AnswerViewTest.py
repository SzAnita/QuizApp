import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizAppSettings.settings')
django.setup()

from django.test import TestCase, RequestFactory
from QuizApp.models import User, Quiz, Question, Answer
from django.urls import reverse
from QuizApp.views.quiz.AnswerView import AnswerView


class AnswerViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="anita", email="anita@yahoo.com",
                                             password="test_user")

    def test_add_answer_unique_for_question(self):
        """"
        A user can't add the same answer twice to the question
        """

        Quiz(owner_id=self.user, title="TestQuiz").save()
        quiz = Quiz.objects.get(owner_id=self.user, title="TestQuiz")

        Question(quiz_id=quiz, question="3+5=", type='SC', points=1).save()
        question = Question.objects.get(quiz_id=quiz, question="3+5=")

        Answer(quiz_id=quiz, question_id=question, answer="8", correct=True, point=1).save()

        # POST request with already existing question for quiz
        request1 = self.factory.post(reverse('answer'),
                                     {"question_id": question.id, "answer": "8", "points": 1, "correct": True})
        request1.user = self.user
        response1 = AnswerView.as_view()(request1)

        # Assertions for checking correct status code and content
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response1.content, b'{"msg": "This answer already exists. Please change it."}')

        # Assertion for checking the same answer hasn't been created more than once
        self.assertEqual(len(Answer.objects.filter(question_id=question, answer="8")), 1)

        # POST request with not yet existing question for the quiz
        request2 = self.factory.post(reverse('answer'),
                                     {"question_id": question.id, "answer": "10", "points": 1, "correct": True})
        request2.user = self.user
        response2 = AnswerView.as_view()(request2)

        # Assertion for checking correct status code
        self.assertEqual(response2.status_code, 201)

        # Assertion for checking that the answer has been created
        self.assertEqual(Answer.objects.filter(question_id=question, answer__iexact="10").exists(), True)

    def test_edit_answer_exists(self):
        """
        User can only edit existing answers
        """
        request = self.factory.put(reverse('answer'))
        request.user = self.user
        request.PUT = {'answer_id': "-1", "question": "test"}
        response = AnswerView.as_view()(request)
        self.assertEqual(Answer.objects.filter(id=-1).exists(), False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'{"msg": "This answer does not exist"}')

    def test_edit_answer_owned(self):
        """
        User can only edit questions that are his/her own
        """
        # setup answer to be updated
        Quiz(owner_id=self.user, title='TestQuiz').save()
        quiz = Quiz.objects.get(owner_id=self.user, title='TestQuiz')
        Question(quiz_id=quiz, question="3+5=").save()
        question = Question.objects.get(quiz_id=quiz, question="3+5=")
        Answer(quiz_id=quiz, question_id=question, answer="10", point=0).save()
        answer = Answer.objects.get(question_id=question, answer="10")

        # setup request
        request = self.factory.put(reverse('answer'))
        request.PUT = {"answer_id": answer.id, "answer": "9", 'correct': False, 'points': 0}
        request.user = User.objects.create_user(username="Luke", email="luke@yahoo.com", password='luke')
        response1 = AnswerView.as_view()(request)
        self.assertEqual(response1.status_code, 401)

        request.user = self.user
        response2 = AnswerView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

        answer.refresh_from_db()
        self.assertEqual(answer.answer, "9")

    def test_edited_answer_unique(self):
        """"
        Edited answer can't be the same as another answer of the question
        """
        # setup answer to be updated
        Quiz(owner_id=self.user, title='TestQuiz').save()
        quiz = Quiz.objects.get(owner_id=self.user, title='TestQuiz')
        Question(quiz_id=quiz, question="3+5=").save()
        question = Question.objects.get(quiz_id=quiz, question="3+5=")
        Answer(quiz_id=quiz, question_id=question, answer="10", point=0).save()
        answer = Answer.objects.get(question_id=question, answer="10")
        Answer(quiz_id=quiz, question_id=question, answer="9", point=0).save()

        # setup request1
        request = self.factory.put(reverse('answer'))
        request.PUT = {"answer_id": answer.id, "answer": "9", 'correct': False, 'points': 0}
        request.user = self.user
        response1 = AnswerView.as_view()(request)
        self.assertEqual(response1.status_code, 406)
        self.assertEqual(response1.content, b'{"msg": "This answer already exists."}')

        request.PUT['answer'] = '7'
        response2 = AnswerView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

    def test_delete_question_exists(self):
        """"
        User can only delete existing question
        """
        request = self.factory.delete(reverse('answer'))
        request.user = self.user
        request.DELETE = {'answer_id': "-1"}
        response = AnswerView.as_view()(request)
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
        Answer(quiz_id=quiz, question_id=question, answer="10", point=0).save()
        answer = Answer.objects.get(question_id=question, answer="10")

        # setup request
        request = self.factory.delete(reverse('answer'))
        request.DELETE = {"answer_id": answer.id}
        request.user = User.objects.create_user(username="Luke", email="luke@yahoo.com", password='luke')
        response1 = AnswerView.as_view()(request)
        self.assertEqual(response1.status_code, 401)

        request.user = self.user
        response2 = AnswerView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

        self.assertEqual(Answer.objects.filter(quiz_id__owner_id=request.user, answer="10").exists(), False)