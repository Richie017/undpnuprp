from datetime import datetime, date

from django import forms
from django.forms import Form
from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.route_partial_routes import route, partial_route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.utils.month_enum import MonthEnum
from undp_nuprp.nuprp_admin.models.nutrition.nutrition_mass_awareness_session import NutritionMassAwarenessSession

__author__ = 'Mahbub, Shuvro'


@decorate(is_object_context,
          route(route='nutrition-reporting', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis, display_name='Nutrition Reporting', group_order=3, item_order=23),
          partial_route(relation='normal', models=[NutritionMassAwarenessSession]))
class NutritionReporting(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True)
    month = models.IntegerField(default=1, null=True, blank=True)
    year = models.IntegerField(default=2020)
    no_of_100_day_hh_targeted_last_month = models.IntegerField(null=True, blank=True)
    no_of_pregnant_women_targeted_last_month = models.IntegerField(null=True, blank=True)
    no_of_lactating_women_targeted_last_month = models.IntegerField(null=True, blank=True)
    no_of_children_0_6_months_targeted_last_month = models.IntegerField(null=True, blank=True)
    no_of_children_7_24_months_targeted_last_month = models.IntegerField(null=True, blank=True)
    no_of_pregnant_women_received_one_counseling_session = models.IntegerField(null=True, blank=True)
    no_of_lactating_women_received_one_counseling_session = models.IntegerField(null=True, blank=True)
    no_of_hhs_children_0_6_months_received_alo_counseling_lm = models.IntegerField(null=True, blank=True)
    no_of_hhs_children_7_24_months_have_alo_counseling_last_month = models.IntegerField(
        null=True, blank=True)
    no_of_pg_targeted_for_nutrition_session_last_month = models.IntegerField(null=True, blank=True)
    no_of_pg_received_at_least_one_nutrition_session_last_month = models.IntegerField(null=True, blank=True)
    total_no_of_sessions_held_last_month = models.IntegerField(null=True, blank=True)
    no_of_children_7_24_months_screened_for_severe_malnourishment = models.IntegerField(null=True, blank=True)
    no_of_children_identified_as_severely_malnourished_last_month = models.IntegerField(null=True, blank=True)
    no_of_children_successfully_referred_last_month = models.IntegerField(null=True, blank=True)
    percent_of_pregnant_women_attending_anc_in_correct_schedule = models.IntegerField(null=True, blank=True)
    percent_of_lactating_women_attending_anc_in_schedule = models.IntegerField(null=True, blank=True)
    no_of_pregnant_women_who_received_sbcc_materials_last_month = models.IntegerField(null=True, blank=True)
    no_of_lactating_women_who_received_sbcc_materials_last_month = models.IntegerField(null=True, blank=True)
    no_of_hhs_children_7_24_months_have_one_counseling_last_month = models.IntegerField(null=True, blank=True)
    no_of_pregnant_women_who_received_foodstuff_last_month = models.IntegerField(null=True, blank=True)
    no_of_lactating_women_who_received_foodstuff_last_month = models.IntegerField(null=True, blank=True)
    no_of_hhs_children_7_24_months_received_foodstuff_last_month = models.IntegerField(null=True, blank=True)
    no_of_pregnant_women_graduating_last_month = models.IntegerField(null=True, blank=True)
    no_of_lactating_women_graduating_last_month = models.IntegerField(null=True, blank=True)
    no_of_hhs_with_children_7_24_months_graduating_last_month = models.IntegerField(null=True, blank=True)
    no_of_pregnant_women_newly_included_last_month = models.IntegerField(null=True, blank=True)
    no_of_lactating_women_newly_included_last_month = models.IntegerField(null=True, blank=True)
    no_of_hhs_with_children_0_6_months_newly_included_last_month = models.IntegerField(null=True, blank=True)
    no_of_hhs_with_children_7_24_months_newly_included_last_month = models.IntegerField(null=True, blank=True)
    no_of_hhs_have_hand_washing_facilities = models.IntegerField(null=True, blank=True)
    no_of_hhs_with_children_7_24_months_have_demo_on_hand_washing = models.IntegerField(null=True, blank=True)
    no_of_pregnant_women_consumed_food_basket_in_last_month = models.IntegerField(null=True, blank=True)
    no_of_lactating_mothers_consumed_food_basket_in_last_month = models.IntegerField(null=True, blank=True)
    no_of_children_consumed_food_basket_in_last_month = models.IntegerField(null=True, blank=True)
    no_of_meeting_of_clmsncc_organized_in_last_month = models.IntegerField(null=True, blank=True)
    no_of_clmsncc_member_participated_in_this_meeting = models.IntegerField(null=True, blank=True)
    nutrition_mass_awareness_sessions = models.ManyToManyField('nuprp_admin.NutritionMassAwarenessSession')

    class Meta:
        app_label = 'nuprp_admin'

    @property
    def detail_title(self):
        return mark_safe(str(self.display_name()))

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        return button

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit,
            ViewActionEnum.AdvancedExport, ViewActionEnum.Delete
        ]

    @property
    def render_month(self):
        return datetime.now().replace(month=self.month).strftime("%B")

    @classmethod
    def table_columns(cls):
        return [
            'code', 'city', 'year', 'render_month', 'created_by', 'date_created',
            'last_updated_by', 'last_updated:Last Updated On'
        ]

    @classmethod
    def details_view_fields(cls):
        return [
            'detail_title', 'city>Basic information', 'render_month>Basic information', 'year>Basic information',
            'created_by>Basic information', 'date_created>Basic information', 'last_updated_by>Basic information',
            'last_updated>Basic information',

            # General - section
            'no_of_100_day_hh_targeted_last_month:Number of 1,000 day HHs targeted last month '
            '(reporting month)>General',
            'no_of_pregnant_women_targeted_last_month:Number of pregnant women targeted last month '
            '(reporting month)>General',
            'no_of_lactating_women_targeted_last_month:Number of lactating women targeted last month '
            '( reporting month)>General',
            'no_of_children_0_6_months_targeted_last_month:Number of children, 0-6 months, '
            'targeted last month ( reporting month)>General',
            'no_of_children_7_24_months_targeted_last_month:Number of children, 7-24 months, '
            'targeted last month ( reporting month)>General',

            # Counseling - section
            'no_of_pregnant_women_received_one_counseling_session:Number of pregnant women who received at least '
            'one counseling session last month (reporting month)>Counseling',
            'no_of_lactating_women_received_one_counseling_session:Number of lactating women who received at least '
            'one counseling session last month (reporting month)>Counseling',
            'no_of_hhs_children_0_6_months_received_alo_counseling_lm:Number of HHs in which children, 0-6 months, '
            'received at least one counseling session last month (reporting month)>Counseling',
            'no_of_hhs_children_7_24_months_have_alo_counseling_last_month:Number of HHs in which children, '
            '7-24 months, received at least one counseling session last month (reporting month)>Counseling',

            # Primary groups nutrition sessions - section
            'no_of_pg_targeted_for_nutrition_session_last_month:Number of primary group targeted for '
            'nutrition session in last month (reporting month)>Primary groups nutrition sessions',
            'no_of_pg_received_at_least_one_nutrition_session_last_month:Number of primary groups that received '
            'at least one nutrition session last month (reporting month)>Primary groups nutrition sessions',
            'total_no_of_sessions_held_last_month:Total number of nutrition sessions held last month '
            '(reporting month)>Primary groups nutrition sessions',

            # Referrals - section
            'no_of_children_7_24_months_screened_for_severe_malnourishment:Number of children, 7-24 months, '
            'screened for severe malnourishment (SAM) by MUAC>Referrals',
            'no_of_children_identified_as_severely_malnourished_last_month:Number of SAM children identified by '
            'MUAC screening in last month (reporting month)>Referrals',
            'no_of_children_successfully_referred_last_month:Number of children received SAM services '
            'through referral (i.e. referred and attended) last month (reporting month)>Referrals',
            'percent_of_pregnant_women_attending_anc_in_correct_schedule:% of pregnant women attending ANC '
            'as per the correct schedule in last month (reporting month)>Referrals',
            'percent_of_lactating_women_attending_anc_in_schedule:% of lactating mother received PNC '
            'as per schedule in last month (reporting month)>Referrals',

            # Distribution of social and behaviour change communication (SBCC) materials - section
            'no_of_pregnant_women_who_received_sbcc_materials_last_month:Number of pregnant women who received SBCC '
            'materials last month (reporting month)>Distribution of social and behaviour '
            'change communication (SBCC) materials',
            'no_of_lactating_women_who_received_sbcc_materials_last_month:Number of lactating mother who received SBCC '
            'materials last month (reporting month)>Distribution of social and behaviour '
            'change communication (SBCC) materials',
            'no_of_hhs_children_7_24_months_have_one_counseling_last_month:Number of 7-24 months children who received '
            'SBCC materials in last month (reporting month)>Distribution of social and behaviour '
            'change communication (SBCC) materials',

            # In-kind food transfers - section
            'no_of_pregnant_women_who_received_foodstuff_last_month:Number of pregnant women who received '
            'food basket in last month (reporting month)>In-kind food transfers',
            'no_of_lactating_women_who_received_foodstuff_last_month:Number of lactating mothers who received '
            'food basket in last month (reporting month)>In-kind food transfers',
            'no_of_hhs_children_7_24_months_received_foodstuff_last_month:Number of 7-24 months children received '
            'food basket in last month (reporting month)>In-kind food transfers',
            'no_of_pregnant_women_consumed_food_basket_in_last_month:Number of pregnant women consumed food basket '
            'with maintaining full compliance in last month (reporting month)>In-kind food transfers',
            'no_of_lactating_mothers_consumed_food_basket_in_last_month:Number of Lactating Mothers consumed food '
            'basket with maintaining full compliance in last month (reporting month)>In-kind food transfers',
            'no_of_children_consumed_food_basket_in_last_month:Number of Children consumed food basket with '
            'maintaining full compliance in last month (reporting month)>In-kind food transfers',

            # New recruits and graduation - section
            'no_of_pregnant_women_graduating_last_month:Number of pregnant women graduate in '
            'last month (reporting month)>New recruits and graduation',
            'no_of_lactating_women_graduating_last_month:Number of lactating mother graduate in '
            'last month (reporting month)>New recruits and graduation',
            'no_of_hhs_with_children_7_24_months_graduating_last_month:Number of 0-24 months children graduate in '
            'last month (reporting month)>New recruits and graduation',
            'no_of_pregnant_women_newly_included_last_month:Number of pregnant women newly included/registered '
            'last month (reporting month)>New recruits and graduation',
            'no_of_lactating_women_newly_included_last_month:Number of lactating mother newly included/registred '
            'last month (reporting month)>New recruits and graduation',
            'no_of_hhs_with_children_0_6_months_newly_included_last_month:Number of 0-6 months children newly '
            'included/registered in last month (reporting month)>New recruits and graduation',
            'no_of_hhs_with_children_7_24_months_newly_included_last_month:Number of 7-24 months children newly '
            'included/registered in last month (reporting month)>New recruits and graduation',

            # Handwashing - section
            'no_of_hhs_have_hand_washing_facilities:Number of Tippy-tap/handwashing devices installed at HHs in '
            'last month (reporting month)>Handwashing',
            'no_of_hhs_with_children_7_24_months_have_demo_on_hand_washing:Number of 1000 days HHs received '
            'a demonstration on handwashing from the SENF in last month (reporting month)>Handwashing',

            #Nutrition Governance - section
            'no_of_meeting_of_clmsncc_organized_in_last_month:Number of meeting of CLMSNCC organized in last month '
            '(reporting month)>Nutrition Governance',
            'no_of_clmsncc_member_participated_in_this_meeting:Number of CLMSNCC member participated in this meeting '
            '(reporting month)>Nutrition Governance'
        ]

    @classmethod
    def export_file_columns(cls):
        return [
            'city', 'render_month', 'year', 'created_by',

            # General - section
            'no_of_100_day_hh_targeted_last_month:Number of 1,000 day HHs targeted last month '
            '(reporting month)>General',
            'no_of_pregnant_women_targeted_last_month:Number of pregnant women targeted last month '
            '(reporting month)>General',
            'no_of_lactating_women_targeted_last_month:Number of lactating women targeted last month '
            '( reporting month)>General',
            'no_of_children_0_6_months_targeted_last_month:Number of children, 0-6 months, '
            'targeted last month ( reporting month)>General',
            'no_of_children_7_24_months_targeted_last_month:Number of children, 7-24 months, '
            'targeted last month ( reporting month)>General',

            # Counseling - section
            'no_of_pregnant_women_received_one_counseling_session:Number of pregnant women who received at least '
            'one counseling session last month (reporting month)>Counseling',
            'no_of_lactating_women_received_one_counseling_session:Number of lactating women who received at least '
            'one counseling session last month (reporting month)>Counseling',
            'no_of_hhs_children_0_6_months_received_alo_counseling_lm:Number of HHs in which children, 0-6 months, '
            'received at least one counseling session last month (reporting month)>Counseling',
            'no_of_hhs_children_7_24_months_have_alo_counseling_last_month:Number of HHs in which children, '
            '7-24 months, received at least one counseling session last month (reporting month)>Counseling',

            # Primary groups nutrition sessions - section
            'no_of_pg_targeted_for_nutrition_session_last_month:Number of primary group targeted for '
            'nutrition session in last month (reporting month)>Primary groups nutrition sessions',
            'no_of_pg_received_at_least_one_nutrition_session_last_month:Number of primary groups that received '
            'at least one nutrition session last month (reporting month)>Primary groups nutrition sessions',
            'total_no_of_sessions_held_last_month:Total number of nutrition sessions held last month '
            '(reporting month)>Primary groups nutrition sessions',

            # Referrals - section
            'no_of_children_7_24_months_screened_for_severe_malnourishment:Number of children, 7-24 months, '
            'screened for severe malnourishment (SAM) by MUAC>Referrals',
            'no_of_children_identified_as_severely_malnourished_last_month:Number of SAM children identified by '
            'MUAC screening in last month (reporting month)>Referrals',
            'no_of_children_successfully_referred_last_month:Number of children received SAM services '
            'through referral (i.e. referred and attended) last month (reporting month)>Referrals',
            'percent_of_pregnant_women_attending_anc_in_correct_schedule:% of pregnant women attending ANC '
            'as per the correct schedule in last month (reporting month)>Referrals',
            'percent_of_lactating_women_attending_anc_in_schedule:% of lactating mother received PNC '
            'as per schedule in last month (reporting month)>Referrals',

            # Distribution of social and behaviour change communication (SBCC) materials - section
            'no_of_pregnant_women_who_received_sbcc_materials_last_month:Number of pregnant women who received SBCC '
            'materials last month (reporting month)>Distribution of social and behaviour '
            'change communication (SBCC) materials',
            'no_of_lactating_women_who_received_sbcc_materials_last_month:Number of lactating mother who received SBCC '
            'materials last month (reporting month)>Distribution of social and behaviour '
            'change communication (SBCC) materials',
            'no_of_hhs_children_7_24_months_have_one_counseling_last_month:Number of 7-24 months children who received '
            'SBCC materials in last month (reporting month)>Distribution of social and behaviour '
            'change communication (SBCC) materials',

            # In-kind food transfers - section
            'no_of_pregnant_women_who_received_foodstuff_last_month:Number of pregnant women who received '
            'food basket in last month (reporting month)>In-kind food transfers',
            'no_of_lactating_women_who_received_foodstuff_last_month:Number of lactating mothers who received '
            'food basket in last month (reporting month)>In-kind food transfers',
            'no_of_hhs_children_7_24_months_received_foodstuff_last_month:Number of 7-24 months children received '
            'food basket in last month (reporting month)>In-kind food transfers',
            'no_of_pregnant_women_consumed_food_basket_in_last_month:Number of pregnant women consumed food basket '
            'with maintaining full compliance in last month (reporting month)>In-kind food transfers',
            'no_of_lactating_mothers_consumed_food_basket_in_last_month:Number of Lactating Mothers consumed food '
            'basket with maintaining full compliance in last month (reporting month)>In-kind food transfers',
            'no_of_children_consumed_food_basket_in_last_month:Number of Children consumed food basket with '
            'maintaining full compliance in last month (reporting month)>In-kind food transfers',

            # New recruits and graduation - section
            'no_of_pregnant_women_graduating_last_month:Number of pregnant women graduate in '
            'last month (reporting month)>New recruits and graduation',
            'no_of_lactating_women_graduating_last_month:Number of lactating mother graduate in '
            'last month (reporting month)>New recruits and graduation',
            'no_of_hhs_with_children_7_24_months_graduating_last_month:Number of 0-24 months children graduate in '
            'last month (reporting month)>New recruits and graduation',
            'no_of_pregnant_women_newly_included_last_month:Number of pregnant women newly included/registered '
            'last month (reporting month)>New recruits and graduation',
            'no_of_lactating_women_newly_included_last_month:Number of lactating mother newly included/registred '
            'last month (reporting month)>New recruits and graduation',
            'no_of_hhs_with_children_0_6_months_newly_included_last_month:Number of 0-6 months children newly '
            'included/registered in last month (reporting month)>New recruits and graduation',
            'no_of_hhs_with_children_7_24_months_newly_included_last_month:Number of 7-24 months children newly '
            'included/registered in last month (reporting month)>New recruits and graduation',

            # Handwashing - section
            'no_of_hhs_have_hand_washing_facilities:Number of Tippy-tap/handwashing devices installed at HHs in '
            'last month (reporting month)>Handwashing',
            'no_of_hhs_with_children_7_24_months_have_demo_on_hand_washing:Number of 1000 days HHs received '
            'a demonstration on handwashing from the SENF in last month (reporting month)>Handwashing',

            # Nutrition Governance - section
            'no_of_meeting_of_clmsncc_organized_in_last_month:Number of meeting of CLMSNCC organized in last month '
            '(reporting month)>Nutrition Governance',
            'no_of_clmsncc_member_participated_in_this_meeting:Number of CLMSNCC member participated in this meeting '
            '(reporting month)>Nutrition Governance'
        ]

    @classmethod
    def export_tab_columns(cls):
        base_columns = [
            'Number of events held last month by type of issue/theme',
            'Name of Events/Issue name',
            'Number of male participants in the events',
            'Number of female participants in the events'
        ]
        export_tab_columns = []
        for i in range(1, 6):
            for column in base_columns:
                export_tab_columns.append('Creative Social Campaign/ Mass Awareness Event - {0}: {1}'.format(i, column))
        return export_tab_columns

    @classmethod
    def export_tab_items(cls, self):
        export_tab_queryset = self.nutrition_mass_awareness_sessions.values(
            'number_of_events_held_last_month_by_type_of_issue',
            'issue_name',
            'approximate_number_of_male_participants',
            'approximate_number_of_female_participants'
        )[:5]
        items = []
        for tab_instance in export_tab_queryset:
            data1 = tab_instance['number_of_events_held_last_month_by_type_of_issue']
            data2 = tab_instance['issue_name']
            data3 = tab_instance['approximate_number_of_male_participants']
            data4 = tab_instance['approximate_number_of_female_participants']
            items.append(data1)
            items.append(data2)
            items.append(data3)
            items.append(data4)
        return items

    @classmethod
    def get_export_dependant_fields(cls):
        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                today = date.today()
                year_choices = tuple()
                year_choices += (('', '---------'),)
                for y in range(2000, 2100):
                    year_choices += ((y, str(y)),)

                self.fields['city'] = \
                    GenericModelChoiceField(
                        queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
                        label='Select City',
                        required=False,
                        widget=forms.Select(
                            attrs={
                                'class': 'select2 kpi-filter',
                                'width': '220',
                                'data-kpi-filter-role': 'city'
                            }
                        )
                    )
                month_choices = (('', '---------'),) + MonthEnum.get_choices()
                self.fields['month'] = forms.ChoiceField(
                    label='Select Month',
                    choices=month_choices,
                    initial=date.today().month,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ),
                    required=False
                )
                self.fields['year'] = forms.ChoiceField(
                    label='Select Year',
                    choices=year_choices,
                    initial=today.year,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ),
                    required=False
                )

        return AdvancedExportDependentForm

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Creative Social Campaign/ Mass Awareness Event',
                access_key='nutrition_awareness_sessions',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model='nuprp_admin.NutritionMassAwarenessSession',
                property=self.nutrition_mass_awareness_sessions
            )
        ]
