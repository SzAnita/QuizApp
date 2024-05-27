from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, QueryDict, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView

from QuizApp.forms import Signup
from QuizApp.models import User


class SignUpView(CreateView):
    model = User
    form_class = Signup
    template_name = 'authentication/signup.html'

    def form_valid(self, form):
        login(self.request, form.save())
        return HttpResponseRedirect(reverse('home'))


class UserView(LoginRequiredMixin, View):
    login_url = 'QuizApp/login'

    # update user info
    def put(self, request):
        put = QueryDict(request.body)
        if hasattr(request, 'PUT'):
            put = request.PUT
        user = request.user
        errors = []
        if 'username' in put:
            if not User.objects.filter(username=put['username']).exists():
                user.username = put['username']
            else:
                errors.append('This username already exists')
        elif 'email' in put:
            if check_password(put['pwd'], user.password):
                if not User.objects.filter(email=put['email']).exists():
                    user.email = put['email']
                else:
                    errors.append('This email already has an account')
            else:
                errors.append("The given password doesn't match with your password")
        elif 'old_pwd' in put:
            if check_password(put['old_pwd'], user.password):
                try:
                    validate_password(put['pwd'])
                    user.set_password(put['pwd'])
                except ValidationError:
                    errors.append('Make sure to provide a valid password')
            else:
                errors.append('Make sure that your old password is correct')
        user.save()
        if len(errors) > 0:
            return JsonResponse({'errors': errors}, status=400)
        else:
            return JsonResponse({}, status=200)
