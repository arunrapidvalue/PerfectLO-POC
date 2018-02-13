import json
from django.conf import settings


class UtilityFactory(object):

    @staticmethod
    def create_question_track(questionnaire=None, next_question_definitionId=""):

        if not questionnaire.questionnaire_track:
            question_id_list = []
        else:
            question_id_list = json.loads(questionnaire.questionnaire_track)

        if questionnaire.current_question_id != next_question_definitionId:
            questionnaire.previous_question_id = questionnaire.current_question_id

        questionnaire.current_question_id = next_question_definitionId

        if questionnaire.current_question_id not in question_id_list:
            question_id_list.append(questionnaire.current_question_id)

        questionnaire.questionnaire_track = json.dumps(question_id_list)
        questionnaire.save()

    @staticmethod
    def create_question_HTML(response_data={}):

        # ========================== #
        # Primary div start here
        # ========================== # 
        loop_index = 0
        strHTML = """<div class="col-md-12">"""
        master_content = response_data["AnswersGroups"]

        for sub_content in master_content:

            # ======================================================== #
            # This is mainly introduced for BankDetails as there 
            # will be an add account option . But for POC just showing
            # all the entries.
            # ======================================================== # 
            loop_index += 1
            if loop_index > 1:
                strHTML += "<br><hr><br>"

            sub_content_looper = 0
            for each in sub_content:

                sub_content_looper += 1

                is_dropdown = False
                is_check_box = False
                is_radio = False
                is_textbox = False
                is_currency_textbox = False
                answer_type = each['AnswerType']
                name = each['Name']
                id_name = ""

                if name in (None, '', ""):
                    name = ""

                if settings.ANSWER_TYPE[str(answer_type)] == "check_box":

                    # write a method that fetches the data and gives everything back
                    is_check_box = True
                    strHTML += """<div class="row"><label class="form-check-label">%s</label><ul>""" % (name)
                    raw_data = """<li><input name="SelectedAnswersList" value="%s" id="%s" promtData="%s" api_answer="%s" class="form-check-input" type="checkbox" %s>
                                <label class="form-check-label" for="%s">%s</label></li>"""

                elif settings.ANSWER_TYPE[str(answer_type)] == "radio_button":

                    if name or len(each['AnswerList']) > 11:

                        is_dropdown = True
                        strHTML += """<div class="row"><div class="col-md-3"><label class="form-check-label">%s</label></div>""" % (
                            name)
                        if name:
                            id_name = name.replace(" ", "")
                        else:
                            id_name = str(sub_content_looper)
                        strHTML += """<div class="col-md-4"><select classs="form-control" style="width:50%%" name="dropdown_list" id="%s">""" % (
                                    "id_" + id_name)
                        raw_data = """<option value="%s" %s>%s</option>"""

                    else:

                        is_radio = True
                        strHTML += """<div class="row"><label class="form-check-label">%s</label><ul>""" % (name)
                        raw_data = """<li><input class="form-check-input" value="%s" id="%s" promtData="%s" api_answer="%s" name="SelectedAnswer" type="radio" %s>
                                         <label class="form-check-label" for="%s">%s</label></li>"""

                elif settings.ANSWER_TYPE[str(answer_type)] == "dollar_text_box":

                    is_currency_textbox = True
                    strHTML += """<div class="row">"""
                    if name:
                        strHTML += """<div class="col-md-3"><label class="form-check-label">%s</label></div>""" % (name)
                    raw_data = """<div class="col-md-4"><input name="text_string_value" id="%s" class="form-control comma-formatted-decimal" placeholder="0" pattern="[0-9]*" type="tel" value="%s"></div>
                    <span class="input-group-addon">$</span></div> """

                elif settings.ANSWER_TYPE[str(answer_type)] == "text_box":

                    is_textbox = True
                    strHTML += """<div class="row">"""
                    if name:
                        strHTML += """<div class="col-md-3"><label class="form-check-label">%s</label></div>""" % (name)
                    raw_data = """<div class="col-md-4"><input class="form-control min-width-200 text-box single-line" id="%s" name="text_string_value" value="%s" type="text"></div></div> """

                answer_looper = 0
                for questions in each['AnswerList']:

                    answer_looper += 1
                    value = questions["value"]
                    prompt_data = ""
                    current_value = ''
                    prompt_text = questions["PromptText"]
                    if prompt_text:
                        prompt_data = (questions["PromptText"]).replace(" ", "").replace("(", "").replace(")",
                                                                                                          "").replace(
                            ",", "").replace("/", "").replace("+", "")

                        # This is to fix ascii issues
                    try:
                        # element_id =  "id_"+ str(prompt_data)
                        element_id = "id_" + str(answer_looper) + '_' + str(sub_content_looper)
                    except:
                        stripped = lambda elem: "".join(i for i in elem if 31 < ord(i) < 127)
                        prompt_data = stripped(prompt_data)
                        element_id = "id_" + str(prompt_data)

                    answer_data = questions['APIAnswer']

                    if is_dropdown:
                        if value:
                            current_value = "selected"
                        strHTML += raw_data % (answer_data, current_value, prompt_text)

                    if is_textbox or is_currency_textbox:
                        text_box_id = "id_" + str(answer_looper) + '_' + str(sub_content_looper)
                        if value:
                            current_value = value
                        strHTML += raw_data % (text_box_id, current_value)

                    if is_check_box or is_radio:
                        if value:
                            current_value = "checked"
                        strHTML += raw_data % (
                        value, element_id, prompt_data, answer_data, current_value, element_id, prompt_text)

                if is_dropdown:
                    strHTML += """</select></div></div>"""

                if is_check_box or is_radio:
                    strHTML += """</ul></div>"""

            # ================================ #
            # Primary div close here
            # ================================ #
            strHTML += """</div>"""

        return strHTML
