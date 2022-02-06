"""
Created by tareq on 2/19/18
"""
from datetime import datetime, date

from django import forms
from django.apps import apps
from django.db import models
from django.forms import Form

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Organization, Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import MPI_SCORE_FOR_EP, MPI_SCORE_FOR_MP, \
    MPI_SCORE_FOR_POOR, HH_RESOURCE_QUESTION_CODE
from undp_nuprp.reports.config.constants.values import BATCH_SIZE

get_model = apps.get_model

__author__ = 'Tareq'


class EligibleGrantee(OrganizationDomainEntity):
    survey_response = models.ForeignKey('survey.SurveyResponse', null=True, on_delete=models.SET_NULL)
    pg_member = models.ForeignKey('nuprp_admin.PrimaryGroupMember', null=True, on_delete=models.SET_NULL)
    household_head_name = models.CharField(max_length=512, blank=True)
    grantee_name = models.CharField(max_length=512, blank=True)
    age = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=255, blank=True)
    affiliation = models.CharField(max_length=255, blank=True)
    ethnicity = models.CharField(max_length=255, blank=True)
    disability = models.CharField(max_length=255, blank=True)
    employment = models.CharField(max_length=255, blank=True)
    mpi_score = models.FloatField(default=0)
    nuprp_grant_recipient = models.CharField(max_length=255, blank=True)
    nuprp_grant_type_recipient = models.CharField(max_length=255, blank=True)
    other_grant_recipient = models.CharField(max_length=255, blank=True)
    other_grant_type_recipient = models.CharField(max_length=255, blank=True)
    is_eligible = models.BooleanField(default=False, db_index=True)
    is_female_headed = models.BooleanField(default=False)
    address = models.ForeignKey('core.ContactAddress', null=True)
    indvidually_edited = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = 'approval'

    @property
    def render_grants_received(self):
        type_dict = {
            "EligibleBusinessGrantee": 'SEFBusinessGrantDisbursement',
            "EligibleApprenticeshipGrantee": 'SEFApprenticeshipGrantDisbursement',
            "EligibleEducationDropOutGrantee": 'SEFEducationDropoutGrantDisbursement',
            "EligibleEducationEarlyMarriageGrantee": 'SEFEducationChildMarriageGrantDisbursement',
        }
        from undp_nuprp.approvals.models import SEFGrantInstalment
        is_grant_received = SEFGrantInstalment.objects.filter(
            status='Disbursed',
            sefgrantdisbursement__pg_member=self.pg_member,
            sefgrantdisbursement__type=type_dict.get(self.__class__.__name__, 'SEFGrantDisbursement')
        ).exists()

        if is_grant_received:
            return "Yes"
        return "No"

    @property
    def render_year(self):
        type_dict = {
            "EligibleBusinessGrantee": 'SEFBusinessGrantDisbursement',
            "EligibleApprenticeshipGrantee": 'SEFApprenticeshipGrantDisbursement',
            "EligibleEducationDropOutGrantee": 'SEFEducationDropoutGrantDisbursement',
            "EligibleEducationEarlyMarriageGrantee": 'SEFEducationChildMarriageGrantDisbursement',
        }
        from undp_nuprp.approvals.models import SEFGrantInstalment
        is_grant_received = SEFGrantInstalment.objects.filter(
            status='Disbursed',
            sefgrantdisbursement__pg_member=self.pg_member,
            sefgrantdisbursement__type=type_dict.get(self.__class__.__name__, 'SEFGrantDisbursement')
        ).first()

        if is_grant_received:
            return is_grant_received.date
        return "N/A"

    @property
    def render_eligibility(self):
        if self.is_eligible:
            return "Eligible"
        else:
            return "Not Eligible"

    @property
    def render_eligible(self):
        if self.is_eligible:
            return "Yes"
        return "No"

    @property
    def render_city_corporation(self):
        if self.pg_member and self.pg_member.assigned_to:
            return self.pg_member.assigned_to.parent.address.geography.parent.name
        else:
            return 'N/A'

    @classmethod
    def search_eligible(cls, queryset, value):
        _value = False
        if value.lower().__contains__('yes'):
            _value = True
        return queryset.filter(is_eligible=_value)

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(pg_member__assigned_to__parent__address__geography__parent__name__icontains=value)

    @classmethod
    def get_export_dependant_fields(cls):

        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                today = date.today().replace(day=1)
                year_choices = tuple()
                month_choices = tuple(
                    [(today.replace(month=i).strftime('%B'), today.replace(month=i).strftime('%B'))
                     for i in range(1, 13)])
                for y in range(2000, 2100):
                    year_choices += ((y, str(y)),)

                self.fields['city'] = \
                    GenericModelChoiceField(
                        queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
                        label='Select City',
                        empty_label="Select one",
                        required=True,
                        widget=forms.Select(
                            attrs={
                                'class': 'select2 kpi-filter',
                                'width': '220'
                            }
                        )
                    )

                self.fields['year'] = forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )

                self.fields['month'] = forms.ChoiceField(
                    choices=month_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.strftime('%B')
                )

        return AdvancedExportDependentForm

    @classmethod
    def get_question_response(cls, question_code, response_dict={}):
        if not question_code in response_dict.keys():
            return ''
        return ', '.join(response_dict[question_code])

    @classmethod
    def get_resource_response(cls, resource_name, response_dict={}):
        if not HH_RESOURCE_QUESTION_CODE in response_dict.keys():
            return 'No'
        if resource_name in response_dict[HH_RESOURCE_QUESTION_CODE]:
            return 'Yes'
        return 'No'

    @property
    def render_other_grants(self):
        grantee_model_names = ['EligibleBusinessGrantee', 'EligibleApprenticeshipGrantee',
                               'EligibleEducationDropOutGrantee', 'EligibleEducationEarlyMarriageGrantee']
        grantee_model_names.remove(self.__class__.__name__)
        other_grants = ''
        for model_name in grantee_model_names:
            Model = get_model('approvals', model_name)
            if Model.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    pg_member_id=self.pg_member_id).exists():
                other_grants += bw_titleize(model_name) + ', '

        return other_grants.rstrip(', ')

    @property
    def render_female_headed_hh(self):
        if self.is_female_headed:
            return "Yes"
        return "No"

    @classmethod
    def table_columns(cls):
        return (
            'survey_response', 'render_grants_received', 'render_year', 'pg_member:PG Member', 'grantee_name',
            'render_city_corporation' ,'affiliation', 'age', 'gender', 'ethnicity', 'mpi_score:MPI Score', 'render_eligible'
        )

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedExport]

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @classmethod
    def get_button_title(cls, button):
        if button == ViewActionEnum.AdvancedExport:
            return 'Export'
        return 'Action'

    @property
    def render_city(self):
        if self.address:
            try:
                return self.address.geography.parent.name
            except:
                pass
        return ''

    @property
    def render_survey_date(self):
        try:
            return datetime.fromtimestamp(self.survey_response.survey_time / 1000).strftime("%d/%m/%Y")
        except:
            return ''

    @property
    def render_ward(self):
        if self.address:
            try:
                return self.address.geography.name
            except:
                pass
        return ''

    @property
    def render_cluster(self):
        try:
            return self.pg_member.assigned_to.parent.parent.name
        except:
            return ''

    @property
    def render_cdc(self):
        try:
            return self.pg_member.assigned_to.parent.name
        except:
            return ''

    @property
    def render_poverty_status(self):
        if self.mpi_score > MPI_SCORE_FOR_EP:
            return 'Extreme Poor'
        if self.mpi_score > MPI_SCORE_FOR_MP:
            return 'Moderate Poor'
        if self.mpi_score > MPI_SCORE_FOR_POOR:
            return 'Poor'
        return 'Not Poor'

    @property
    def render_pg_phone(self):
        if self.pg_member.phone_number:
            return self.pg_member.phone_number.phone
        else:
            return 'N/A'

    @property
    def render_pg_number(self):
        try:
            return self.pg_member.assigned_to.assigned_code
        except:
            return ''

    @property
    def render_pg_name(self):
        try:
            return self.pg_member.assigned_to.name
        except:
            return ''

    @property
    def render_pg_member_number(self):
        try:
            return self.pg_member.assigned_code
        except:
            return ''

    @property
    def export_pg_member_number(self):
        pg_member_number = self.render_pg_member_number
        if pg_member_number != '':
            return '\'' + pg_member_number

    @property
    def export_pg_number(self):
        pg_number = self.render_pg_number
        if pg_number != '':
            return '\'' + pg_number

    @property
    def render_pg_member_name(self):
        try:
            return self.pg_member.name
        except:
            return ''

    @property
    def render_geo_reference(self):
        if self.survey_response:
            if self.survey_response.location:
                return str(self.survey_response.location.latitude) + ', ' + str(self.survey_response.location.longitude)
        return "N/A"

    @classmethod
    def get_export_file_name(cls):
        return cls.__name__.lower()

    @classmethod
    def build_report(
            cls, columns=None, max_id=0, id_limit=0, batch_size=BATCH_SIZE, year=None, month=None, city_id=None):
        from undp_nuprp.survey.models.response.question_response import QuestionResponse

        report = list()
        headers = list()

        organization = Organization.get_organization_from_cache()
        if columns is None:
            columns = cls.exporter_config(organization=organization).columns.all().order_by('date_created')

        for column in columns:
            headers.append(column.column_name)

        report.append(headers)

        initial_queryset = cls.objects.all()
        if city_id:
            initial_queryset = initial_queryset.filter(address__geography__parent_id=city_id)
        if year:
            if month:
                start_time = datetime.now().replace(year=year, month=month, day=1, hour=0, minute=0,
                                                    second=0).timestamp() * 1000
                if month == 12:
                    month = 0
                    year += 1
                end_time = datetime.now().replace(year=year, month=month + 1, day=1, hour=0, minute=0,
                                                  second=0).timestamp() * 1000 - 1000
            else:
                start_time = datetime.now().replace(year=year, month=1, day=1, hour=0, minute=0,
                                                    second=0).timestamp() * 1000
                end_time = datetime.now().replace(year=year + 1, month=1, day=1, hour=0, minute=0,
                                                  second=0).timestamp() * 1000 - 1000
            initial_queryset = initial_queryset.filter(
                pg_member__date_created__gte=start_time, pg_member__date_created__lte=end_time)

        eligible_grantee_queryset = initial_queryset.order_by('pk').filter(
            pk__gt=max_id, pk__lte=id_limit
        )[:batch_size]

        handled = 0
        for _object in eligible_grantee_queryset:
            max_id = _object.pk
            row = list()

            answers = QuestionResponse.objects.filter(
                section_response__survey_response_id=_object.survey_response_id).values(
                'answer_text', 'question__question_code')

            response_dict = dict()
            for answer in answers:
                if answer['question__question_code'] in response_dict.keys():
                    response_dict[answer['question__question_code']].append(answer['answer_text'])
                else:
                    response_dict[answer['question__question_code']] = [answer['answer_text']]

            for column in columns:
                _value = ''
                prop_name = column.property_name
                if hasattr(_object, prop_name):
                    _value = str(getattr(_object, prop_name))
                elif prop_name.startswith('render_q_code_') and prop_name.endswith('_response'):
                    _value = cls.get_question_response(
                        question_code=prop_name[14:-9].replace('_', '.'), response_dict=response_dict)
                elif prop_name.startswith('render_resource_') and prop_name.endswith('_response'):
                    _value = cls.get_resource_response(
                        resource_name=column.column_name, response_dict=response_dict)
                row.append(_value)
            report.append(row)
            handled += 1
        return handled, max_id, report
