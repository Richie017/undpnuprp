from blackwidow.core.models.alert_config.alert_config import AlertConfig

__author__ = "Shama"


class NuprpAlertBaseConfig(AlertConfig):

    class Meta:
        app_label = 'nuprp_admin'

    @property
    def get_inline_manage_buttons(self):
        return []

    @classmethod
    def table_columns(cls):
        return ['code', 'date_created', 'last_updated']