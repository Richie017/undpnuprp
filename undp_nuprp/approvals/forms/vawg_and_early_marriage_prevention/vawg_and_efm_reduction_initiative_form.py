from django import forms

from blackwidow.core.forms.files.fileobject_form import FileObjectForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.vawg_and_efm_reduction_initiative import \
    VAWGEFMReductionInitiative

__author__ = 'Shuvro'

NAME_CHOICES = (('', 'Select One'), ('Awareness Raising', 'Awareness Raising'),
                ('Referral mechanism', 'Referral mechanism'), ('Advocacy and Networking', 'Advocacy and Networking'),
                ('Local Arbitration', 'Local Arbitration'), ('Other', 'Other'))


class VAWGEFMReductionInitiativeForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(VAWGEFMReductionInitiativeForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                             **kwargs)

        self.fields['name_of_issue'] = forms.ChoiceField(
            label='Name of the issue',
            initial=instance.name_of_issue if instance and instance.pk else None,
            required=False,
            choices=NAME_CHOICES,
            widget=forms.Select(
                attrs={'class': 'select2'}
            )
        )

        kwargs.update({
            'prefix': prefix + '-attachment'
        })

        self.add_child_form(
            "attachment", FileObjectForm(
                data=data, files=files,
                instance=instance.attachment if instance and instance.attachment else None,
                allow_login=True, form_header='Attachment', **kwargs
            )
        )

        self.fields['name_of_issue'].required = False
        self.fields['explanation_regarding_issue'].required = False

    class Meta(GenericFormMixin.Meta):
        model = VAWGEFMReductionInitiative
        fields = ('name_of_issue', 'explanation_regarding_issue')
        widgets = {
            'explanation_regarding_issue': forms.Textarea
        }
        labels = {
            'explanation_regarding_issue': 'Explanation'
        }
