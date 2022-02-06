from collections import OrderedDict

from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models.query_utils import Q
from django.urls import reverse
from jsonfield import JSONField
from taggit.managers import TaggableManager

from blackwidow.core.models import ErrorLog, ApprovalAction, ApprovalStatus
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from dynamic_survey.enums.dynamic_survey_status_enum import DynamicSurveyStatusEnum
from dynamic_survey.models.design.dynamic_survey_group import DynamicSurveyGroup
from dynamic_survey.models.response.dynamic_survey_response import DynamicSurveyResponse

__author__ = 'Razon'

ASSET_UID_LENGTH = 22


@decorate(save_audit_log, is_object_context, expose_api('dynamic-survey'),
          route(route='dynamic-survey', group='Dynamic Survey', group_order=5, module=ModuleEnum.Administration,
                display_name="Dynamic Survey", item_order=1))
class DynamicSurvey(OrganizationDomainEntity):
    '''
    SurveyDrafts belong to a user and contain the minimal representation of
    the draft survey of the user and of the question library.
    '''
    user = models.ForeignKey(User, related_name="survey_drafts")
    name = models.CharField(max_length=255, null=False)
    status = models.IntegerField(default=DynamicSurveyStatusEnum.Draft.value)
    version = models.IntegerField(default=1)
    survey = models.ForeignKey(DynamicSurveyGroup, null=True, on_delete=models.CASCADE, related_name="survey_drafts")
    detail_link = models.CharField(max_length=255, default="", blank=True)
    date_published = models.BigIntegerField(editable=False, default=0)
    latest_flag = models.BooleanField(default=False)
    body = models.TextField()
    description = models.CharField(max_length=255, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    summary = JSONField()
    asset_type = models.CharField(max_length=32, null=True)
    tags = TaggableManager()
    kpi_asset_uid = models.CharField(
        max_length=ASSET_UID_LENGTH, default='', blank=True)

    class Meta:
        app_label = 'dynamic_survey'

    @property
    def _pyxform_survey(self):
        from dynamic_survey.utils.pyxform_utils import convert_csv_to_valid_xlsform_unicode_csv, \
            create_survey_from_csv_text
        valid_csv_body = convert_csv_to_valid_xlsform_unicode_csv(self.body)
        survey = create_survey_from_csv_text(valid_csv_body)
        survey.title = self.name
        return survey

    @property
    def id_string(self):
        # Ideally, we could determine this without needing to load the entire
        # survey into pyxform, but parsing csvs from unk sources can be complicated
        # and this method of finding the id_string is (at least) consistent.
        return self._pyxform_survey.id_string

    def _set_form_id_string(self, form_id_string, title=False):
        '''
        goal: rewrite this to avoid csv manipulation
        '''
        body = self.body.split('\n')

        form_settings = body.pop()

        if form_settings is u'':
            form_settings = body.pop() + '\n'
        form_settings_list = form_settings.split(',')

        if title and title != '':
            form_settings_list.pop(1)
            form_settings_list.insert(1, '"' + title + '"')
        if form_id_string and form_id_string != '':
            form_settings_list.pop(2)
            form_settings_list.insert(2, '"' + form_id_string + '"')

        body.append(','.join(form_settings_list))
        self.body = '\n'.join(body)

    def to_xml(self):
        return self._pyxform_survey.to_xml()

    def to_xls(self):
        from dynamic_survey.utils.pyxform_utils import convert_csv_to_xls
        return convert_csv_to_xls(self.body)

    def _summarize(self):
        try:
            from dynamic_survey.utils.pyxform_utils import summarize_survey
            self.summary = summarize_survey(self.body, self.asset_type)
        except Exception as err:
            self.summary = {'error': str(err)}

    def save(self, *args, **kwargs):
        self._summarize()
        super(DynamicSurvey, self).save(*args, **kwargs)

    # BlackWidow Magics Start From Here
    @property
    def render_status(self):
        return DynamicSurveyStatusEnum.get_status_name(self.status)

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['status'] = self.render_status
        details['version'] = self.version
        # details['infrastructure_unit_level'] = self.infrastructure_unit_level
        # details['client_level'] = self.client_level
        # details['product'] = self.product
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        return details

    @staticmethod
    def get_formatted_date_time(value, user=None, format=None):
        format = "%d/%m/%Y - %I:%M %p"
        return value.strftime(format=format)

    def details_link_config(self, **kwargs):
        links = []
        if self.status == DynamicSurveyStatusEnum.Draft.value:
            links.append(
                dict(
                    name='Publish',
                    action='approve',
                    icon='fbx-rightnav-tick',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Approve),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))

            links.append(
                dict(
                    name='Edit Survey',
                    action='edit',
                    icon='fbx-rightnav-edit',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))

        elif self.status == DynamicSurveyStatusEnum.Published.value:
            links.append(
                dict(
                    name='Disable Survey',
                    action='mutate',
                    icon='fbx-rightnav-cancel',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Mutate),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))
            links.append(
                dict(
                    name='Upgrade To New Version',
                    action='deactivate',
                    icon='fbx-rightnav-new',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Deactivate),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))
            links.append(
                dict(
                    name='View Survey',
                    action='restore',
                    icon='fbx-rightnav-resume',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Restore),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))

        elif self.status == DynamicSurveyStatusEnum.Disabled.value:
            links.append(
                dict(
                    name='Publish Survey Again',
                    action='mutate',
                    icon='fbx-rightnav-tick',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Mutate),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))
            links.append(
                dict(
                    name='Upgrade To New Version',
                    action='deactivate',
                    icon='fbx-rightnav-new',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Deactivate),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))

            links.append(
                dict(
                    name='View Survey',
                    action='restore',
                    icon='fbx-rightnav-resume',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Restore),
                    classes='manage-action all-action confirm-action',
                    parent=None
                ))

        return links

    @property
    def tabs_config(self):
        if self.status != DynamicSurveyStatusEnum.Draft.value:
            return [
                TabView(
                    title='Section(s)',
                    access_key='dynamic_sections',
                    route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                    relation_type=ModelRelationType.INVERTED,
                    related_model='dynamic_survey.DynamicSection',
                    queryset_filter=Q(**{'survey_id': self.pk})
                ),
                TabView(
                    title='Question(s)',
                    access_key='dynamic_questions',
                    route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                    relation_type=ModelRelationType.INVERTED,
                    related_model='dynamic_survey.DynamicQuestion',
                    queryset_filter=Q(**{'section__survey_id': self.pk})
                ),
                TabView(
                    title='Answer/Option(s)',
                    access_key='dynamic_answers',
                    route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                    relation_type=ModelRelationType.INVERTED,
                    related_model='dynamic_survey.DynamicAnswer',
                    queryset_filter=Q(**{'question__section__survey_id': self.pk})
                ),
                TabView(
                    title='Response(s)',
                    access_key='dynamic_responses',
                    route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                    relation_type=ModelRelationType.INVERTED,
                    related_model='dynamic_survey.DynamicSurveyResponse',
                    queryset=DynamicSurveyResponse.objects.all(),
                    queryset_filter=Q(**{'survey_id': self.pk})
                )
            ]
        return []

    def approval_level_1_action(self, action, *args, **kwargs):
        # This method is only used to publish the survey for the first time

        previous_status = self.status
        if action == "Approved":
            if previous_status == DynamicSurveyStatusEnum.Draft.value:
                from dynamic_survey.utils.dynamic_survey.survey_design_db_handler import parse_survey
                _success = parse_survey(self)
                if _success:
                    try:
                        with transaction.atomic():
                            self.disable_surveys()
                            self.status = DynamicSurveyStatusEnum.Published.value
                            self.latest_flag = True
                            self.date_published = Clock.timestamp()
                            self.save()

                            _survey_group = self.survey
                            _survey_group.publish_flag = True
                            _survey_group.save()
                    except Exception as e:
                        ErrorLog.log(e)
                        ApprovalAction.objects.filter(object_id=self.id, status=ApprovalStatus.Approved.value,
                                                      model_name=self.__class__.__name__).order_by(
                            'date_created').last().delete()

    @transaction.atomic
    def mutate_to(self):

        previous_status = self.status
        if previous_status == DynamicSurveyStatusEnum.Published.value:
            self.status = DynamicSurveyStatusEnum.Disabled.value
            self.latest_flag = False
            self.save()
            survey_group = self.survey
            survey_group.publish_flag = False
            survey_group.save()
        elif previous_status == DynamicSurveyStatusEnum.Disabled.value:
            self.disable_surveys()
            self.status = DynamicSurveyStatusEnum.Published.value
            self.latest_flag = True
            self.date_published = Clock.timestamp()
            self.save()
            survey_group = self.survey
            survey_group.publish_flag = True
            survey_group.save()

        return self

    @classmethod
    def get_serializer(cls):
        from dynamic_survey.serializers.design.v_1.dynamic_survey_serializer import DynamicSurveySerializer
        return DynamicSurveySerializer

    @classmethod
    def success_url(cls):
        return reverse(cls.get_route_name(ViewActionEnum.Manage))

    @classmethod
    def show_approve_button_first_level(cls):
        return True

    def get_choice_name(self):
        code = self.code if self.code else ""
        name = self.name if self.name else ""
        version = str(self.version) if self.version else ""
        return code + ": " + name + "-Version: " + version

    @classmethod
    def delete_disabled_survey_and_its_responses(cls):
        from dynamic_survey.models.response.dynamic_question_response import DynamicQuestionResponse
        from dynamic_survey.models.response.dynamic_section_response import DynamicSectionResponse

        _survey_ids = DynamicSurvey.objects.filter(status=DynamicSurveyStatusEnum.Disabled.value).values_list('pk',
                                                                                                              flat=True)

        with transaction.atomic():
            for _id in _survey_ids:
                _survey = DynamicSurvey.objects.filter(id=_id).first()
                if _survey:
                    total, items = DynamicQuestionResponse.objects.filter(
                        section_response__survey_response__survey_id=_id).delete()
                    print(
                        'Total {} question responses has deleted associated with the dynamic survey: #{}'.format(total,
                                                                                                                 _id))

                    total, items = DynamicSectionResponse.objects.filter(survey_response__survey_id=_id).delete()
                    print('Total {} section responses has deleted associated with the dynamic survey: #{}'.format(total,
                                                                                                                  _id))

                    total, items = DynamicSurveyResponse.objects.filter(survey_id=_id).delete()
                    print('Total {} survey responses has deleted associated with the dynamic survey: #{}'.format(total,
                                                                                                                 _id))

                    DynamicSurvey.objects.filter(id=_id).delete()
                    print('Survey name: {} has deleted successfully'.format(_survey.name))

    @classmethod
    def get_model_api_queryset(cls, queryset=None, **kwargs):
        """
        With `survey__isnull=False` we are excluding all the question library from the api.
        With `exclude(status=DynamicSurveyStatusEnum.Draft.value) we are excluding all the draft surveys.
        Then we are getting the max versioned survey of each survey group

        :param queryset: by default gets all the objects of the model as queryset
        :return: returns filtered queryset
        """

        queryset = queryset.filter(latest_flag=True)
        return queryset

    def disable_surveys(self):
        # Getting the previous latest survey of this group
        self.__class__.objects.filter(survey__isnull=False, survey=self.survey,
                                      status=DynamicSurveyStatusEnum.Published.value).update(latest_flag=False,
                                      status=DynamicSurveyStatusEnum.Disabled.value)

    # This portion is commented out as there is no mongo support in blackwidow
    # def get_document_class(self):
    #     from dynamic_survey.models.entity.dynamic_question import DynamicQuestion
    #     document_name = bw_str(self.name).to_alpha_numeric() + str(self.pk) + "_Document"
    #     field_dict = {
    #         "db_id": IntField(),
    #         "survey": EmbeddedDocumentField(NamedItemDocuemnt),
    #         "survey_timestamp": LongField(default=0),
    #         "year_value": IntField(default=0),
    #         "month_value": IntField(default=0),
    #         "day_value": IntField(default=0),
    #         "week_value": IntField(default=0),
    #         "respondent_client": EmbeddedDocumentField(NamedItemDocuemnt),
    #         "respondent_unit": EmbeddedDocumentField(NamedItemDocuemnt),
    #         "location": EmbeddedDocumentField(LocationDocument),
    #     }
    #
    #     grids = {}
    #     for q in DynamicQuestion.objects.filter(section__survey_id=self.pk):
    #         _name = 'f_' + str(q.id)
    #         if q.section and q.section.name:
    #             _text = q.section.name + "-" + q.text
    #         else:
    #             _text = q.text
    #         if q.question_code:
    #             _verbose = q.question_code + "-" + _text
    #         else:
    #             _verbose = _text
    #
    #         if q.question_type == DynamicSurveyQuestionTypeEnum.DynamicGrid.value:
    #             if q.pk not in grids.keys():
    #                 grids[q.pk] = {
    #                     'name': _name,
    #                     'verbose': _verbose,
    #                     'code': q.question_code,
    #                     'fields': {}
    #                 }
    #             else:
    #                 grids[q.pk].update({
    #                     'name': _name,
    #                     'verbose': _verbose,
    #                 })
    #         elif q.parent and q.parent.question_type == DynamicSurveyQuestionTypeEnum.DynamicGrid.value:
    #             if q.parent_id not in grids.keys():
    #                 grids[q.parent_id] = {
    #                     'name': q.parent.text,
    #                     'code': q.parent.question_code,
    #                     'fields': {}
    #                 }
    #             if q.question_type == DynamicSurveyQuestionTypeEnum.NumberInput.value:
    #                 grids[q.parent_id]['fields'][_name] = FloatField(default=0, verbose_name=_verbose)
    #             else:
    #                 grids[q.parent_id]['fields'][_name] = StringField(verbose_name=_verbose)
    #         else:
    #             if q.question_type == DynamicSurveyQuestionTypeEnum.NumberInput.value:
    #                 field_dict[_name] = FloatField(default=0, verbose_name=_verbose)
    #             else:
    #                 field_dict[_name] = StringField(verbose_name=_verbose)
    #
    #     for grid_id, grid_dict in grids.items():
    #         grid_class = type(GRID_QUESTION_PREFIX + str(grid_id), (EmbeddedDocument,), grid_dict['fields'])
    #         field_dict[grid_dict["name"]] = EmbeddedDocumentListField(grid_class, verbose_name=grid_dict["verbose"])
    #
    #     return type(
    #         document_name, (Document,), field_dict
    #     )
