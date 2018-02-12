
import json
import uuid
import shutil
import requests

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import View
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.models import User
from app_questionnaires.utility_factory import UtilityFactory
from app_questionnaires.perfectLO_client import PerfectLOClient
from app_questionnaires.models import CustomUser, Questionnaire, QuestionnaireStatuses


class Index(View):
    
    def get(self, request, *args, **kwargs):
    	
    	loanofficerId = settings.LOAN_OFFICER_UUID
    	custom_loan_officer= CustomUser.objects.get(uuid=settings.LOAN_OFFICER_UUID)
    	loan_officer_questionnaires = Questionnaire.objects.filter(created_by=custom_loan_officer)
        
        return render(request, "index.html", {"response_data" : loan_officer_questionnaires})


class CreateQuestionnaire(View):

	def get(self, request, *args, **kwargs):
		return render(request, "create_questionnaire.html")

	def post(self, request, *args, **kwargs):

		# =============================================== #
		# Calling the api for creating the borrower
		# =============================================== #

		lo_client = PerfectLOClient()
		response = lo_client.create_borrower(request.POST)
		borrower_id = response["success_data"]

		if not borrower_id and response['error'] and response['error_text']:
			messages.error(request, response['error_text'])
			return HttpResponseRedirect("/app/create_questionnaire/")

		new_base_user_instance = User()
		new_borrower_instance = CustomUser() 

		# Django auth user table
		new_base_user_instance.username = request.POST.get('BorrowerEmail')
		new_base_user_instance.email = request.POST.get('BorrowerEmail')
		new_base_user_instance.set_password(request.POST.get('BorrowerPWD'))
		new_base_user_instance.save()

		# Our custom user table
		new_borrower_instance.user = new_base_user_instance
		new_borrower_instance.uuid = borrower_id
		new_borrower_instance.first_name = request.POST.get('BorrowerFirstName')
		new_borrower_instance.middle_name = request.POST.get('BorrowerMiddleInitial')
		new_borrower_instance.last_name = request.POST.get('BorrowerLastName')
		new_borrower_instance.suffix = request.POST.get('BorrowerSuffix')
		new_borrower_instance.phone = request.POST.get('BorrowerHomePhone')
		new_borrower_instance.mobilephone = request.POST.get('BorrowerCellPhone')
		new_borrower_instance.save()

		# =============================================== #
		# Calling the api for creating the questionnaire
		# =============================================== #
		lo_client = PerfectLOClient()
		response = lo_client.create_questionnaire(request.POST, new_borrower_instance)
		questionnaire_id = response["success_data"]

		if not questionnaire_id and response['error'] :
			messages.error(request, response['error_text'])
			app_url = "/app/create_questionnaire/"

		# Check the status
		if questionnaire_id:
			custom_loan_officer = CustomUser.objects.get(uuid=settings.LOAN_OFFICER_UUID)
			questionnaire_instance = Questionnaire()
			questionnaire_instance.questionnaire_uuid = questionnaire_id
			questionnaire_instance.borrower = new_borrower_instance
			questionnaire_instance.created_by = custom_loan_officer
			questionnaire_instance.save()
			app_url = '/app/edit_questions/'+questionnaire_instance.questionnaire_uuid
		

		return HttpResponseRedirect(app_url)

