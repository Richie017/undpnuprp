import re

from django.db import models
from django.db.models import Count, Max
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from blackwidow.engine.templatetags.blackwidow_filter import SITE_ROOT
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.awareness_raising_by_scc import \
    AwarenessRaisingBySCC
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.functioning_of_scc import FunctionOfSCC
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.safety_security_initiative import \
    SafetySecurityInitiative
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.scc_partnership.activities_of_partnership import \
    ActivitiesOfPartnership
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.scc_partnership.agreed_partnership import \
    AgreedPartnership
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.scc_partnership.explored_partnership import \
    ExploredPartnership
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.vawg_and_efm_reduction_initiative import \
    VAWGEFMReductionInitiative
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster

__author__ = 'Shuvro'


@decorate(is_object_context,
          route(route='vawg-and-early-marriage-prevention-reporting',
                group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                display_name='VAWG & Early Marriage Prevention Reporting', group_order=3, item_order=24))
class VAWGEarlyMarriagePreventionReporting(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)
    year = models.CharField(max_length=4, null=True, blank=True)
    month = models.CharField(max_length=10, null=True, blank=True)
    cdc_cluster = models.ForeignKey(CDCCluster, null=True, on_delete=models.SET_NULL, related_name='+')
    name_of_scc = models.CharField(null=True, blank=True, max_length=256)
    has_a_committee_been_formed = models.CharField(null=True, blank=True, max_length=128)
    has_a_constitution_been_prepared = models.CharField(null=True, blank=True, max_length=128)
    composition_of_the_committee = models.CharField(null=True, blank=True, max_length=256)
    number_of_male = models.IntegerField(null=True, default=0)
    number_of_female = models.IntegerField(null=True, default=0)
    number_of_disabled = models.IntegerField(null=True, default=0)
    number_of_disabled_male = models.IntegerField(null=True, default=0)
    number_of_disabled_female = models.IntegerField(null=True, default=0)
    number_of_transsexual = models.IntegerField(null=True, default=0)
    total_number_of_people = models.IntegerField(null=True, default=0)
    function_of_scc = models.OneToOneField(FunctionOfSCC, null=True, on_delete=models.SET_NULL)
    vawg_and_efm_reduction_initiatives = models.ManyToManyField(VAWGEFMReductionInitiative)
    safety_security_initiatives = models.ManyToManyField(SafetySecurityInitiative)
    awareness_raising_by_sccs = models.ManyToManyField(AwarenessRaisingBySCC)
    explored_partnerships = models.ManyToManyField(ExploredPartnership)
    agreed_partnerships = models.ManyToManyField(AgreedPartnership)
    activities_of_partnerships = models.ManyToManyField(ActivitiesOfPartnership)

    class Meta:
        app_label = 'approvals'

    @property
    def render_CDC_Cluster(self):
        return self.cdc_cluster if self.cdc_cluster else 'N/A'

    @property
    def render_name_of_SCC(self):
        return self.name_of_scc if self.name_of_scc else 'N/A '

    @property
    def render_city(self):
        return self.city if self.city else 'N/A'

    @property
    def render_scc_meeting_happen_before_or_after_the_cluster_meeting(self):
        return self.function_of_scc.scc_meeting_happen_before_or_after_the_cluster_meeting \
            if self.function_of_scc and \
               self.function_of_scc.scc_meeting_happen_before_or_after_the_cluster_meeting else 'N/A'

    @property
    def render_scc_last_hold_its_quarterly_review_meeting(self):
        return self.function_of_scc.scc_last_hold_its_quarterly_review_meeting \
            if self.function_of_scc and self.function_of_scc.scc_last_hold_its_quarterly_review_meeting else 'N/A'

    @property
    def render_number_of_male(self):
        return self.function_of_scc.number_of_male if self.function_of_scc else 'N/A'

    @property
    def render_number_of_female(self):
        return self.function_of_scc.number_of_female if self.function_of_scc else 'N/A'

    @property
    def render_number_of_transsexual(self):
        return self.function_of_scc.number_of_transsexual if self.function_of_scc else 'N/A'

    @property
    def render_number_of_participants(self):
        return self.function_of_scc.number_of_participants if self.function_of_scc else 'N/A'

    @property
    def render_parts_of_the_scc_plan_included_within_the_cap(self):
        return self.function_of_scc.parts_of_the_scc_plan_included_within_the_cap \
            if self.function_of_scc and self.function_of_scc.parts_of_the_scc_plan_included_within_the_cap else 'N/A'

    @property
    def detail_title(self):
        return mark_safe(str(self.display_name()))

    @classmethod
    def table_columns(cls):
        return [
            'code', 'render_city', 'year', 'month', 'render_CDC_Cluster', 'render_name_of_SCC', 'created_by',
            'date_created', 'last_updated_by', 'last_updated:Last Updated On'
        ]

    @classmethod
    def details_view_fields(cls):
        _basic_info = 'Establishment of SCCs (for each SCC that has been established, enter the following information)'
        _functioning_of_sccs = 'Functioning of SCCs'
        return [
            'detail_title', 'city>{}'.format(_basic_info),
            'year>{}'.format(_basic_info), 'month>{}'.format(_basic_info),
            'cdc_cluster:CDC Cluster>{}'.format(_basic_info),
            'name_of_scc:Name of SCC>{}'.format(_basic_info),
            'has_a_committee_been_formed>{}'.format(_basic_info),
            'has_a_constitution_been_prepared>{}'.format(_basic_info),
            # 'composition_of_the_committee>{}'.format(_basic_info),
            'number_of_male>{}'.format(_basic_info),
            'number_of_female>{}'.format(_basic_info),
            'number_of_disabled_male>{}'.format(_basic_info),
            'number_of_disabled_female>{}'.format(_basic_info),
            'number_of_transsexual>{}'.format(_basic_info),
            'total_number_of_people>{}'.format(_basic_info),
            'render_scc_meeting_happen_before_or_after_the_cluster_meeting:Does the SCC meeting happen just before/ just '
            'after the cluster committee meeting (same day)?>{}'.format(_functioning_of_sccs),
            'render_scc_last_hold_its_quarterly_review_meeting:When did the SCC last hold it\'s quarterly (review) '
            'meeting?>{}'.format(_functioning_of_sccs),
            'render_number_of_male>{}'.format(_functioning_of_sccs),
            'render_number_of_female>{}'.format(_functioning_of_sccs),
            'render_number_of_transsexual>{}'.format(_functioning_of_sccs),
            'render_number_of_participants>{}'.format(_functioning_of_sccs),
            'render_parts_of_the_scc_plan_included_within_the_cap:Are parts of the SCC plan included within the CAP?>{}'.format(
                _functioning_of_sccs)
        ]

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Initiatives to reduce VAWG and EFM',
                access_key='vawg_and_efm_reduction_initiatives',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=VAWGEFMReductionInitiative,
                property=self.vawg_and_efm_reduction_initiatives,
            ),
            TabView(
                title='Initiatives to increase gender-friendly communities',
                access_key='safety_security_initiatives',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=SafetySecurityInitiative,
                property=self.safety_security_initiatives,
            ),
            TabView(
                title='Awareness campaigns by SCC',
                access_key='awareness_raising_by_sccs',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=AwarenessRaisingBySCC,
                property=self.awareness_raising_by_sccs,
            ),
            TabView(
                title='Partnerships explored',
                access_key='explored_partnerships',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=ExploredPartnership,
                property=self.explored_partnerships,
            ),
            TabView(
                title='Partnerships agreement',
                access_key='agreed_partnerships',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=AgreedPartnership,
                property=self.agreed_partnerships,
            ),
            TabView(
                title='Partnership activities conducted',
                access_key='activities_of_partnerships',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=ActivitiesOfPartnership,
                property=self.activities_of_partnerships,
            ),
        ]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.Import:
            return "Import"

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedExport]

    @classmethod
    def export_file_columns(cls):
        """
        this method is used to get the list of columns to be exported
        :return: a list of column properties
        """
        return 'code', 'render_city:City', 'year', 'month', 'render_CDC_Cluster:CDC Cluster', 'render_name_of_SCC:Name of SCC', \
               'has_a_committee_been_formed', \
               'has_a_constitution_been_prepared', \
               'number_of_male', \
               'number_of_female', \
               'number_of_disabled_male', \
               'number_of_disabled_female', \
               'number_of_transsexual', \
               'total_number_of_people', \
               'render_scc_meeting_happen_before_or_after_the_cluster_meeting:Does the SCC meeting happen just ' \
               'before/ just after the cluster committee meeting (same day)?', \
               'render_scc_last_hold_its_quarterly_review_meeting:When did the SCC last hold it\'s quarterly ' \
               '(review) meeting?', \
               'render_number_of_male', \
               'render_number_of_female', \
               'render_number_of_transsexual', \
               'render_number_of_participants', \
               'render_parts_of_the_scc_plan_included_within_the_cap:Are parts of the SCC plan included within the CAP?'

    @classmethod
    def get_export_order_by(cls):
        return '-last_updated'

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):
        """
        this method is used to format the excel file at the beginning of the export
        :param workbook: the workbook instance to work on
        :param columns: exported column configs
        :param row_number: beginning row at which the cursor is on
        :param query_set: the queryset for exportable objects
        :param kwargs: extra params
        :return: tuple of (workbook, row_number): these are updated workbook and row_number after the initiatialization
        """
        column = 1
        for c in columns:
            workbook.cell(row=row_number, column=column).value = c.column_name
            workbook.merge_cells(start_row=row_number, end_row=row_number + 1, start_column=column, end_column=column)
            column += 1

        no_of_vawg_initiatives = len(cls.vawg_and_efm_reduction_initiatives_export_column_titles())
        no_of_safety_initiatives = len(cls.safety_security_initiatives_export_column_titles())
        no_of_awareness_campaigns = len(cls.awareness_raising_by_sccs_export_column_titles())
        no_of_partnerships_explored = len(cls.explored_partnerships_export_column_titles())
        no_of_partnerships_agreed = len(cls.agreed_partnerships_export_column_titles())
        no_of_partnerships_conducted = len(cls.activities_of_partnerships_export_column_titles())
        tab_headers = [
            ('Initiatives to reduce VAWG & EFM', no_of_vawg_initiatives),
            ('Initiative to increase gender friendly communities', no_of_safety_initiatives),
            ('Awareness campaign of last month', no_of_awareness_campaigns),
            ('Partnerships explored', no_of_partnerships_explored),
            ('Partnerships agreed', no_of_partnerships_agreed),
            ('Partnership activities conducted', no_of_partnerships_conducted)
        ]
        kwargs.update({'no_of_vawg_initiatives': no_of_vawg_initiatives,
                       'no_of_safety_initiatives': no_of_safety_initiatives,
                       'no_of_awareness_campaigns': no_of_awareness_campaigns,
                       'no_of_partnerships_explored': no_of_partnerships_explored,
                       'no_of_partnerships_agreed': no_of_partnerships_agreed,
                       'no_of_partnerships_conducted': no_of_partnerships_conducted})

        merged_header = column
        for h in tab_headers:
            workbook.cell(row=row_number, column=merged_header).value = h[0]
            workbook.merge_cells(start_row=row_number, end_row=row_number, start_column=merged_header,
                                 end_column=merged_header + h[1] - 1)
            merged_header += h[1]

        row_number += 1

        tab_columns = list(
            cls.vawg_and_efm_reduction_initiatives_export_column_titles() +
            cls.safety_security_initiatives_export_column_titles() +
            cls.awareness_raising_by_sccs_export_column_titles() +
            cls.explored_partnerships_export_column_titles() +
            cls.agreed_partnerships_export_column_titles() +
            cls.activities_of_partnerships_export_column_titles()
        )

        for _col_name in tab_columns:
            workbook.cell(row=row_number, column=column).value = bw_titleize(_col_name)
            column += 1

        row_number += 1

        for obj in query_set:
            _, row_number = obj.export_item_(workbook=workbook, columns=columns, row_number=row_number, **kwargs)

        return workbook, row_number

    @staticmethod
    def export_row_item(workbook=None, row_number=None, items=None, **kwargs):
        """
        prepare individual row for the excel file
        :param workbook: the workbook instance to work on
        :param row_number: number of current row of cursor position
        :param items: items of the tow to be write in workbook
        :return:
        """
        column_no = 1
        for item in items:
            workbook.cell(row=row_number, column=column_no).value = str(item)
            column_no += 1

    @staticmethod
    def extend_list(list_, val, len_):
        sz = len_ - len(list_)
        if sz > 0:
            for _ in range(sz):
                list_.append(val)
        return list_

    def export_item_(self, workbook=None, columns=None, row_number=None, **kwargs):
        """
        prepare individual row for the excel file
        :param workbook: the workbook instance to work on
        :param columns: expoted colmun configs
        :param row_number: number of current row of cursor position
        :return: tuple (pk, row_number): pk of the current item, and the updated cursor position as row
        """
        items = []
        for column in columns:
            _value = getattr(self, column.property_name, '')
            _url = ''
            href = False

            if column.property_name in self.__class__.get_datetime_fields():
                _value = self.render_timestamp(_value)

            if _value:
                url_search = re.search('<a(.+?)href=(.+?)>(.+?)</a>', str(_value))
                if url_search:
                    _value = url_search.group(3)
                    _url = url_search.group(2).replace('"', '').replace("'", '')
                    href = True
            else:
                _value = ''

            if href:
                items.append('=HYPERLINK("{}", "{}")'.format((SITE_ROOT + _url), _value))
            else:
                items.append(str(_value))

        items = [*items,
                 *self.extend_list(self.vawg_and_efm_reduction_initiatives_export_column_values, 'N/A',
                                   kwargs.get('no_of_vawg_initiatives')),
                 *self.extend_list(self.safety_security_initiatives_export_column_values, 'N/A',
                                   kwargs.get('no_of_safety_initiatives')),
                 *self.extend_list(self.awareness_raising_by_sccs_export_column_values, 'N/A',
                                   kwargs.get('no_of_awareness_campaigns')),
                 *self.extend_list(self.explored_partnerships_export_column_values, 'N/A',
                                   kwargs.get('no_of_partnerships_explored')),
                 *self.extend_list(self.agreed_partnerships_export_column_values, 'N/A',
                                   kwargs.get('no_of_partnerships_agreed')),
                 *self.extend_list(self.activities_of_partnerships_export_column_values, 'N/A',
                                   kwargs.get('no_of_partnerships_conducted'))
                 ]
        self.export_row_item(workbook=workbook, row_number=row_number, items=items)

        return self.pk, row_number + 1

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        return self.pk, row_number

    @classmethod
    def vawg_and_efm_reduction_initiatives_export_column_titles(cls):
        _col_header_prefix = ['Total number of issues']
        column_name = ['Name of issue', 'Explanation']
        _max_no_initiatives = cls.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).annotate(total=Count('vawg_and_efm_reduction_initiatives')).aggregate(Max('total'))['total__max']
        _max_no_initiatives = _max_no_initiatives if _max_no_initiatives else 0
        return _col_header_prefix + ['{} {}'.format(_col_name, i + 1)
                                     for i in range(_max_no_initiatives) for _col_name in column_name]

    @property
    def vawg_and_efm_reduction_initiatives_export_column_values(self):
        column_values = self.vawg_and_efm_reduction_initiatives.using(
            BWDatabaseRouter.get_export_database_name()
        ).values_list('name_of_issue', 'explanation_regarding_issue')
        values = [self.vawg_and_efm_reduction_initiatives.using(BWDatabaseRouter.get_export_database_name()).count()]
        for column_value in column_values:
            _name, _explanation = column_value
            values.append(_name if _name else '')
            values.append(_explanation if _explanation else '')

        return values

    @classmethod
    def safety_security_initiatives_export_column_titles(cls):
        _col_header_prefix = ['Total number of issues']
        column_name = ['Name of issue', 'Explanation']
        _max_no_initiatives = cls.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).annotate(total=Count('safety_security_initiatives')).aggregate(Max('total'))['total__max']
        _max_no_initiatives = _max_no_initiatives if _max_no_initiatives else 0
        return _col_header_prefix + ['{} {}'.format(_col_name, i + 1)
                                     for i in range(_max_no_initiatives) for _col_name in column_name]

    @property
    def safety_security_initiatives_export_column_values(self):
        column_values = self.safety_security_initiatives.using(
            BWDatabaseRouter.get_export_database_name()
        ).values_list('name_of_issue', 'explanation_regarding_issue')
        values = [self.safety_security_initiatives.using(BWDatabaseRouter.get_export_database_name()).count()]
        for column_value in column_values:
            _name, _explanation = column_value
            values.append(_name if _name else '')
            values.append(_explanation if _explanation else '')

        return values

    @classmethod
    def awareness_raising_by_sccs_export_column_titles(cls):
        _col_header_prefix = ['Total number of campaigns']
        column_name = ['Campaign Date', 'Explanation', 'Campaign Location',
                       'Female attending', 'Male attending',
                       'Transgender attending',
                       'Disabled male attending',
                       'Disabled female attending',
                       'LGI member attending',
                       'Campaign Key Messages', 'Name of Usage Method']
        _max_no_campaigns = cls.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).annotate(total=Count('awareness_raising_by_sccs')).aggregate(Max('total'))['total__max']
        _max_no_campaigns = _max_no_campaigns if _max_no_campaigns else 0
        return _col_header_prefix + ['{} {}'.format(_col_name, i + 1)
                                     for i in range(_max_no_campaigns) for _col_name in column_name]

    @property
    def awareness_raising_by_sccs_export_column_values(self):
        values = [self.awareness_raising_by_sccs.using(BWDatabaseRouter.get_export_database_name()).count()]
        for column_value in self.awareness_raising_by_sccs.using(BWDatabaseRouter.get_export_database_name()).all():
            values.append(column_value.campaign_date or '')
            values.append(column_value.activity_name or '')
            values.append(column_value.render_campaign_location)
            values.append(column_value.number_of_female_attending or '')
            values.append(column_value.number_of_male_attending or '')
            values.append(column_value.number_of_transgender_attending or '')
            values.append(column_value.number_of_disabled_male_attending or '')
            values.append(column_value.number_of_disabled_female_attending or '')
            values.append(column_value.number_of_lgi_member_attending or '')
            values.append(column_value.campaign_key_messages or '')
            values.append(column_value.name_of_usage_method or '')

        return values

    @classmethod
    def explored_partnerships_export_column_titles(cls):
        _col_header_prefix = ['Total number of partnerships']
        column_name = ['Are partnerships explored',
                       'With which organisation',
                       'Date of partnership',
                       'Partnership related to what']
        _max_no_partnerships = cls.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).annotate(total=Count('explored_partnerships')).aggregate(Max('total'))['total__max']
        _max_no_partnerships = _max_no_partnerships if _max_no_partnerships else 0
        return _col_header_prefix + ['{} {}'.format(_col_name, i + 1)
                                     for i in range(_max_no_partnerships) for _col_name in column_name]

    @property
    def explored_partnerships_export_column_values(self):
        values = [self.explored_partnerships.using(BWDatabaseRouter.get_export_database_name()).count()]
        for column_value in self.explored_partnerships.using(BWDatabaseRouter.get_export_database_name()).all():
            values.append(column_value.is_partnerships_explored or '')
            values.append(column_value.with_which_organisation or '')
            values.append(column_value.date_of_partnership or '')
            values.append(column_value.partnership_related_to_what or '')

        return values

    @classmethod
    def agreed_partnerships_export_column_titles(cls):
        _col_header_prefix = ['Total number of partnerships']
        column_name = ['Are partnerships agreed',
                       'With which organisation',
                       'Date of agreement',
                       'Duration of agreement',
                       'Partnership related to what']
        _max_no_partnerships = cls.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).annotate(total=Count('agreed_partnerships')).aggregate(Max('total'))['total__max']
        _max_no_partnerships = _max_no_partnerships if _max_no_partnerships else 0
        return _col_header_prefix + ['{} {}'.format(_col_name, i + 1)
                                     for i in range(_max_no_partnerships) for _col_name in column_name]

    @property
    def agreed_partnerships_export_column_values(self):
        values = [self.agreed_partnerships.using(BWDatabaseRouter.get_export_database_name()).count()]
        for column_value in self.agreed_partnerships.using(BWDatabaseRouter.get_export_database_name()).all():
            values.append(column_value.is_agreed_partnership or '')
            values.append(column_value.with_which_organisation or '')
            values.append(column_value.date_of_agreement or '')
            values.append(column_value.duration_of_agreement or '')
            values.append(column_value.partnership_related_to_what or '')

        return values

    @classmethod
    def activities_of_partnerships_export_column_titles(cls):
        _col_header_prefix = ['Total number of partnerships']
        column_name = ['Conducted partnership activities',
                       'With which organisation',
                       'Date of activity',
                       'Explanation of the activity']
        _max_no_partnerships = cls.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).annotate(total=Count('activities_of_partnerships')).aggregate(Max('total'))['total__max']
        _max_no_partnerships = _max_no_partnerships if _max_no_partnerships else 0
        return _col_header_prefix + ['{} {}'.format(_col_name, i + 1)
                                     for i in range(_max_no_partnerships) for _col_name in column_name]

    @property
    def activities_of_partnerships_export_column_values(self):
        values = [self.activities_of_partnerships.using(BWDatabaseRouter.get_export_database_name()).count()]
        for column_value in self.activities_of_partnerships.using(BWDatabaseRouter.get_export_database_name()).all():
            values.append(column_value.conducted_partnership_activities or '')
            values.append(column_value.with_which_organisation or '')
            values.append(column_value.date_of_activity or '')
            values.append(column_value.explanation_of_the_activity or '')

        return values
