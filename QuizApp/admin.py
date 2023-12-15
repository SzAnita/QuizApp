from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

admin.site.register(User, UserAdmin)
admin.site.register(QuizGroup)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionResult)
admin.site.register(QuizResult)
