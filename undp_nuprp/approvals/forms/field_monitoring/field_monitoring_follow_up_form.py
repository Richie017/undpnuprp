from blackwidow.core.mixins.formmixin import GenericFormMixin
from undp_nuprp.approvals.models import FieldMonitoringFollowup


class FieldMonitoringFollowupForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(FieldMonitoringFollowupForm, self).__init__(data=data, files=files, instance=instance,
                                                          prefix=prefix, **kwargs)

    class Meta(GenericFormMixin.Meta):
        model = FieldMonitoringFollowup

        fields = ('key_observation', 'key_actions', 'person_responsible_for_key_action')

        labels = {
            'key_observation': 'Key observation (please explain in brief what is your observation of the visited '
                               'activities)',
            'key_actions': 'Key actions (what kind of action city/person need to take for resolving issues)',
            'person_responsible_for_key_action': 'Person responsible for key action (Who is the person or persons '
                                                 'responsible for resolving the issues)'
        }
