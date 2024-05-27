from django.views.generic import TemplateView
from QuizApp.models import Quiz, QuizGroup, User


class HomeView(TemplateView):
    template_name = 'index.html'
    extra_context = {
        'auth': 'no',
        'group': 'false',
        'quizzes': Quiz.objects.filter(public=True).values()
    }
    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.user.is_authenticated:
            context['auth'] = 'yes'
            context['group'] = 'true'
            context['groups'] = QuizGroup.objects.filter(owner_id=request.user)
        return self.render_to_response(context)