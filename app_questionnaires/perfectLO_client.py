
import json
import requests
from django.conf import settings
import datetime


class PerfectLOClient:

	def __init__(self):
		self.response_dict = {"success":True, "error":False, "error_text":"", "success_data":""}

	def create_borrower(self, request_data):
		
		create_borrower_api_url = 'https://perfectlo-staging.azurewebsites.net/api/v1/borrowers?SubscriptionID={}'.format(settings.SUBSCRIPTION_ID)
		
		borrower_dict = {}
		borrower_id = ""

		borrower_dict['password'] = request_data.get('BorrowerPWD')
		borrower_dict['firstName'] = request_data.get('BorrowerFirstName')
		borrower_dict['lastName'] = request_data.get('BorrowerLastName')
		borrower_dict['email'] = request_data.get('BorrowerEmail')
		borrower_dict['loanOfficerId'] = settings.LOAN_OFFICER_UUID

		response = requests.post(create_borrower_api_url, data=borrower_dict)

		if response.status_code == 200:
			self.response_dict["success_data"] = response.json()
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"

		return self.response_dict

	def create_questionnaire(self, request_data, new_borrower_instance):

		create_questionnaire_api_url = "https://perfectlo-staging.azurewebsites.net/api/v1/questionnaires?SubscriptionID=%s&api_key=%s"%(settings.SUBSCRIPTION_ID, settings.SUBSCRIPTION_ID)
		
		questionnaire_id = ""
		questionnaires_payload = {}

		questionnaires_payload['title'] = request_data.get('BorrowerTitle')
		questionnaires_payload['firstname'] = request_data.get('BorrowerFirstName')
		questionnaires_payload['middleinitial'] = request_data.get('BorrowerMiddleInitial')
		questionnaires_payload['lastname'] = request_data.get('BorrowerLastName')
		questionnaires_payload['suffix'] = request_data.get('BorrowerSuffix')
		questionnaires_payload['email'] = request_data.get('BorrowerEmail')
		questionnaires_payload['phone'] = request_data.get('BorrowerHomePhone')
		questionnaires_payload['mobilephone'] = request_data.get('BorrowerCellPhone')
		questionnaires_payload['loanofficerId'] = settings.LOAN_OFFICER_UUID
		questionnaires_payload['borrowerId'] = new_borrower_instance.uuid
		questionnaires_payload['createdById'] = settings.LOAN_OFFICER_UUID

		questionnaires_response = requests.post(create_questionnaire_api_url, data=questionnaires_payload)

		if questionnaires_response.status_code == 200:
			self.response_dict["success_data"] = questionnaires_response.json()
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"

		return self.response_dict

	def get_next_question_id(self, questionnaire_uuid):
		"""
		Logic for saving the questionID in a list and saving as JSON
		"""
		next_question_definitionId = ''
		api_next_question_definition_url = "https://perfectlo-staging.azurewebsites.net/api/v1/questions/nextQuestionId"
		
		query_params_payload = {"SubscriptionID":settings.SUBSCRIPTION_ID,
						 		"api_key":settings.PERFECTLO_API_KEY,
						 		"QuestionnaireId":questionnaire_uuid}

		response = requests.get(api_next_question_definition_url, params=query_params_payload)

		if response.status_code == 200:
			if response.json():
				self.response_dict["success_data"] = response.json()
			else:
				self.response_dict["success_data"] = "LoanPurpose"
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"


		return self.response_dict

	def get_question(self, questionnaire_uuid, next_question_definitionId):
		
		response_data = {}
		api_questions_url = "https://perfectlo-staging.azurewebsites.net/api/v1/questions"

		query_params_payload = {"SubscriptionID":settings.SUBSCRIPTION_ID,
						 		"api_key":settings.PERFECTLO_API_KEY,
						 		"QuestionnaireId":questionnaire_uuid,
						 		"QuestionDefinitionId":next_question_definitionId}
		print ("***************GET QUESTION**************************")
		print (datetime.datetime.now())
		response = requests.get(api_questions_url, params=query_params_payload)
		print (datetime.datetime.now())

		if response.status_code == 200:
			self.response_dict["success_data"] = response.json()
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"

		return self.response_dict

		
	def submit_question_answers(self, api_post_data={}):
		
		nextQuestionId = ''
		api_question_post_url = "https://perfectlo-staging.azurewebsites.net/api/v1/questions?SubscriptionID=%s&api_key=%s"%(settings.SUBSCRIPTION_ID, settings.SUBSCRIPTION_ID)
		print ("***************SUBMIT ANSWERS**************************")
		print (datetime.datetime.now())
		# import pdb;pdb.set_trace()
		response = requests.post(api_question_post_url, json=api_post_data)
		print (datetime.datetime.now())
		if response.status_code == 200:
			nextQuestionId = response.json()
			self.response_dict["success_data"] = nextQuestionId
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"
		
		return self.response_dict


	def submit_questionnaire(self, borrowerId, questionnaireId, loanOfficerId):
		
		api_submit_questionnaire_url = "https://perfectlo-staging.azurewebsites.net/api/v1/submit?SubscriptionID=%s&api_key=%s"%(settings.SUBSCRIPTION_ID, settings.SUBSCRIPTION_ID)
		post_payload = {"borrowerId": str(borrowerId),
  						"questionnaireId": str(questionnaireId),
  						"loanOfficerId": str(loanOfficerId),
						"email": True
						} 
		response = requests.post(api_submit_questionnaire_url, json=post_payload)
		if response.status_code == 200:
			return self.response_dict
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"
			return self.response_dict

	def export_file(self, questionnaire_uuid, borrower_uuid):
		
		api_export_file_url = "https://perfectlo-staging.azurewebsites.net/api/v1/downloadexportfile"
		query_params_payload = {"SubscriptionID":settings.SUBSCRIPTION_ID,
						 		"api_key":settings.PERFECTLO_API_KEY,
						 		"QuestionnaireId":questionnaire_uuid,
						 		"BorrowerID":borrower_uuid}

		response = requests.get(api_export_file_url, params=query_params_payload, stream=True)

		if response.status_code == 200:
			self.response_dict["success_data"] = response.content
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"
		
		return self.response_dict


	def export_questionnaire_summary(self, questionnaire_uuid, borrower_uuid):

		api_export_summary_url = "https://perfectlo-staging.azurewebsites.net/api/v1/downloadquestionnairesummary"
		query_params_payload = {"SubscriptionID":settings.SUBSCRIPTION_ID,
						 		"api_key":settings.PERFECTLO_API_KEY,
						 		"QuestionnaireId":questionnaire_uuid,
						 		"BorrowerID":borrower_uuid}

		headers = {'Content-type': 'application/pdf', 'Accept': 'application/json'}
		response = requests.get(api_export_summary_url, params=query_params_payload)

		if response.status_code == 200:
			self.response_dict["success_data"] = response.content
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"
		
		return self.response_dict


	def get_questionnaire_summary_data(self, questionnaire_uuid, borrower_uuid):
		
		api_summary_url = "https://perfectlo-staging.azurewebsites.net/api/v1/downloadquestionnairesummary"
		query_params_payload = {"SubscriptionID":settings.SUBSCRIPTION_ID,
						 		"api_key":settings.PERFECTLO_API_KEY,
						 		"QuestionnaireId":questionnaire_uuid,
						 		"BorrowerID":borrower_uuid}

		headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
		response = requests.get(api_summary_url, params=query_params_payload, headers=headers)

		if response.status_code == 200:
			self.response_dict["success_data"] = response.json()
		else:
			self.response_dict["success"] = False
			self.response_dict["error"] = True
			self.response_dict["error_text"] = response.json() if response.json() else "API ERROR"
		
		return self.response_dict





