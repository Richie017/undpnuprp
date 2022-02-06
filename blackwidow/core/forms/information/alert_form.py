from blackwidow.core.forms.information.information_object_form import InformationObjectForm
from blackwidow.core.models.information.alert import Alert

__author__ = 'Mahmud'


class AlertForm(InformationObjectForm):
    class Meta(InformationObjectForm.Meta):
        model = Alert