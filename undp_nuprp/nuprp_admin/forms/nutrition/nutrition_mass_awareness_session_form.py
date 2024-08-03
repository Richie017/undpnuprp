from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models import NutritionMassAwarenessSession

__author__ = 'Mahbub, Shuvro'


class NutritionMassAwarenessSessionForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(NutritionMassAwarenessSessionForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

    class Meta(GenericFormMixin.Meta):
        model = NutritionMassAwarenessSession
        fields = (
            'number_of_events_held_last_month_by_type_of_issue', 'issue_name',
            'approximate_number_of_male_participants',
            'approximate_number_of_female_participants'
        )
        labels = {
            'number_of_events_held_last_month_by_type_of_issue':
                'Number of events held last month by type of issue/theme',
            'issue_name': 'Name of Events/Issue name',
            'approximate_number_of_male_participants': 'Number of male participants in the events',
            'approximate_number_of_female_participants': 'Number of female participants in the events'
        }
