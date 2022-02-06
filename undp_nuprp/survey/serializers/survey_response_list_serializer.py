from rest_framework.serializers import ListSerializer

from undp_nuprp.survey.models.response.question_response import QuestionResponse


class SurveyResponseListSerializer(ListSerializer):
    @property
    def data(self):
        _data = super(SurveyResponseListSerializer, self).data
        id_vs_response_object = dict()
        for each_data in _data:
            _id = each_data["id"]
            id_vs_response_object[_id] = each_data
        questions_queryset = QuestionResponse.objects.filter(
            section_response__survey_response_id__in=id_vs_response_object.keys()).values(
            "section_response__survey_response_id", "id", 'tsync_id', 'question', 'question__question_code',
            'question__order', 'answer', 'answer__answer_code', 'question_text', 'answer_text', 'index', 'date_created',
            'last_updated'
        )
        for question in questions_queryset:
            _survey_id = question["section_response__survey_response_id"]
            _id = question["id"]
            _tsync_id = question["tsync_id"]
            _parent_tsync_id = id_vs_response_object[_survey_id]["tsync_id"]
            _question = question["question"]
            _question_code = question['question__question_code']
            _question_order = question['question__order']
            _answer = question["answer"]
            _answer_code = question["answer__answer_code"]
            _question_text = question["question_text"]
            _answer_text = question["answer_text"]
            _index = question["index"]
            _date_created = question["date_created"]
            _last_updated = question["last_updated"]

            question_object = {
                "id": _id,
                "tsync_id": _tsync_id,
                "parent_tsync_id": _parent_tsync_id,
                "question": _question,
                "question_code": _question_code,
                "question_order": _question_order,
                "answer": _answer,
                "answer_code": _answer_code,
                "question_text": _question_text,
                "answer_text": _answer_text,
                "index": _index,
                "date_created": _date_created,
                "last_updated": _last_updated
            }

            if "questions" not in id_vs_response_object[_survey_id]:
                id_vs_response_object[_survey_id]['questions'] = list()
            question_list = id_vs_response_object[_survey_id]['questions']
            question_list.append(question_object)

        return _data
