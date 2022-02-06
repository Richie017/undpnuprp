import uuid
from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from blackwidow.core.models import Location, ErrorLog, ImageFileObject
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from dynamic_survey.models import DynamicSurveyResponse
from dynamic_survey.serializers.response.v_1.dynamic_survey_response_list_serializer import \
    DynamicSurveyResponseListSerializer


class DynamicSurveyResponseSerializer(OrganizationDomainEntity.get_serializer()):
    location = Location.get_serializer()(required=False)
    respondent_client_tsync_id = serializers.SerializerMethodField(required=False)
    creator_name = serializers.SerializerMethodField()

    def get_creator_name(self, obj):
        try:
            return obj.created_by.name
        except:
            return "N/A"

    def get_respondent_client_tsync_id(self, obj):
        try:
            return obj.respondent_client.tsync_id
        except:
            return None

    def __init__(self, *args, fields=None, context=None, **kwargs):
        if bool(context):
            if context['request'].data:
                _data = context['request'].data
                if 'questions' in _data:
                    self.questions = _data['questions']
                if 'photos' in _data:
                    self.photos = _data['photos']
        super().__init__(fields=fields, context=context, *args, **kwargs)
        try:
            if hasattr(self, "initial_data"):
                if 'respondent_client' in self.initial_data and not self.initial_data['respondent_client']:
                    self.initial_data.pop('respondent_client')
        except Exception as e:
            ErrorLog.log(exp=e)

    def validate(self, attrs):
        # Check for duplicate tsync id
        from blackwidow.core.models import Client

        # tsync_id = attrs['tsync_id']
        # responseObj = self.Meta.model.objects.filter(tsync_id=tsync_id)
        # if responseObj.exists():
        #     raise ValidationError(
        #         {"error": "tsync_id already exists for Survey Response, Survey Response object not created"}
        #     )

        if 'respondent_client' not in self.initial_data or not self.initial_data['respondent_client']:
            if 'respondent_client_tsync_id' in self.initial_data and self.initial_data['respondent_client_tsync_id']:
                client_obj = Client.objects.filter(tsync_id=self.initial_data['respondent_client_tsync_id']).first()
                if client_obj:
                    attrs['respondent_client'] = client_obj

        return attrs

    def create(self, attrs):
        from dynamic_survey.models.entity.dynamic_question import DynamicQuestion
        from dynamic_survey.models.response.dynamic_question_response import DynamicQuestionResponse
        with transaction.atomic():
            pk = attrs['survey'].pk

            tsync_id = attrs.get('tsync_id', uuid.uuid4())
            survey_response_obj = self.Meta.model.objects.filter(tsync_id=tsync_id)
            if survey_response_obj.exists():
                return survey_response_obj.first()

            instance = super().create(attrs=attrs)
            question_queryset = DynamicQuestion.objects.filter(section__survey_id=pk)
            all_question_id = question_queryset.values_list('id', flat=True)
            section_response_dict = dict()  # Get section response by sention_id as key
            question_to_section_dict = dict()  # Get section by question_id as key
            questions = dict()
            for q in question_queryset:
                questions[q.pk] = q

            existing_questions_by_tsync_id = dict()
            for qr in DynamicQuestionResponse.objects.filter(section_response__survey_response_id=instance.pk):
                existing_questions_by_tsync_id[qr.tsync_id] = qr

            if hasattr(self, 'questions'):
                question_ids = [q['question'] for q in self.questions]
                question_section_tuple = question_queryset.filter(pk__in=question_ids).values('pk', 'section_id')
                for section in question_section_tuple:
                    question_to_section_dict[section['pk']] = section['section_id']
                    if section['section_id'] not in section_response_dict.keys():
                        from dynamic_survey.models.response.dynamic_section_response import \
                            DynamicSectionResponse
                        section_response = DynamicSectionResponse(survey_response_id=instance.pk,
                                                                  section_id=section['section_id'])
                        section_response.save()
                        section_response_dict[section['section_id']] = section_response

                creatable_question_responses = []
                timestamp=datetime.now().timestamp() * 1000
                for question in self.questions:
                    if question['tsync_id'] in existing_questions_by_tsync_id.keys():
                        continue

                    actual_question = questions[question['question']]
                    if question['answer'] == 0:
                        actual_answer_id = actual_question.answers.first().pk
                    else:
                        actual_answer_id = question['answer']
                    question_response = DynamicQuestionResponse(
                        section_response_id=section_response_dict[
                            question_to_section_dict[question['question']]].pk,
                        question_id=question['question'],
                        question_text=actual_question.text,
                        answer_id=actual_answer_id,
                        answer_text=question['answer_text'],
                        tsync_id=question['tsync_id'],
                        organization_id=instance.organization_id,
                        date_created=timestamp, created_by=instance.created_by,
                        last_updated=timestamp, last_updated_by=instance.last_updated_by
                    )
                    timestamp += 1
                    if 'index' in question.keys() and question['index']:
                        question_response.index = int(question['index'])
                    creatable_question_responses.append(question_response)
                DynamicQuestionResponse.objects.bulk_create(creatable_question_responses, batch_size=200)
            if hasattr(self, 'photos'):
                question_ids = [q['question'] for q in self.photos]
                question_section_tuple = question_queryset.filter(pk__in=question_ids).values('pk', 'section_id')
                for section in question_section_tuple:
                    question_to_section_dict[section['pk']] = section['section_id']
                    if section['section_id'] not in section_response_dict.keys():
                        from dynamic_survey.models.response.dynamic_section_response import \
                            DynamicSectionResponse
                        section_response = DynamicSectionResponse(survey_response_id=instance.pk,
                                                                  section_id=section['section_id'])
                        section_response.save()
                        section_response_dict[section['section_id']] = section_response
                for question in self.photos:
                    if DynamicQuestionResponse.objects.filter(tsync_id=question['tsync_id']).exists():
                        continue
                    actual_question = question_queryset.filter(pk=question['question']).first()
                    actual_answer_id = actual_question.answers.first().id
                    # Added tsync_id sent from the api response
                    question.update({'section_response': section_response_dict[
                        question_to_section_dict[question['question']]].pk,
                                     'answer': actual_answer_id,
                                     'question_text': actual_question.text
                                     })
                    question_serializer = DynamicQuestionResponse.get_serializer()(data=question, context=dict(
                        request=self.context['request']))
                    question_serializer.is_valid(raise_exception=True)
                    question_response_instance = question_serializer.save()
                    if question.get('photo', None) and question['photo']:
                        question['photo'].update({
                            "id": question_response_instance.photo.id if question_response_instance and question_response_instance.photo and question_response_instance.photo.id else 0
                        })

            return instance

    questions = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    def get_questions(self, obj):
        try:
            if hasattr(self, 'questions'):
                questions = getattr(self, 'questions')
                return questions
            else:
                return []
        except Exception as e:
            ErrorLog.log(exp=e)

    def get_photos(self, obj):
        try:
            if hasattr(self, "photos"):
                photos = getattr(self, 'photos')
                tsync_ids = []
                for item in photos:
                    if item.get('photo', None) and item['photo'].get('tsync_id', None):
                        tsync_ids.append(item['photo']['tsync_id'])

                photo_queryset = ImageFileObject.objects.filter(
                    tsync_id__in=tsync_ids
                ).values('id', 'tsync_id').order_by('pk')
                tsync_id_dict = {}
                for image in photo_queryset:
                    tsync_id_dict[image['tsync_id']] = image['id']

                for item in photos:
                    if item.get('photo', None) and item['photo'].get('tsync_id', None):
                        photo_pk = tsync_id_dict.get(item['photo']['tsync_id'], 0)
                        item['photo'].update({
                            "id": photo_pk
                        })
                return photos
            else:
                return []
        except Exception as e:
            ErrorLog.log(exp=e)

    class Meta:
        model = DynamicSurveyResponse
        list_serializer_class = DynamicSurveyResponseListSerializer
        fields = (
            'id', 'survey', 'survey_time', 'on_spot_creation_time', 'tsync_id', 'questions', 'photos', 'creator_name',
            'respondent_client', 'respondent_client_tsync_id', 'date_created', 'last_updated', 'location', 'created_by')
