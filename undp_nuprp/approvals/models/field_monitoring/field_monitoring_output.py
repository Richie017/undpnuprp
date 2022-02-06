from blackwidow.core.models.contracts.configurabletype import ConfigurableType


class FieldMonitoringOutput(ConfigurableType):
    class Meta:
        app_label = 'approvals'

    def get_choice_name(self):
        return self.name
