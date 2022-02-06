from django.forms import modelformset_factory

from blackwidow.core.mixins.formmixin import GenericModelFormSetMixin
from undp_nuprp.nuprp_admin.forms.workshop.workshop_form import WorkshopForm
from undp_nuprp.nuprp_admin.models import Workshop


def make_workshop_formset(extra=1, max_num=100, min_num=0, validate_min=True, can_delete=True, **kwargs):
    form_set = modelformset_factory(Workshop, form=WorkshopForm, formset=GenericModelFormSetMixin,
                                    extra=extra, max_num=max_num, min_num=min_num, validate_min=validate_min,
                                    can_delete=can_delete, )

    class modified_formset(form_set):
        def save(self):
            super().save()
            return self.instance

    return modified_formset