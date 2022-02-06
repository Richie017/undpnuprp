from blackwidow.core.forms.files.imagefileobject_form import ImageFileObjectForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models import CustomFieldValue
from blackwidow.core.models.common.custom_field import CustomField, CustomImageFieldValue
from blackwidow.core.models.common.domain_entity_meta import DomainEntityMeta
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.generate_form_fields import genarate_form_field

__author__ = 'Tareq'


class DomainEntityMetaForm(GenericFormMixin):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, instance=None, parent_model=None, **kwargs):
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, instance=instance, **kwargs)

        if self.instance is not None and self.instance.pk is not None:
            custom_field_values = self.instance.custom_field_values.all()
            extra_images = self.instance.extra_images.all()
        else:
            custom_field_values = CustomFieldValue.objects.none()
            extra_images = CustomImageFieldValue.objects.none()
        if parent_model:
            self.parent_model = parent_model
        model_custom_fields = CustomField.objects.filter(
            model_name__in=self.parent_model.get_parent_class_names()).order_by('name')
        if len(model_custom_fields) > 0:
            kwargs.update({
                'prefix': 'meta'
            })
            custom_field_form = self
            _index = 0
            for x in model_custom_fields:
                if x.field_type == 'image':
                    initial_image = None
                    if x.name in [f.field.name for f in extra_images]:
                        initial_image = [f.value for f in extra_images if f.field.name == x.name][0]
                    kwargs.update({"form_header": bw_titleize(x.name), "prefix": 'field_' + str(_index)})
                    custom_field_form.add_child_form('field_' + str(_index),
                                                     ImageFileObjectForm(data=data, files=files, instance=initial_image,
                                                                         **kwargs))
                elif x.field_type == 'file':
                    pass
                else:
                    field_instance_args = {
                        'label': bw_titleize(x.name),
                        'required': x.is_required,
                    }
                    custom_field_form.fields['field_' + str(_index)] = genarate_form_field(x, field_instance_args)
                    if x.name not in [f.field.name for f in custom_field_values]:
                        custom_field_form.fields['field_' + str(_index)].initial = ""
                    else:
                        custom_field_form.fields['field_' + str(_index)].initial = \
                            [f.value for f in custom_field_values if f.field.name == x.name][0]
                _index += 1

    class Meta(GenericFormMixin.Meta):
        model = DomainEntityMeta

    def save(self, commit=True):
        super().save(commit)
        self.instance.custom_field_values.clear()
        self.instance.extra_images.clear()
        model_custom_fields = CustomField.objects.filter(
            model_name__in=self.parent_model.get_parent_class_names()).order_by('name')
        if len(model_custom_fields) > 0:
            custom_field_form = self
            index = 0
            for x in model_custom_fields:
                if x.field_type == 'image':
                    image_form = [tup[1] for tup in self.child_forms if tup[0] == 'field_' + str(index)][0]
                    if image_form.is_valid():
                        image = image_form.save()
                        f_value = CustomImageFieldValue(value=image, field=x)
                        f_value.save()
                        self.instance.extra_images.add(f_value)
                elif x.field_type == 'file':
                    pass
                else:
                    if ('field_' + str(index)) in custom_field_form.fields:
                        value = custom_field_form.cleaned_data['field_' + str(index)]
                    else:
                        value = ""
                    f_value = CustomFieldValue()
                    f_value.value = value
                    f_value.field = x
                    f_value.save()
                    self.instance.custom_field_values.add(f_value)
                index += 1
        return self.instance
