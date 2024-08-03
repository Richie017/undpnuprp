from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.bank_info import MobileBankingDetails

__author__ = 'ruddra'


class MobileBankingForm(GenericFormMixin):

    class Meta(GenericFormMixin.Meta):
        model = MobileBankingDetails
        fields = ['service_provider', 'account_name', 'mobile_number']
