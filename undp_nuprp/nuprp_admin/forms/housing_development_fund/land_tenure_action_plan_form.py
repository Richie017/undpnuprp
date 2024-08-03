from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.housing_development_fund.land_tenure_action_plan import LandTenureActionPlan

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class LandTenureActionPlanForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(LandTenureActionPlanForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                       **kwargs)

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

        self.fields['land_tenure_action_plan_required'] = forms.ChoiceField(
            required=False,
            label='Land tenure action plan required?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.land_tenure_action_plan_required if instance and instance.pk else None
        )

        self.fields['started'] = forms.ChoiceField(
            required=False,
            label='Started?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.started if instance and instance.pk else None
        )

        self.fields['developed'] = forms.ChoiceField(
            required=False,
            label='Developed?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.developed if instance and instance.pk else None
        )

        self.fields['implemented'] = forms.ChoiceField(
            required=False,
            label='Implemented?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.implemented if instance and instance.pk else None
        )

    class Meta(GenericFormMixin.Meta):
        model = LandTenureActionPlan

        fields = (
            'city', 'land_tenure_action_plan_required', 'started', 'developed', 'implemented'
        )
