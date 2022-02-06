from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from rest_framework import serializers

from blackwidow.core.models.clients.client_meta import ClientMeta
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.custom_field import CustomFieldValue
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.common.qr_code import QRCode
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.file.imagefileobject import ImageFileObject
from blackwidow.core.models.finanical.financial_information import FinancialInformation
from blackwidow.core.models.manufacturers.manufacturer import Manufacturer
from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.core.models.users.web_user import WebUser
from blackwidow.engine.decorators.enable_caching import enable_caching
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, track_assignments, travarse_child_for_status
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Mahmud'


@decorate(track_assignments, enable_caching(), travarse_child_for_status,
          route(route='clients', module=ModuleEnum.Administration, display_name='Client', group='Customers', hide=True))
class Client(OrganizationDomainEntity):
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, null=True)
    manufacturer = models.ForeignKey(Manufacturer, null=True, on_delete=models.SET_NULL)
    address = models.ForeignKey(ContactAddress, null=True, on_delete=models.SET_NULL)
    phone_number = models.ForeignKey(PhoneNumber, null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', null=True, default=None, on_delete=models.SET_NULL)
    group = models.CharField(max_length=255, null=True, default='')
    assigned_to = models.ForeignKey(InfrastructureUnit, null=True, on_delete=models.SET_NULL)
    contact_person = models.ForeignKey(WebUser, null=True, on_delete=models.SET_NULL)
    financial_information = models.ForeignKey(FinancialInformation, null=True, default=None, on_delete=models.SET_NULL)
    remark = models.CharField(max_length=500, default='')
    qr_code = models.ForeignKey(QRCode, null=True, on_delete=models.SET_NULL)
    custom_fields = models.ManyToManyField(CustomFieldValue)
    credit_limit = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    client_meta = models.ForeignKey(ClientMeta, null=True, default=None, verbose_name='Additional Information',
                                    on_delete=models.SET_NULL)
    assigned_code = models.CharField(max_length=256, blank=True)
    last_2_digits_of_assigned_code = models.IntegerField(default=0)
    status = models.CharField(max_length=255, blank=True, default='')

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @classmethod
    def filter_query(cls, query_set, custom_search_fields=[]):
        for param_name, value in custom_search_fields:
            if param_name == "__search_shops_sales_ladies_by_client_id":
                client_ids = [int(_id) for _id in value.split(',') if _id]
                query_set = query_set.filter(assigned_to__parent__parent_client__id__in=client_ids)
            elif param_name == "__search_distributor_cng_by_infrastructure_unit":
                infrastructure_unit_id = value
                query_set = query_set.filter(
                    Q(type__in=['Distributor', 'RVSClient'], assigned_to__id=infrastructure_unit_id))
            elif param_name == "__search_shops_sales_ladies_by_vehicle_user_id":
                vehicle_user_id = value
                query_set = query_set.filter(
                    Q(type__in=['SalesLady', 'UrbanShop', 'RuralShop'],
                      assigned_to__parent__assigned_to__pk=vehicle_user_id))
            elif param_name.startswith("_search_by_route_id"):
                try:
                    query_set = query_set.filter(assigned_to__pk=value)
                except:
                    query_set = cls.objects.none()
            elif param_name.startswith("__search_shops_sales_ladies"):
                try:
                    query_set = query_set.filter(Q(type__in=['SalesLady', 'UrbanShop', 'RuralShop']))
                except:
                    query_set = cls.objects.none()
            elif param_name.startswith("__search_by_user"):
                try:
                    query_set = query_set.filter(Q(type__in=['SalesLady', 'UrbanShop', 'RuralShop']))
                except:
                    query_set = cls.objects.none()
        return query_set

    def to_model_data(self):
        model_data = super(Client, self).to_model_data()
        model_data['name'] = self.name
        model_data['assigned_to'] = self.assigned_to_id if self.assigned_to else None
        return model_data

    @classmethod
    def relations(cls):
        return ['client_product_config']

    def delete(self, *args, **kwargs):
        if self.qr_code:
            self.qr_code.is_used = False
            self.qr_code.save()
        super().delete(*args, **kwargs)

    @classmethod
    def get_trigger_properties(cls, prefix='', expand=['address']):
        return super().get_trigger_properties(prefix=prefix, expand=expand)

    @property
    def details_config(self):
        details_config = super().details_config

        for x in self.custom_fields.all():
            details_config[x.field.name] = x.value

        if self.entity_meta:
            for x in self.entity_meta.custom_field_values.all():
                details_config[x.field.name] = x.value

            for x in self.entity_meta.extra_images.all():
                details_config[x.field.name] = x.value

        return details_config

    @property
    def render_code(self):
        return mark_safe(
            '<a class="inline-link" href="' + reverse(self.true_route_name(ViewActionEnum.Details),
                                                      kwargs={'pk': self.pk}) + '">' + self.code + '</a>')

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)
        self.name = "Client " + str(kwargs['index'])

        self.save()

    @classmethod
    def get_dependent_field_list(cls):
        return ['address', 'financial_information', 'custom_fields']

    def save(self, *args, signal=True, **kwargs):
        if self.qr_code:
            self.qr_code.is_used = True
            self.qr_code.save()
        self.last_2_digits_of_assigned_code = int(self.assigned_code[-2:])
        super().save(*args, **kwargs)

    def get_choice_name(self):
        return self.code + ': ' + self.name

    @property
    def image(self):
        return str(self.client_meta.p_photo.relative_url) if self.client_meta is not None else ''

    @property
    def qr_code_value(self):
        if self.qr_code is None:
            return None
        return str(self.qr_code.value)

    @property
    def date_of_birth(self):
        if self.entity_meta:
            _dob = self.entity_meta.custom_field_values.filter(field__name='Date of Birth').first()
            if _dob and _dob.value:
                return str(_dob.value)
        return ''

    @property
    def image(self):
        if self.entity_meta:
            _photo = self.entity_meta.extra_images.filter(field__name='Entrepreneur Photo').first()
            if _photo is not None:
                return {
                    'id': _photo.id,
                    'tsync_id': _photo.value.tsync_id,
                    'relative_url': _photo.value.relative_url
                } if _photo.value else None
        return None

    @property
    def national_id_image(self):
        if self.entity_meta:
            _photo = self.entity_meta.extra_images.filter(field__name='National ID Photo').first()
            if _photo is not None:
                return {
                    'id': _photo.id,
                    'tsync_id': _photo.value.tsync_id,
                    'relative_url': _photo.value.relative_url
                } if _photo.value else None
        return None

    @property
    def national_id_no(self):
        if self.entity_meta:
            _cf = self.entity_meta.custom_field_values.filter(field__name='National ID').first()
            if _cf is not None:
                return str(_cf.value) if _cf.value is not None else ''
        return ''

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            address = ContactAddress.get_serializer()(required=False)
            phone_number = serializers.SerializerMethodField()
            assigned_to = serializers.SerializerMethodField()
            image = ImageFileObject.get_serializer()
            national_id_image = ImageFileObject.get_serializer()
            national_id_no = serializers.CharField(required=False)
            date_of_birth = serializers.SerializerMethodField(required=False)

            def get_phone_number(self, obj):
                if obj.phone_number:
                    return obj.phone_number.phone
                return ""

            def get_date_of_birth(self, obj):
                if obj.entity_meta:
                    _dob = obj.entity_meta.custom_field_values.filter(field__name='Date of Birth').first()
                    if _dob and _dob.value:
                        return str(_dob.value)
                return ''

            def get_assigned_to(self, obj):
                if obj.assigned_to_id:
                    return obj.assigned_to_id
                return 0

            class Meta(ss.Meta):
                model = cls
                fields = (
                    'id', 'code', 'name', 'tsync_id', 'assigned_to', 'phone_number', 'address', 'date_of_birth',
                    'image', 'national_id_image', 'national_id_no', 'qr_code_value', 'type'
                )

        return Serializer


class ClientCompact(Client):
    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            address = ContactAddress.get_serializer()(required=False)
            phone_number = PhoneNumber.get_serializer()(required=False)
            qr_code = QRCode.get_serializer()(required=False)
            financial_information = FinancialInformation.get_serializer()(required=False)

            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'name', 'code', 'tsync_id', 'phone_number', 'qr_code',
                          'credit_limit', 'financial_information', 'address',
                          'custom_fields', 'type', 'image')

        return Serializer

    class Meta:
        proxy = True
