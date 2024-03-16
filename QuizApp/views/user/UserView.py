from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect, QueryDict, JsonResponse
from django.template import loader
from django.utils.decorators import method_decorator
from django.views import View

from QuizApp.forms import Signup
from QuizApp.models import User


class UserView(View):

    # display signup page
    def get(self, request):
        context = {'form': Signup}
        return HttpResponse(loader.get_template('signup.html').render(context, request))

    def post(self, request):
        form = Signup(request.POST)
        context = {'form': form}
        if form.is_valid():
            email = form.cleaned_data.get('email')
            pwd = form.cleaned_data.get('pwd')
            name = None
            username = email
            user = User(email=email, password=pwd)
            if len(form.cleaned_data['name']) > 0:
                name = form.cleaned_data['name']
                user.name = name
            if len(form.cleaned_data['username']) > 0:
                username = form.cleaned_data['username']
                user.username = username
            if not User.objects.filter(email=email).exists():
                try:
                    validate_password(pwd, user)
                    user.set_password(pwd)
                    user.save()
                    login(request, user)
                    request.session['email'] = email
                    request.session.modified = True
                    return HttpResponseRedirect('../home')
                except ValidationError as e:
                    form.add_error('pwd', e)
                    context['form'] = form
        return HttpResponse(loader.get_template('signup.html').render(context, request))

    # update user info
    def put(self, request):
        if request.user.is_authenticated:
            put = QueryDict(request.body)
            user = request.user
            errors = []
            if 'username' in put:
                if not User.objects.filter(username=put['username']).exists():
                    user.username = put['username']
                else:
                    errors.append('This username already exists')
            if 'email' in put:
                if check_password(put['pwd'], user.password):
                    if not User.objects.filter(email=put['email']).exists():
                        user.email = put['email']
                    else:
                        errors.append('This email already has an account')
                else:
                    errors.append("The given password doesn't match with your password")
            if 'old_pwd' in put:
                if check_password(put['old_pwd'], user.password):
                    user.set_password(put['pwd'])
                else:
                    errors.append('Make sure that your old password is correct')
            user.save()
            if len(errors) > 0:
                return JsonResponse({'errors': errors}, status=200)
            else:
                return JsonResponse({}, status=200)
        else:
            return HttpResponseRedirect('QuizApp/login')
