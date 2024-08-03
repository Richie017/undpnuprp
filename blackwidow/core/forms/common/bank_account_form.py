from blackwidow.core.forms.files.imagefileobject_form import ImageFileObjectForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.bank_info import BankAccountDetails


__author__ = 'ruddra'


class BankAccountForm(GenericFormMixin):

    def __init__(self, *args, instance=None, prefix='', form_header='', **kwargs):
        super().__init__(*args, instance=instance, prefix=prefix, form_header=form_header, **kwargs)
        self.add_child_form("image_of_bank_cheque", ImageFileObjectForm(*args, instance=instance.image_of_bank_cheque if instance is not None else None, form_header=form_header + '- Image of bank cheque', prefix=prefix + '-0', **kwargs))

    class Meta(GenericFormMixin.Meta):
        model = BankAccountDetails
        fields = ['bank_name', 'branch_name', 'routing_number', 'account_name', 'account_number']
