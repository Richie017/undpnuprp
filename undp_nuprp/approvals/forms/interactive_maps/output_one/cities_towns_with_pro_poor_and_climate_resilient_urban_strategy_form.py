from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.approvals.models import CitiesTownsWithProPoorClimateResilientUrbanStrategy

__author__ = 'Kaikobud'

Status_Choices = \
    (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'), ('Ongoing', 'Ongoing'), ('Not applicable', 'Not applicable'))
Stage_choices = \
    (('', 'Select One'), ('Stage 1', 'Stage 1'), ('Stage 2', 'Stage 2'), ('Stage 3', 'Stage 3'))
Name_of_Assessment_Choices = \
    (('', 'Select one'),
     ("Poverty Mapping / Assessment", "Poverty Mapping / Assessment"),
     ("Mapping donor efforts in the city", "Mapping donor efforts in the city"),
     ("Standing Committee and Coordination Committee Assessment of the Local Government",
      "Standing Committee and Coordination Committee Assessment of the Local Government"),
     ("Institutional and Financial Capacity Assessment of the Local Government",
      "Institutional and Financial Capacity Assessment of the Local Government"),
     ("CDC Capacity Assessment", "CDC Capacity Assessment"),
     ("Capacity Assessment of CDC Town Federation", "Capacity Assessment of CDC Town Federation"),
     ("PG Member Registration", "PG Member Registration"),
     ("Local job market assessment", "Local job market assessment"),
     ("Gender Based Violence Assessment", "Gender Based Violence Assessment"),
     ("Nutrition Assessment", "Nutrition Assessment",),
     ("Disability Assessment", "Disability Assessment"),
     ("Infrastructure Assessment", "Infrastructure Assessment"),
     ("Climate Change Vulnerability Assessment (CCVA)", "Climate Change Vulnerability Assessment (CCVA)"),
     ("Vacant Land Mapping/Assessment (VLM)", "Vacant Land Mapping/Assessment (VLM)"),
     ("Housing and Land Tenure Assessment", "Housing and Land Tenure Assessment")
     )
Name_of_Component_Choices = \
    (('', 'Select one'),
     ('Improved coordination, planning and management in programme towns and cities',
      'Improved coordination, planning and management in programme towns and cities'),
     ('Enhanced organization, capability and effective voice of poor urban communities',
      'Enhanced organization, capability and effective voice of poor urban communities'),
     ('Improved well-being in poor urban slums particularly for women and girls',
      ' Improved well-being in poor urban slums particularly for women and girls'),
     ('More secure land tenure and housing in programme towns and cities',
      'More secure land tenure and housing in programme towns and cities'),
     ('More and better climate-resilient and community-based infrastructure in programme towns and cities',
      'More and better climate-resilient and community-based infrastructure in programme towns and cities'),
     )


class CitiesTownsWithProPoorClimateResilientUrbanStrategyForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CitiesTownsWithProPoorClimateResilientUrbanStrategyForm, self).__init__(data=data, files=files,
                                                                                      instance=instance, prefix=prefix,
                                                                                      **kwargs)

        self.fields['stage'] = forms.ChoiceField(
            label='Stage',
            choices=Stage_choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.stage if instance and instance.pk else None
        )

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )

        self.fields['name_of_component'] = forms.ChoiceField(
            label='Name of Component',
            choices=Name_of_Component_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.name_of_component if instance and instance.pk else None
        )

        self.fields['name_of_assessment'] = forms.ChoiceField(
            label='Name of assessment',
            choices=Name_of_Assessment_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.name_of_assessment if instance and instance.pk else None
        )

        self.fields['status'] = forms.ChoiceField(
            label='Status',
            choices=Status_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.status if instance and instance.pk else None
        )

    class Meta(GenericFormMixin.Meta):
        model = CitiesTownsWithProPoorClimateResilientUrbanStrategy
        fields = (
            'stage', 'city', 'name_of_component', 'name_of_assessment', 'status'
        )
