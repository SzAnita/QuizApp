import json
import os, django

from django.http import QueryDict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizAppSettings.settings')
django.setup()

from django.test import TestCase, RequestFactory
from QuizApp.models import User, Quiz, QuizGroup
from QuizApp.views.quiz.QuizGroupView import QuizGroupView
from django.urls import reverse


class QuizViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="anita", email="anita@yahoo.com",
                                             password="test_user")

    def test_add_quizgroup_unique(self):
        """
        Users can't create quizgroups that have the same name
        """
        QuizGroup(owner_id=self.user, name="TestGroup").save()
        quiz_group = QuizGroup.objects.get(owner_id=self.user, name='TestGroup')

        # Post request with same name
        request1 = self.factory.post(reverse('quiz_group'), {'group': 'TestGroup'})
        request1.user = self.user
        response1 = QuizGroupView.as_view()(request1)
        self.assertEqual(response1.content, b'{"msg": "You already have a quiz group with this name."}')
        self.assertEqual(response1.status_code, 406)
        self.assertEqual(len(QuizGroup.objects.filter(owner_id=self.user, name="TestGroup")), 1)

        # Post request with different name
        request2 = self.factory.post(reverse('quiz_group'), {'group': 'MyGroup'})
        request2.user = self.user
        response2 = QuizGroupView.as_view()(request2)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(json.loads(response2.content)['group_name'], 'MyGroup')
        self.assertEqual(QuizGroup.objects.filter(owner_id=self.user, name='MyGroup').exists(), True)

    def test_edit_quizgroup_exists(self):
        """
        User can only edit existing quiz groups
        """
        # setup quiz group to be edited
        QuizGroup(owner_id=self.user, name="TestGroup").save()
        quiz_group = QuizGroup.objects.get(owner_id=self.user, name='TestGroup')

        # setup request
        request = self.factory.put(reverse('quiz_group'))
        request.user = self.user
        request.PUT = {'type': 'name', 'old_name': 'Test', 'new_name': 'Group1'}
        response = QuizGroupView.as_view()(request)
        self.assertEqual(response.content, b'{"msg": "This quiz group doesn\'t exist"}')
        self.assertEqual(response.status_code, 404)

    def test_edited_quiz_group_unique(self):
        """
        Edited quiz group's name must be different from user's
        other quiz groups' names
        """
        # setup quiz group to be edited
        QuizGroup(owner_id=self.user, name="TestGroup").save()
        quiz_group = QuizGroup.objects.get(owner_id=self.user, name='TestGroup')
        QuizGroup(owner_id=self.user, name="Group2").save()

        # setup request with already existing quiz group name
        request = self.factory.put(reverse('quiz_group'))
        request.user = self.user
        request.PUT = {'type': 'name', 'old_name': 'TestGroup', 'new_name': 'Group2'}
        response1 = QuizGroupView.as_view()(request)
        self.assertEqual(response1.content, b'{"msg": "You already have a quiz group with this name."}')
        self.assertEqual(response1.status_code, 409)
        self.assertEqual(len(QuizGroup.objects.filter(owner_id=self.user, name='Group2')), 1)

        request.PUT['new_name'] = 'MyGroup'
        response2 = QuizGroupView.as_view()(request)
        self.assertEqual(response2.status_code, 200)
        quiz_group.refresh_from_db()
        self.assertEqual(quiz_group.name, "MyGroup")

    def test_add_or_remove_quiz_exists_to_quiz_group(self):
        """
        Only existing quizzes can be added/removed to a quiz group
        """
        # setup request
        request = self.factory.put(reverse('quiz_group'))
        request.PUT = {'type': 'add', 'quiz_id': -1}

        # response for adding quiz
        response1 = QuizGroupView.as_view()(request)
        self.assertEqual(response1.content, b'{"msg": "This quiz doesn\'t exist"}')
        self.assertEqual(response1.status_code, 404)

        # response for removing quiz
        request.PUT['type'] = 'remove'
        response2 = QuizGroupView.as_view()(request)
        self.assertEqual(response2.content, b'{"msg": "This quiz doesn\'t exist"}')
        self.assertEqual(response2.status_code, 404)

    def test_add_quiz_to_quiz_group_exists(self):
        """
        Users can only add quiz to existing quiz group(s)
        """
        # setup quiz and quiz groups
        QuizGroup(owner_id=self.user, name="TestGroup").save()
        quiz_group = QuizGroup.objects.get(owner_id=self.user, name='TestGroup')
        QuizGroup(owner_id=self.user, name="Group2").save()
        Quiz(owner_id=self.user, title="TestQuiz").save()
        quiz = Quiz.objects.get(owner_id=self.user, title="TestQuiz")

        request = self.factory.put(reverse('quiz_group'))
        request.PUT = {'type': 'add', 'quiz_id': quiz.id, 'groups[]': ['Test']}

        response1 = QuizGroupView.as_view()(request)
        self.assertEqual(response1.status_code, 404)
        self.assertEqual(response1.content, b'{"msg": "This quiz group doesn\'t exist}')

    def test_remove_quiz_from_quiz_group_exists(self):
        """
        Users can only remove a quiz from an existing quiz group
        """
        Quiz(owner_id=self.user, title="TestQuiz").save()
        quiz = Quiz.objects.get(owner_id=self.user, title='TestQuiz')
        QuizGroup(owner_id=self.user, name='Group1').save()
        group = QuizGroup.objects.get(owner_id=self.user, name='Group1')

        # setup request
        request = self.factory.put(reverse('quiz_group'))
        request.user = self.user
        request.PUT = {'type': 'remove', 'group_id': -1, 'quiz_id': quiz.id}
        response1 = QuizGroupView.as_view()(request)
        self.assertEqual(response1.status_code, 404)
        self.assertEqual(json.loads(response1.content)['msg'], "This quiz group doesn't exist")

        request.PUT['group_id'] = group.id
        group.quizzes.add(quiz)
        group.save()
        self.assertEqual(QuizGroup.objects.filter(id=group.id, quizzes__id=quiz.id).exists(), True)
        response2 = QuizGroupView.as_view()(request)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(QuizGroup.objects.filter(id=group.id, quizzes__id=quiz.id).exists(), False)

    def test_delete_quiz_group_exists(self):
        """
        Users can only delete existing quiz groups
        """
        QuizGroup(owner_id=self.user, name='Group1').save()
        group = QuizGroup.objects.get(owner_id=self.user, name='Group1')

        request = self.factory.delete(reverse('quiz_group'))
        request.user = self.user
        request.DELETE = {'group_id': -1}
        response1 = QuizGroupView.as_view()(request)
        self.assertEqual(response1.status_code, 404)
        self.assertEqual(json.loads(response1.content)['msg'], "This group doesn't exist")

        request.DELETE['group_id'] = group.id
        response2 = QuizGroupView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

    def test_delete_quiz_group_owned(self):
        """
        Users can delete only their own quiz groups
        """
        # setup quiz group and user
        QuizGroup(owner_id=self.user, name='Group1').save()
        group = QuizGroup.objects.get(owner_id=self.user, name='Group1')

        request = self.factory.delete(reverse('quiz_group'))
        request.DELETE = {'group_id': group.id}
        request.user = User.objects.create_user(email="luke@yahoo.com", username="luke", password='luke_pwd')
        response1 = QuizGroupView.as_view()(request)
        self.assertEqual(response1.status_code, 401)
        self.assertEqual(QuizGroup.objects.filter(owner_id=self.user, name='Group1').exists(), True)

        request.user = self.user
        response2 = QuizGroupView.as_view()(request)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(QuizGroup.objects.filter(owner_id=self.user, name='Group1').exists(), False)
