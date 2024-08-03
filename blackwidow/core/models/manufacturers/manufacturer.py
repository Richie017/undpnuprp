from django.db import models

from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.users.web_user import WebUser
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Mahmud'


@decorate(is_object_context,
          route(route='manufacturers', group='Products', group_order=10, item_order=1,
                module=ModuleEnum.Administration, display_name="Manufacturer",
                hide=True))
class Manufacturer(OrganizationDomainEntity):
    name = models.CharField(max_length=200)
    contact_persons = models.ManyToManyField(WebUser, name='contact_persons')
    addresses = models.ManyToManyField(ContactAddress, name='addresses')
    emails = models.ManyToManyField(EmailAddress, name='emails')
    phone_numbers = models.ManyToManyField(PhoneNumber, name="phone_numbers")
    is_master = models.BooleanField(default=0)

    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)

    @classmethod
    def table_columns(cls):
        return 'code', 'name', 'render_discount', 'last_updated'

    def render_discount(self):
        return str(self.discount) + ' %'

    @classmethod
    def get_dependent_field_list(cls):
        return ['addresses', 'emails', 'phone_numbers']
