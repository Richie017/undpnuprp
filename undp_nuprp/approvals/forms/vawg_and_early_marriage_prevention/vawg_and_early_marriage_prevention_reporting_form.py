from collections import OrderedDict
from datetime import date

from django import forms
from django.forms.models import modelformset_factory
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.forms.vawg_and_early_marriage_prevention.awareness_raising_by_scc_form import \
    AwarenessRaisingBySCCForm
from undp_nuprp.approvals.forms.vawg_and_early_marriage_prevention.safety_security_initiative_form import \
    SafetySecurityInitiativeForm
from undp_nuprp.approvals.forms.vawg_and_early_marriage_prevention.scc_partnership.activities_of_partnership_form import \
    ActivitiesOfPartnershipForm
from undp_nuprp.approvals.forms.vawg_and_early_marriage_prevention.scc_partnership.agreed_partnership_form import \
    AgreedPartnershipForm
from undp_nuprp.approvals.forms.vawg_and_early_marriage_prevention.scc_partnership.explored_partnership_form import \
    ExploredPartnershipForm
from undp_nuprp.approvals.forms.vawg_and_early_marriage_prevention.scc_partnership.function_of_scc_form import \
    FunctionOfSCCForm
from undp_nuprp.approvals.forms.vawg_and_early_marriage_prevention.vawg_and_efm_reduction_initiative_form import \
    VAWGEFMReductionInitiativeForm
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
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.vawg_and_early_marriage_prevention_reporting import \
    VAWGEarlyMarriagePreventionReporting
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.vawg_and_efm_reduction_initiative import \
    VAWGEFMReductionInitiative
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster

__author__ = 'Shuvro'

Yes_No_Choices = [('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'), ]

YEAR_CHOICES = [('', "Select One"), ]
for year in range(2000, 2101):
    YEAR_CHOICES += [(year, str(year)), ]

MONTH_CHOICES = [
    ('', "Select One"), ('January', "January"), ('February', "February"), ('March', "March"),
    ('April', "April"), ('May', "May"), ('June', "June"), ('July', "July"), ('August', "August"),
    ('September', "September"), ('October', "October"), ('November', "November"), ('December', "December")
]

