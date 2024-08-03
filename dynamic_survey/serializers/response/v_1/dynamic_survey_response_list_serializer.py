from dynamic_survey.models import DynamicQuestionResponse
from rest_framework.serializers import ListSerializer


class DynamicSurveyResponseListSerializer(ListSerializer):
    @property
    def data(self):
        _data = super(DynamicSurveyResponseListSerializer, self).data
        id_vs_response_object = dict()
        for each_data in _data:
            _id = each_data["id"]
            id_vs_response_object[_id] = each_data
        questions_queryset = DynamicQuestionResponse.objects.filter(
            section_response__survey_response_id__in=id_vs_response_object.keys()).values(
            "section_response__survey_response_id", "id", 'tsync_id', 'question', 'answer', 'question_text',
            'answer_text', 'index', 'date_created', 'last_updated', "photo", "photo__tsync_id", "photo__date_created",
            "photo__last_updated"
        )
        for question in questions_queryset:
            _survey_id = question["section_response__survey_response_id"]
            _id = question["id"]
            _tsync_id = question["tsync_id"]
            _parent_tsync_id = id_vs_response_object[_survey_id]["tsync_id"]
            _question = question["question"]
            _answer = question["answer"]
            _question_text = question["question_text"]
            _answer_text = question["answer_text"]
            _index = question["index"]
            _date_created = question["date_created"]
            _last_updated = question["last_updated"]
            _photo_id = question["photo"]
            _photo_tsync_id = question["photo__tsync_id"]
            _photo_date_created = question["photo__date_created"]
            _photo_last_updated = question["photo__last_updated"]
            question_object = {
                "id": _id,
                "tsync_id": _tsync_id,
                "parent_tsync_id": _parent_tsync_id,
                "question": _question,
                "answer": _answer,
                "question_text": _question_text,
                "answer_text": _answer_text,
                "index": _index,
                "date_created": _date_created,
                "last_updated": _last_updated
            }
            if _photo_id:
                photo_object = {
                    "id": _photo_id,
                    "tsync_id": _photo_tsync_id,
                    "date_created": _photo_date_created,
                    "last_updated": _photo_last_updated
                }
                question_object.update(photo=photo_object)
                if "photos" not in id_vs_response_object[_survey_id]:
                    id_vs_response_object[_survey_id]['photos'] = list()
                photo_list = id_vs_response_object[_survey_id]['photos']
                photo_list.append(question_object)

            else:
                if "questions" not in id_vs_response_object[_survey_id]:
                    id_vs_response_object[_survey_id]['questions'] = list()
                question_list = id_vs_response_object[_survey_id]['questions']
                question_list.append(question_object)
        return _data
