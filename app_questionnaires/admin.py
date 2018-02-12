from django.contrib import admin
from app_questionnaires.models import CustomUser, Questionnaire


admin.site.register(CustomUser)
admin.site.register(Questionnaire)