class EditQuestions(View):

	def get(self, request, questionnaire_uuid=None, *args, **kwargs):

		lo_client = PerfectLOClient()

		response_data = ""
		next_question_definitionId = "LoanPurpose"
		
		try:
			questionnaire = Questionnaire.objects.get(questionnaire_uuid=questionnaire_uuid)
		except ObjectDoesNotExist:
			messages.error(request, "No questionnaire associated with this UUID")
			return HttpResponseRedirect("/app/")

		# =======If conditions - logic desc============= #    
		# 1 . For getting the previous question
		# 2 . For getting next question
		# 3 . For getting first question
		# ============================================== #
		if request.GET.get('q','') and request.GET.get('q') == 'back':
			questions_visited_list = json.loads(questionnaire.questionnaire_track)
			current_question_id_index = questions_visited_list.index(questionnaire.current_question_id)
			next_question_definitionId = questions_visited_list[current_question_id_index-1]

			questionnaire.previous_question_id = questionnaire.current_question_id
			questionnaire.current_question_id = next_question_definitionId
			questionnaire.save()

		elif request.GET.get('nextQuestionId'):
			next_question_definitionId = request.GET.get('nextQuestionId')
		else:
			response = lo_client.get_next_question_id(questionnaire_uuid)
			if response["success"]:
				next_question_definitionId = response["success_data"]

		# =============================================================== #
		# Logic for saving the questionID in a list and saving as JSON
		# =============================================================== #
		UtilityFactory.create_question_track(questionnaire, next_question_definitionId)

		# =========================================================== #
		# No more questions to ask . Just submit the questionnaire
		# =========================================================== #
		if next_question_definitionId in (0, '0'):
			trigger_url = "/app/submit_questionnaire/"+str(questionnaire_uuid)
			return HttpResponseRedirect(trigger_url)

		# =================================================== #
		# Get the questions using the next questionID
		# =================================================== #
		response = lo_client.get_question(questionnaire_uuid, next_question_definitionId)
		if response["success"]:
			response_data = response["success_data"]
			main_header = strip_tags(response_data['PromptText'])
		else:
			messages.error(request, response['error_text'])

		# =============================================== #
		# Creating the question HTML dynamically
		# =============================================== #
		strHTML = UtilityFactory.create_question_HTML(response_data)

		return render(request, "edit_questions.html", {
			"main_header":main_header, 
			"HTMLdata":strHTML, 
			"response_data" : json.dumps(response_data)
		})

	def json_loads_byteified(self, json_text):
	    return self._byteify(
	        json.loads(json_text, object_hook=self._byteify),
	        ignore_dicts=True
	    )

	def _byteify(self, data, ignore_dicts = False):
	    # if this is a unicode string, return its string representation
	    if isinstance(data, unicode):
	        return data.encode('utf-8')
	    # if this is a list of values, return list of byteified values
	    if isinstance(data, list):
	        return [ self._byteify(item, ignore_dicts=True) for item in data ]
	    # if this is a dictionary, return dictionary of byteified keys and values
	    # but only if we haven't already byteified it
	    if isinstance(data, dict) and not ignore_dicts:
	        return {
	            self._byteify(key, ignore_dicts=True): self._byteify(value, ignore_dicts=True)
	            for key, value in data.iteritems()
	        }
	    # if it's anything else, return it in its original form
	    return data


	def post(self, request, questionnaire_uuid=None, *args, **kwargs):
		
		post_data = request.POST
		hdn_response_data = post_data.get('hdn_response_val','')

		try:
			questionnaire = Questionnaire.objects.get(questionnaire_uuid=questionnaire_uuid)
		except ObjectDoesNotExist:
			messages.error(request, "No questionnaire associated with this UUID")
			return HttpResponseRedirect("/app/")

		response_data = hdn_response_data
		api_post_data = {"userId":str(questionnaire.borrower.uuid),  
						"questionnaireId":str(questionnaire_uuid),
						"data":""}	

		response_json_load_data = self.json_loads_byteified(response_data)
		# import pdb;pdb.set_trace()
		api_post_data['data'] = response_json_load_data

		# ======================================= #
		# Calling the api for posting the answer
		# ======================================= #
		lo_client = PerfectLOClient()
		response = lo_client.submit_question_answers(api_post_data)
		
		if response["success"]:
			nextQuestionId = response["success_data"]
			app_url = str('/app/edit_questions/')+str(questionnaire_uuid)+"?nextQuestionId="+str(nextQuestionId)
		else:
			messages.error(request, response['error_text'])
			app_url = "/app/"
			
		return HttpResponseRedirect(app_url)

class ResumeQuestionnaire(View):

	def get(self, request, questionnaire_uuid=None, *args, **kwargs):
		
		try:
			
			questionnaire = Questionnaire.objects.get(questionnaire_uuid=questionnaire_uuid)

			current_question_id = questionnaire.current_question_id
			if current_question_id and current_question_id not in ('0',0):
				trigger_url = str('/app/edit_questions/')+str(questionnaire_uuid)+"?nextQuestionId="+str(current_question_id)
			else:
				trigger_url = str('/app/edit_questions/')+str(questionnaire_uuid)

		except ObjectDoesNotExist:
			
			trigger_url = "/app/"
			messages.error(request, "No questionnaire associated with this UUID.")
			return HttpResponseRedirect("/app/")
		
		return HttpResponseRedirect(trigger_url)

class SubmitQuestionnaire(View):

	def get(self, request, questionnaire_uuid=None, *args, **kwargs):
		
		try:
			
			questionnaire = Questionnaire.objects.get(questionnaire_uuid=questionnaire_uuid)
			borrower_uuid = questionnaire.borrower.uuid
			loanofficer_uuid = questionnaire.created_by.uuid

			lo_client = PerfectLOClient()
			response = lo_client.submit_questionnaire(borrower_uuid, questionnaire_uuid, loanofficer_uuid)

			if response['success']:
				questionnaire.status = QuestionnaireStatuses.SUBMITTED
				questionnaire.save()
			elif response['error']:
				messages.error(request, response['error_text'])
			
		except ObjectDoesNotExist:		
			messages.error(request, "No questionnaire associated with this UUID.")
		
		return HttpResponseRedirect("/app/")


class ExportFile(View):

	def get(self, request, questionnaire_uuid=None, *args, **kwargs):

		response = HttpResponse(content_type='application/force-download')
		response['Content-Disposition'] = 'attachment; filename="somefilename.fnm"'

		try:
			
			questionnaire = Questionnaire.objects.get(questionnaire_uuid=questionnaire_uuid)
			borrower_uuid = questionnaire.borrower.uuid
		
			lo_client = PerfectLOClient()
			api_response = lo_client.export_file(questionnaire_uuid, borrower_uuid, )

			if api_response["success"]:
				response.write(api_response["success_data"])
			else:
				messages.error(request, api_response['error_text'])
		
		except ObjectDoesNotExist:
			messages.error(request, "No questionnaire associated with this UUID")
			return HttpResponseRedirect("/app/")

		return response


class ExportQuestionnaireSummary(View):

	def get(self, request, questionnaire_uuid=None, *args, **kwargs):

		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="summary.pdf"'

		try:

			questionnaire = Questionnaire.objects.get(questionnaire_uuid=questionnaire_uuid)
			borrower_uuid = questionnaire.borrower.uuid
		
			lo_client = PerfectLOClient()
			api_response = lo_client.export_questionnaire_summary(questionnaire_uuid, borrower_uuid, )

			if api_response["success"]:
				response.write(api_response["success_data"])
			else:
				messages.error(request, api_response['error_text'])

			return response

		except ObjectDoesNotExist:
			messages.error(request, "No questionnaire associated with this UUID")
			return HttpResponseRedirect("/app/")

		





























