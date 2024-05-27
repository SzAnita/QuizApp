import json
import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizAppSettings.settings')
django.setup()

from django.test import TestCase, RequestFactory
from QuizApp.models import User, Quiz
from QuizApp.views.user.UserView import UserView
from django.urls import reverse

class UserViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="anita", email="anita01@yahoo.com",
                                             password="test_user")
        self.user2 = User.objects.create_user(username="luke", email="luke@yahoo.com",
                                             password="test_luke")

    def test_edited_username_unique(self):
        request = self.factory.put(reverse('user_edit'))
        request.user = self.user
        request.PUT = {"username": "luke"}

        response1 = UserView.as_view()(request)
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(json.loads(response1.content)['errors'], ['This username already exists'])

        request.PUT['username'] = '_anita_'
        response2 = UserView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

    def test_edit_email_pwd_correct(self):
        request = self.factory.put(reverse('user_edit'))
        request.user = self.user
        request.PUT = {'email': 'anita01@gmail.com', 'pwd': 'test'}

        response1 = UserView.as_view()(request)
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(json.loads(response1.content)['errors'], ["The given password doesn't match with your password"])

        request.PUT['pwd'] = 'test_user'
        response2 = UserView.as_view()(request)
        self.assertEqual(response2.status_code, 200)


    def test_edited_email_unique(self):
        request = self.factory.put(reverse('user_edit'))
        request.user = self.user
        request.PUT = {'email': 'luke@yahoo.com', 'pwd': 'test_user'}

        response1 = UserView.as_view()(request)
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(json.loads(response1.content)['errors'], ["This email already has an account"])

        request.PUT['email'] = 'anita_@gmail.com'
        response2 = UserView.as_view()(request)
        self.assertEqual(response2.status_code, 200)


    def test_edit_pwd_old_pwd_correct(self):
        request = self.factory.put(reverse('user_edit'))
        request.user = self.user
        request.PUT = {'old_pwd': 'test', 'pwd': '#testAnita24'}

        response1 = UserView.as_view()(request)
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(json.loads(response1.content)['errors'],
                         ["Make sure that your old password is correct"])

        request.PUT['old_pwd'] = 'test_user'
        response2 = UserView.as_view()(request)
        self.assertEqual(response2.status_code, 200)

    def test_edit_pwd_valid(self):
        request = self.factory.put(reverse('user_edit'))
        request.user = self.user
        request.PUT = {'old_pwd': 'test_user', 'pwd': 'test_anita'}

        response1 = UserView.as_view()(request)
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(json.loads(response1.content)['errors'],
                         ["Make sure to provide a valid password"])

        request.PUT['pwd'] = '#testAnita24'
        response2 = UserView.as_view()(request)
        self.assertEqual(response2.status_code, 200)