vawgefm_reduction_initiatives_formset = modelformset_factory(
    VAWGEFMReductionInitiative, form=VAWGEFMReductionInitiativeForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

safety_security_initiatives_formset = modelformset_factory(
    SafetySecurityInitiative, form=SafetySecurityInitiativeForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

awareness_raising_by_sccs_formset = modelformset_factory(
    AwarenessRaisingBySCC, form=AwarenessRaisingBySCCForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

activities_of_partnerships_formset = modelformset_factory(
    ActivitiesOfPartnership, form=ActivitiesOfPartnershipForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

agreed_partnerships_formset = modelformset_factory(
    AgreedPartnership, form=AgreedPartnershipForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

explored_partnerships_formset = modelformset_factory(
    ExploredPartnership, form=ExploredPartnershipForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

function_of_scc_formset = modelformset_factory(
    FunctionOfSCC, form=FunctionOfSCCForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)


class VAWGEarlyMarriagePreventionReportingForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(VAWGEarlyMarriagePreventionReportingForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        if instance and instance.pk:
            # vawgefm_reduction_initiatives_objects = instance.vawg_and_efm_reduction_initiatives.all()
            safety_security_initiatives_objects = instance.safety_security_initiatives.all()
            awareness_raising_by_sccs_objects = instance.awareness_raising_by_sccs.all()
            activities_of_partnerships_objects = instance.activities_of_partnerships.all()
            explored_partnerships_objects = instance.explored_partnerships.all()
            agreed_partnerships_objects = instance.agreed_partnerships.all()
        else:
            # vawgefm_reduction_initiatives_objects = VAWGEFMReductionInitiative.objects.none()
            safety_security_initiatives_objects = SafetySecurityInitiative.objects.none()
            awareness_raising_by_sccs_objects = AwarenessRaisingBySCC.objects.none()
            activities_of_partnerships_objects = ActivitiesOfPartnership.objects.none()
            explored_partnerships_objects = ExploredPartnership.objects.none()
            agreed_partnerships_objects = AgreedPartnership.objects.none()

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
            initial=instance.city if instance and instance.pk else None,
            label='City',
            empty_label='Select One',
            required=False,
            widget=forms.Select(
                attrs={
                    'class': 'select2',
                    'width': '220',
                }
            )
        )

        self.fields['year'] = forms.ChoiceField(
            choices=YEAR_CHOICES, required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=date.today().year
        )

        self.fields['month'] = forms.ChoiceField(
            choices=MONTH_CHOICES, required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=date.today().month
        )

        self.fields['cdc_cluster'] = GenericModelChoiceField(
            required=False,
            queryset=CDCCluster.objects.all(), label='CDC Cluster',
            initial=instance.cdc_cluster if instance and instance.pk else None,
            widget=forms.TextInput(attrs={
                'class': 'select2-input', 'width': '220',
                'data-depends-on': 'city',
                'data-depends-property': 'address:geography:id',
                'data-url': reverse(
                    CDCCluster.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
            }))

        self.fields['has_a_committee_been_formed'] = forms.ChoiceField(
            label='Has a committee been formed?',
            choices=Yes_No_Choices,
            required=False,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_a_committee_been_formed if instance and instance.pk else None
        )

        self.fields['has_a_constitution_been_prepared'] = forms.ChoiceField(
            label='Has a constitution been prepared?',
            required=False,
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.has_a_constitution_been_prepared if instance and instance.pk else None
        )

        self.fields['name_of_scc'].required = False
        # self.fields['composition_of_the_committee'].required = True

        self.fields['number_of_male'].required = False
        self.fields['number_of_female'].required = False
        self.fields['number_of_disabled_male'].required = False
        self.fields['number_of_disabled_female'].required = False
        self.fields['number_of_transsexual'].required = False
        self.fields['total_number_of_people'].required = False
        self.fields['total_number_of_people'].widget.attrs['readonly'] = True

        self.add_child_form("function_of_scc", FunctionOfSCCForm(
            data=data, files=files, instance=instance.function_of_scc if instance and instance.pk else None,
            form_header='Functioning of SCCs', prefix='function_of_scc', **kwargs))

        # self.add_child_form("vawg_and_efm_reduction_initiatives", vawgefm_reduction_initiatives_formset(
        #     data=data, files=files, queryset=vawgefm_reduction_initiatives_objects,
        #     prefix='vawgefm_reduction_initiatives',
        #     header='Initiatives have been taken by the SCC to reduce VAWG and EFM',
        #     add_more=True, **kwargs
        # ))

        self.add_child_form("safety_security_initiatives", safety_security_initiatives_formset(
            data=data, files=files, queryset=safety_security_initiatives_objects,
            prefix='safety_security_initiatives',
            header='Initiatives have been taken by the SCC to increase safety, security and gender friendly communities',
            add_more=True, **kwargs
        ))

        self.add_child_form("awareness_raising_by_sccs", awareness_raising_by_sccs_formset(
            data=data, files=files, queryset=awareness_raising_by_sccs_objects,
            prefix='awareness_raising_by_sccs',
            header='Awareness raising/campaign activities took place during the last month',
            add_more=True, **kwargs
        ))

        self.add_child_form("explored_partnerships", explored_partnerships_formset(
            data=data, files=files, queryset=explored_partnerships_objects,
            prefix='explored_partnerships',
            header='Explored Partnerships',
            add_more=True, **kwargs
        ))

        self.add_child_form("agreed_partnerships", agreed_partnerships_formset(
            data=data, files=files, queryset=agreed_partnerships_objects,
            prefix='agreed_partnerships',
            header='Agreed Partnerships',
            add_more=True, **kwargs
        ))

        self.add_child_form("activities_of_partnerships", activities_of_partnerships_formset(
            data=data, files=files, queryset=activities_of_partnerships_objects,
            prefix='activities_of_partnerships',
            header='Activities of partnerships',
            add_more=True, **kwargs
        ))

    class Meta(GenericFormMixin.Meta):
        model = VAWGEarlyMarriagePreventionReporting
        fields = [
            'city', 'year', 'month', 'cdc_cluster', 'name_of_scc',
            'has_a_committee_been_formed', 'has_a_constitution_been_prepared',
            'number_of_male', 'number_of_female',
            'number_of_disabled_male', 'number_of_disabled_female',
            'number_of_transsexual', 'total_number_of_people'
        ]

        labels = {
            'name_of_scc': 'Name of SCC',
            # 'composition_of_the_committee': 'What is the composition of the Committee?'
            'number_of_disabled_male': 'Number of disabled (Male)',
            'number_of_disabled_female': 'Number of disabled (Female)'
        }

        widgets = {
            'name_of_scc': forms.TextInput
            # 'composition_of_the_committee': forms.TextInput
        }

        render_tab = True
        tabs = OrderedDict([
            ('Support to safe community committees', [
                'city', 'year', 'month', 'cdc_cluster', 'name_of_scc', 'has_a_committee_been_formed',
                'has_a_constitution_been_prepared',
                # 'composition_of_the_committee',
                'number_of_male', 'number_of_female',
                'number_of_disabled_male', 'number_of_disabled_female',
                'number_of_transsexual', 'total_number_of_people',
                'function_of_scc', 'vawg_and_efm_reduction_initiatives',
                'safety_security_initiatives'
            ]),
            ('Awareness Raising Campaigns by SCC (Supported by NUPRP)', ['awareness_raising_by_sccs']),
            ('Partnership between NUPRP & Others',
             ['explored_partnerships', 'agreed_partnerships', 'activities_of_partnerships'])
        ])

    @classmethod
    def field_groups(cls):
        _group = super(VAWGEarlyMarriagePreventionReportingForm, cls).field_groups()
        _group['Establishment of SCCs (for each SCC that has been established, enter the following information)'] = [
            'city', 'year', 'month', 'cdc_cluster', 'name_of_scc', 'has_a_committee_been_formed',
            'has_a_constitution_been_prepared', 'number_of_male', 'number_of_female',
            'number_of_disabled_male', 'number_of_disabled_female', 'number_of_transsexual', 'total_number_of_people'
        ]
        return _group
