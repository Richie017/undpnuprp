from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.finanical.financial_information import FinancialInformation


class FinancialInformationForm(GenericFormMixin):

    def __init__(self, data=None, files=None, instance=None, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)

    class Meta:
        model = FinancialInformation
        fields = ['dues', 'over_dues', 'last_do_quantity', 'last_delivery_quantity', 'sale_quantity' ]