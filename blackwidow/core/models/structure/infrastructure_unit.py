from collections import OrderedDict

from django.apps import apps
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.utils.safestring import mark_safe

from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.custom_field import CustomFieldValue
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import get_models_with_decorator, decorate, track_assignments
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from config.apps import INSTALLED_APPS
from config.email_config import DEFAULT_FROM_EMAIL

get_model = apps.get_model

__author__ = 'Mahmud'


@decorate(route(route='infrastructure-unit', group='Organizations/Hierarchy',
                module=ModuleEnum.Administration, display_name="InfrastructureUnit", hide=True), track_assignments)
class InfrastructureUnit(OrganizationDomainEntity):
    name = models.CharField(max_length=200)

    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    address = models.ForeignKey(ContactAddress, null=True, on_delete=models.SET_NULL)

    custom_fields = models.ManyToManyField(CustomFieldValue)
    assigned_to = models.ForeignKey('core.ConsoleUser', null=True, on_delete=models.SET_NULL)
    parent_client = models.ForeignKey('core.Client', null=True, on_delete=models.SET_NULL)
    assigned_code = models.CharField(max_length=256, blank=True)
    date_of_formation = models.DateTimeField(default=None, null=True)
    remarks = models.TextField(blank=True)

    @classmethod
    def intermediate_models(cls):
        return tuple('', )

    @property
    def parent_infrastructure_unit(self):
        return self.parent

    @property
    def render_code(self):
        return mark_safe(
            "<a class='inline-link' href='" + reverse(self.true_route_name(ViewActionEnum.Details),
                                                      kwargs={'pk': self.pk}) + "' >" + self.code + "</a>")

    @property
    def render_area(self):
        return self.parent_client.assigned_to

    @property
    def render_service_day(self):
        return self.service_days.all().first() if self.service_days.exists() else ""

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def other_information(self):
        details = OrderedDict()
        details['last_updated'] = self.render_timestamp(self.last_updated)
        details['last_updated_by'] = self.last_updated_by
        details['created_at'] = self.render_timestamp(self.date_created)
        details['created_by'] = self.created_by
        return details

    @classmethod
    def get_dependent_field_list(cls):
        return ['address', 'assigned_clients', 'assigned_organization']

    def get_associated_alerts(self, alert_types=None, last_run_time=Clock.utcnow(), include_child=False, **kwargs):
        alerts = []
        alert_types = alert_types if alert_types is not None else get_models_with_decorator('triggers_alert',
                                                                                            INSTALLED_APPS,
                                                                                            include_class=True)
        for alert_type in alert_types:
            alerts += list(
                alert_type.objects.filter(date_created__gte=last_run_time.timestamp() * 1000, counter_part=self))
            if include_child:
                for child in InfrastructureUnit.objects.filter(parent=self):
                    alerts += child.get_associated_alerts(alert_types=alert_types, last_run_time=last_run_time,
                                                          include_child=include_child)
        return alerts

    def build_alert_message(self, alerts=None, **kwargs):
        message = ""
        d_name = self.__class__.get_model_meta('route', 'display_name')
        d_name = self.__class__.__name__ if d_name is None else d_name

        if len(alerts) > 0:
            message += "<h3>for " + d_name + ": " + \
                       self.name + \
                       "</h3>" \
                       "<hr style='border: none; border-bottom:solid 1px #ccc;'/><ul><li>"
            message += "</li><li>".join([str(x) for x in alerts])
            message += "</li></ul>"

        return message

    def send_mail_to_manager(self, template, message, **kwargs):
        from blackwidow.core.models.users.user import ConsoleUser

        managers = ConsoleUser.objects.filter(assigned_to=self)
        for user in managers:
            email_body = 'The daily alert digest from Jita is here for you -' + message + '</ul>.'
            html_msg = template.content_structure \
                .replace('[@recipient_users]', user.name) \
                .replace('[@body]', email_body) \
                .replace('[@sender]', 'System') \
                .replace('[@role]', 'Team Jita')

            emails = []
            for email in user.emails.all():
                emails.append(email.email)

            send_mail(
                "Daily Jita Alert Digest",
                email_body,
                DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False,
                html_message=html_msg)

    def to_model_data(self):
        model_data = super(InfrastructureUnit, self).to_model_data()
        model_data['id'] = self.pk
        model_data['name'] = self.name
        model_data['parent'] = self.parent_id if self.parent is not None else None
        model_data['assigned_to'] = self.assigned_to_id if self.assigned_to is not None else None
        model_data['parent_client'] = self.parent_client_id if self.parent_client is not None else None
        return model_data

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()
        cassign = get_model('core', 'ClientAssignment')

        class Serializer(ss):
            assigned_organization = Organization.get_serializer()(required=False)
            address = ContactAddress.get_serializer()(required=False)
            assigned_clients = cassign.get_serializer()(required=False, many=True)
            custom_fields = CustomFieldValue.get_serializer()(many=True, required=False)

            def create(self, validated_data):
                from blackwidow.core.models.clients.client_assignment import ClientAssignment

                with transaction.atomic():
                    assigned_clients = validated_data.pop('assigned_clients', [])
                    instance = super().create(validated_data)
                    client_dict = dict()

                    for x in instance.assigned_clients.all():
                        for y in x.clients.all():
                            instance.remove_child_item(**{'ids': str(y.pk), 'tab': x.client_type.lower()})
                        x.clients.clear()
                        instance.assigned_clients.remove(x)
                        x.delete()

                    for j in assigned_clients:
                        for x in instance.assigned_clients.all():
                            if x.client_type == j['client_type']:
                                client_dict[x.client_type] = True
                                x.clients.clear()
                                for y in j['clients']:
                                    x.clients.add(y)
                        if j['client_type'] not in client_dict:
                            nx = ClientAssignment()
                            nx.client_type = j['client_type']
                            nx.save()
                            # for y in j['clients']:
                            # nx.clients.add(y)
                            instance.assigned_clients.add(nx)
                            for y in j['clients']:
                                instance.add_child_item(**{'ids': str(y.pk), 'tab': j['client_type'].lower()})
                    return instance

            def update(self, instance, validated_data):
                from blackwidow.core.models.clients.client_assignment import ClientAssignment

                with transaction.atomic():
                    assigned_clients = validated_data.pop('assigned_clients', [])
                    instance = super().update(instance, validated_data)
                    client_dict = dict()

                    for x in instance.assigned_clients.all():
                        for y in x.clients.all():
                            instance.remove_child_item(**{'ids': str(y.pk), 'tab': x.client_type.lower()})
                        x.clients.clear()
                        instance.assigned_clients.remove(x)
                        x.delete()

                    for j in assigned_clients:
                        for x in instance.assigned_clients.all():
                            if x.client_type == j['client_type']:
                                client_dict[x.client_type] = True
                                x.clients.clear()
                                for y in j['clients']:
                                    x.clients.add(y)
                        if j['client_type'] not in client_dict:
                            nx = ClientAssignment()
                            nx.client_type = j['client_type']
                            nx.save()
                            # for y in j['clients']:
                            # nx.clients.add(y)
                            instance.assigned_clients.add(nx)
                            for y in j['clients']:
                                instance.add_child_item(**{'ids': str(y.pk), 'tab': j['client_type'].lower()})
                    return instance

            class Meta(ss.Meta):
                model = cls
                fields = (
                    'id', 'code', 'name', 'assigned_organization',
                    'parent', 'address', 'custom_fields', 'assigned_to',
                    'parent_client', 'assigned_clients', 'service_days'
                )

        return Serializer

    @classmethod
    def filter_query(cls, query_set, custom_search_fields=[]):
        for param_name, value in custom_search_fields:
            if param_name == "__search_cp_vp_rvs_by_client":
                client_id = value
                query_set = query_set.filter(
                    Q(type__in=['CarUnit', 'RickshawUnit', 'VanUnit'], parent_client__id=client_id))

            elif param_name == "_search_vehicle_unit_by_user_type":
                user_type = value
                if user_type == 'CarPuller':
                    query_set = query_set.filter(type='CarUnit')
                elif user_type == 'VanPuller':
                    query_set = query_set.filter(type='VanUnit')
        return query_set
