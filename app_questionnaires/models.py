from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from django.contrib.auth.models import User


class QuestionnaireStatuses(object):
	INPROGRESS = 0
	COMPLETED = 1
	SUBMITTED = 2
	DELETED = 3


class UserType(object):
	BORROWER = 1
	LOAN_OFFICIER = 2


class CustomUser(models.Model):
	USER_TYPE = [(UserType.BORROWER, "Borrower"),
		(UserType.LOAN_OFFICIER, "Loan Officier")]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
	user_type = models.IntegerField(choices=USER_TYPE, default=1)
	uuid = models.CharField(max_length=100)
	first_name = models.CharField(max_length=100)
	middle_name = models.CharField(max_length=100, blank=True, null=True)
	last_name = models.CharField(max_length=100)
	suffix = models.CharField(max_length=20, blank=True, null=True)
	home_phone = models.CharField(max_length=100, blank=True, null=True)
	cell_phone = models.CharField(max_length=100, blank=True, null=True)

	def __unicode__(self):
	   return self.first_name+" "+self.last_name


class Questionnaire(models.Model):

	"""
	Questionnaire status
	"""
	QUESTIONNAIRE_STATUSES = [(QuestionnaireStatuses.INPROGRESS, "Inprogress"),
                       		  (QuestionnaireStatuses.COMPLETED, "Completed"),
                              (QuestionnaireStatuses.SUBMITTED, "Submitted"),
                              (QuestionnaireStatuses.DELETED, "Deleted")]

	questionnaire_uuid = models.CharField(max_length=100)
	loan_officier = models.ForeignKey(CustomUser, related_name="loan_officier", blank=True, null=True)
	borrower = models.ForeignKey(CustomUser, related_name="borrower", blank=True, null=True)
	previous_question_id = models.CharField(max_length=50, blank=True, null=True)
	current_question_id = models.CharField(max_length=50, blank=True, null=True)
	questionnaire_track = models.TextField(blank=True, null=True)
	created_by = models.ForeignKey(CustomUser, related_name="created_by", blank=True, null=True)
	created_datetime = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(choices=QUESTIONNAIRE_STATUSES, default=QuestionnaireStatuses.INPROGRESS)

	def __unicode__(self):
	   return self.questionnaire_uuid