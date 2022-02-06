from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models import UserDevice, ConsoleUser


class UserDeviceForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super(UserDeviceForm, self).__init__(data=data, files=files, instance=instance, **kwargs)

        user_queryset = ConsoleUser.objects.exclude(
                    id__in=UserDevice.objects.values_list('user_id', flat=True)).order_by('name')
        if self.instance and self.instance.pk:
            user_queryset = ConsoleUser.objects.filter(id=UserDevice.objects.get(pk=self.instance.pk).user_id)
        self.fields['user'] = \
            GenericModelChoiceField(
                queryset=user_queryset,
                empty_label='Select One',
                required=True, label='Device User',
                initial=self.instance.user if self.instance else None,
                widget=forms.Select(attrs={'class': 'select2'})
            )

    class Meta(GenericFormMixin.Meta):
        model = UserDevice
        fields = 'user', 'imei_number', 'phone_number'
