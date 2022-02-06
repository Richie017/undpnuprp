from django import forms
from django.db import transaction

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.qr_code import QRCode

__author__ = 'Mahmud'


class QRCodeForm(GenericFormMixin):
    id = forms.CharField(required=False)

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['id'].label = 'Reference ID'

    # def clean(self):
    #     ref_id = self.cleaned_data['id']
    #     if ref_id == '':
    #        raise BWException('Please enter reference id of the QR Code.')
    #     return super().clean()


    def save(self, commit=True):
        with transaction.atomic():
            self.instance = None
            ref_id = self.cleaned_data['id']

            if ref_id != '':
                qrcodes = QRCode.objects.filter(id=int(ref_id))
                if qrcodes.exists():
                    self.instance =  qrcodes.first()
                else:
                    try:
                        qrcodes = QRCode.objects.filter(id=int(ref_id))
                    except:
                        if isinstance(ref_id, int):
                            qrcodes = QRCode.objects.filter(id=ref_id)
                        else:
                            qrcodes = QRCode.objects.none()
                    if qrcodes.exists():
                        self.instance =  qrcodes.first()
                    else:
                        qrcodes = QRCode.objects.filter(code=ref_id)
                        if qrcodes.exists():
                            self.instance =  qrcodes.first()
            return self.instance

    class Meta:
        model = QRCode
        fields = ['id']
