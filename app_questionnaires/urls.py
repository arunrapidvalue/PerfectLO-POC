"""perfectLO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from .views import *

urlpatterns = [

    #This will be the index page
    url(r'^$', Index.as_view(), name="Index"),
    url(r'^create_questionnaire/$', CreateQuestionnaire.as_view(), name="CreateQuestionnaire"),
    url(r'^edit_questions/(?P<questionnaire_uuid>[-\w]+)/$', EditQuestions.as_view(), name="EditQuestions"),
    url(r'^resume_questionnaire/(?P<questionnaire_uuid>[-\w]+)/$', ResumeQuestionnaire.as_view(), name="ResumeQuestionnaire"),
    url(r'^submit_questionnaire/(?P<questionnaire_uuid>[-\w]+)/$', SubmitQuestionnaire.as_view(), name="SubmitQuestionnaire"),
    url(r'^export_file/(?P<questionnaire_uuid>[-\w]+)/$', ExportFile.as_view(), name="ExportFile"),
    url(r'^questionnaire_summary/(?P<questionnaire_uuid>[-\w]+)/$', ExportQuestionnaireSummary.as_view(), name="ExportQuestionnaireSummary"),

]
