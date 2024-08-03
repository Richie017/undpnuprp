from blackwidow.core.models.information.alert import Alert

__author__ = 'shamil'


class AlertBase(Alert):
    class Meta:
        proxy = True
        app_label = 'nuprp_admin'
