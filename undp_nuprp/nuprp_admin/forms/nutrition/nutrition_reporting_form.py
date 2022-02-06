from datetime import date

from django import forms
from django.forms import modelformset_factory

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models import Geography
from undp_nuprp.approvals.utils.month_enum import MonthEnum
from undp_nuprp.nuprp_admin.forms.nutrition.nutrition_mass_awareness_session_form import \
    NutritionMassAwarenessSessionForm
from undp_nuprp.nuprp_admin.models import NutritionMassAwarenessSession
from undp_nuprp.nuprp_admin.models.nutrition.nutrition_reporting import NutritionReporting

__author__ = "Mahbub, Shuvro"

nutrition_awareness_session_formset = modelformset_factory(
    NutritionMassAwarenessSession, form=NutritionMassAwarenessSessionForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)


class NutritionReportingForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(NutritionReportingForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        if instance and instance.pk:
            sessions = instance.nutrition_mass_awareness_sessions.all()
        else:
            sessions = NutritionMassAwarenessSession.objects.none()

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City', empty_label='Select One', required=False,
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )

        self.fields['month'] = forms.ChoiceField(
            choices=MonthEnum.get_choices(), required=False,
            initial=date.today().month if self.is_new_instance else instance.month,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ),
        )
        self.fields['year'] = forms.ChoiceField(
            choices=[(y, str(y)) for y in range(2000, 2100)],
            initial=date.today().year if not instance else instance.year,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ),
            required=False
        )

        self.add_child_form("nutrition_mass_awareness_sessions", nutrition_awareness_session_formset(
            data=data, files=files, queryset=sessions,
            header='Creative Social Campaign/ Mass Awareness Event', add_more=True, **kwargs
        ))

    @classmethod
    def get_template(cls):
        return 'very_large_labelled_form/very_large_labelled_form.html'

    class Meta(GenericFormMixin.Meta):
        model = NutritionReporting
        fields = (
            'city', 'month', 'year', 'no_of_100_day_hh_targeted_last_month', 'no_of_pregnant_women_targeted_last_month',
            'no_of_lactating_women_targeted_last_month', 'no_of_children_0_6_months_targeted_last_month',
            'no_of_children_7_24_months_targeted_last_month', 'no_of_pregnant_women_received_one_counseling_session',
            'no_of_lactating_women_received_one_counseling_session',
            'no_of_hhs_children_0_6_months_received_alo_counseling_lm',
            'no_of_hhs_children_7_24_months_have_alo_counseling_last_month',
            'no_of_pg_targeted_for_nutrition_session_last_month',
            'no_of_pg_received_at_least_one_nutrition_session_last_month',
            'total_no_of_sessions_held_last_month',
            'no_of_children_7_24_months_screened_for_severe_malnourishment',
            'no_of_children_identified_as_severely_malnourished_last_month',
            'no_of_children_successfully_referred_last_month',
            'percent_of_pregnant_women_attending_anc_in_correct_schedule',
            'percent_of_lactating_women_attending_anc_in_schedule',
            'no_of_pregnant_women_who_received_sbcc_materials_last_month',
            'no_of_lactating_women_who_received_sbcc_materials_last_month',
            'no_of_hhs_children_7_24_months_have_one_counseling_last_month',
            'no_of_pregnant_women_who_received_foodstuff_last_month',
            'no_of_lactating_women_who_received_foodstuff_last_month',
            'no_of_hhs_children_7_24_months_received_foodstuff_last_month',
            'no_of_pregnant_women_graduating_last_month',
            'no_of_lactating_women_graduating_last_month',
            'no_of_hhs_with_children_7_24_months_graduating_last_month',
            'no_of_pregnant_women_newly_included_last_month',
            'no_of_lactating_women_newly_included_last_month',
            'no_of_hhs_with_children_0_6_months_newly_included_last_month',
            'no_of_hhs_with_children_7_24_months_newly_included_last_month',
            'no_of_hhs_have_hand_washing_facilities',
            'no_of_hhs_with_children_7_24_months_have_demo_on_hand_washing',
            'no_of_pregnant_women_consumed_food_basket_in_last_month',
            'no_of_lactating_mothers_consumed_food_basket_in_last_month',
            'no_of_children_consumed_food_basket_in_last_month',
            'no_of_meeting_of_clmsncc_organized_in_last_month',
            'no_of_clmsncc_member_participated_in_this_meeting'
        )

        labels = {
            # General - section
            'no_of_100_day_hh_targeted_last_month': 'Number of 1,000 day HHs targeted last month (reporting month)',
            'no_of_pregnant_women_targeted_last_month':
                'Number of pregnant women targeted last month (reporting month)',
            'no_of_lactating_women_targeted_last_month':
                'Number of lactating women targeted last month ( reporting month)',
            'no_of_children_0_6_months_targeted_last_month':
                'Number of children, 0-6 months, targeted last month ( reporting month)',
            'no_of_children_7_24_months_targeted_last_month':
                'Number of children, 7-24 months, targeted last month ( reporting month)',

            # Counseling - section
            'no_of_pregnant_women_received_one_counseling_session':
                'Number of pregnant women who received at least one counseling session last month (reporting month)',
            'no_of_lactating_women_received_one_counseling_session':
                'Number of lactating women who received at least one counseling session last month (reporting month)',
            'no_of_hhs_children_0_6_months_received_alo_counseling_lm':
                'Number of HHs in which children, 0-6 months, received at least '
                'one counseling session last month (reporting month)',
            'no_of_hhs_children_7_24_months_have_alo_counseling_last_month':
                'Number of HHs in which children, 7-24 months, received at least '
                'one counseling session last month (reporting month)',

            # Primary groups nutrition sessions - section
            'no_of_pg_targeted_for_nutrition_session_last_month':
                'Number of primary group targeted for nutrition session in last month (reporting month)',
            'no_of_pg_received_at_least_one_nutrition_session_last_month':
                'Number of primary groups that received at least one nutrition session last month (reporting month)',
            'total_no_of_sessions_held_last_month':
                'Total number of nutrition sessions held last month (reporting month)',

            # Referrals - section
            'no_of_children_7_24_months_screened_for_severe_malnourishment':
                'Number of children, 7-24 months, screened for severe malnourishment (SAM) by MUAC',
            'no_of_children_identified_as_severely_malnourished_last_month':
                'Number of SAM children identified by MUAC screening in last month (reporting month)',
            'no_of_children_successfully_referred_last_month':
                'Number of children received SAM services through referral (i.e. referred and attended) '
                'last month (reporting month)',
            'percent_of_pregnant_women_attending_anc_in_correct_schedule':
                '% of pregnant women attending ANC as per the correct schedule in last month (reporting month)',
            'percent_of_lactating_women_attending_anc_in_schedule':
                '% of lactating mother received PNC as per schedule in last month (reporting month)',

            # Distribution of social and behaviour change communication (SBCC) materials - section
            'no_of_pregnant_women_who_received_sbcc_materials_last_month':
                'Number of pregnant women who received SBCC materials last month (reporting month)',
            'no_of_lactating_women_who_received_sbcc_materials_last_month':
                'Number of lactating mother who received SBCC materials last month (reporting month)',
            'no_of_hhs_children_7_24_months_have_one_counseling_last_month':
                'Number of 7-24 months children who received SBCC materials in last month (reporting month)',

            # In-kind food transfers - section
            'no_of_pregnant_women_who_received_foodstuff_last_month':
                'Number of pregnant women who received food basket in last month (reporting month)',
            'no_of_lactating_women_who_received_foodstuff_last_month':
                'Number of lactating mothers who received food basket in last month (reporting month)',
            'no_of_hhs_children_7_24_months_received_foodstuff_last_month':
                'Number of 7-24 months children received food basket in last month (reporting month)',
            'no_of_pregnant_women_consumed_food_basket_in_last_month':
                'Number of pregnant women consumed food basket with maintaining full compliance in last month '
                '(reporting month)',
            'no_of_lactating_mothers_consumed_food_basket_in_last_month':
                'Number of Lactating Mothers consumed food basket with maintaining full compliance in last month '
                '(reporting month)',
            'no_of_children_consumed_food_basket_in_last_month':
                'Number of Children consumed food basket with maintaining full compliance in last month '
                '(reporting month)',

            # New recruits and graduation - section# New recruits and graduation - section
            'no_of_pregnant_women_graduating_last_month':
                'Number of pregnant women graduate in last month (reporting month)',
            'no_of_lactating_women_graduating_last_month':
                'Number of lactating mother graduate in last month (reporting month)',
            'no_of_hhs_with_children_7_24_months_graduating_last_month':
                'Number of 0-24 months children graduate in last month (reporting month)',
            'no_of_pregnant_women_newly_included_last_month':
                'Number of pregnant women newly included/registered last month (reporting month)',
            'no_of_lactating_women_newly_included_last_month':
                'Number of lactating mother newly included/registred last month (reporting month)',
            'no_of_hhs_with_children_0_6_months_newly_included_last_month':
                'Number of 0-6 months children newly included/registered in last month (reporting month)',
            'no_of_hhs_with_children_7_24_months_newly_included_last_month':
                'Number of 7-24 months children newly included/registered in last month (reporting month)',

            # Handwashing - section
            'no_of_hhs_have_hand_washing_facilities':
                'Number of Tippy-tap/handwashing devices installed at HHs in last month (reporting month)',
            'no_of_hhs_with_children_7_24_months_have_demo_on_hand_washing':
                'Number of 1000 days HHs received a demonstration on handwashing from the SENF in '
                'last month (reporting month)',

            #Nutrition Governance - section
            'no_of_meeting_of_clmsncc_organized_in_last_month':
                'Number of meeting of CLMSNCC organized in last month (reporting month)',
            'no_of_clmsncc_member_participated_in_this_meeting':
                'Number of CLMSNCC member participated in this meeting (reporting month)'
        }

    @classmethod
    def field_groups(cls):
        _group = super(NutritionReportingForm, cls).field_groups()
        _group['Basic information'] = ['city', 'month', 'year']

        _group['General'] = [
            'no_of_100_day_hh_targeted_last_month', 'no_of_pregnant_women_targeted_last_month',
            'no_of_lactating_women_targeted_last_month',
            'no_of_children_0_6_months_targeted_last_month',
            'no_of_children_7_24_months_targeted_last_month'
        ]

        _group['Counseling'] = [
            'no_of_pregnant_women_received_one_counseling_session',
            'no_of_lactating_women_received_one_counseling_session',
            'no_of_hhs_children_0_6_months_received_alo_counseling_lm',
            'no_of_hhs_children_7_24_months_have_alo_counseling_last_month'
        ]

        _group['Primary groups nutrition sessions'] = [
            'no_of_pg_targeted_for_nutrition_session_last_month',
            'no_of_pg_received_at_least_one_nutrition_session_last_month',
            'total_no_of_sessions_held_last_month'
        ]

        _group['Referrals'] = [
            'no_of_children_7_24_months_screened_for_severe_malnourishment',
            'no_of_children_identified_as_severely_malnourished_last_month',
            'no_of_children_successfully_referred_last_month',
            'percent_of_pregnant_women_attending_anc_in_correct_schedule',
            'percent_of_lactating_women_attending_anc_in_schedule'
        ]

        _group['Distribution of social and behaviour change communication (SBCC) materials'] = [
            'no_of_pregnant_women_who_received_sbcc_materials_last_month',
            'no_of_lactating_women_who_received_sbcc_materials_last_month',
            'no_of_hhs_children_7_24_months_have_one_counseling_last_month',
        ]

        _group['In-kind food transfers'] = [
            'no_of_pregnant_women_who_received_foodstuff_last_month',
            'no_of_lactating_women_who_received_foodstuff_last_month',
            'no_of_hhs_children_7_24_months_received_foodstuff_last_month',
            'no_of_pregnant_women_consumed_food_basket_in_last_month',
            'no_of_lactating_mothers_consumed_food_basket_in_last_month',
            'no_of_children_consumed_food_basket_in_last_month'
        ]

        _group['New recruits and graduation'] = [
            'no_of_pregnant_women_graduating_last_month',
            'no_of_lactating_women_graduating_last_month',
            'no_of_hhs_with_children_7_24_months_graduating_last_month',
            'no_of_pregnant_women_newly_included_last_month',
            'no_of_lactating_women_newly_included_last_month',
            'no_of_hhs_with_children_0_6_months_newly_included_last_month',
            'no_of_hhs_with_children_7_24_months_newly_included_last_month'
        ]

        _group['Handwashing'] = [
            'no_of_hhs_have_hand_washing_facilities',
            'no_of_hhs_with_children_7_24_months_have_demo_on_hand_washing'
        ]

        _group['Nutrition Governance'] = ['no_of_meeting_of_clmsncc_organized_in_last_month',
                                          'no_of_clmsncc_member_participated_in_this_meeting']

        return _group
