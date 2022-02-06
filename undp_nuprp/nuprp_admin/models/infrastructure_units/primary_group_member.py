import datetime
from collections import OrderedDict

from django.db import transaction
from django.db.models import Q, F, Min, Max

from blackwidow.core.models import ImageFileObject
from blackwidow.core.models.clients.client import Client
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, has_status_data
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.alerts.duplicate_id_alert import DuplcateIdAlert, DuplicateIDAlertEnum

__author__ = "Shama"


@decorate(is_object_context, has_status_data,
          route(route='primary-group-members', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                display_name='Primary Group Member', group_order=3, item_order=20))
class PrimaryGroupMember(Client):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    def soft_delete(self, *args, force_delete=False, user=None, skip_log=False, **kwargs):
        # Delete survey response for soft deleting client
        from undp_nuprp.survey.models.response.survey_response import SurveyResponse
        with transaction.atomic():
            survey_responses = SurveyResponse.objects.filter(respondent_client=self)
            response_ids = list(survey_responses.values_list('id', flat=True))
            times = survey_responses.values('survey_time').aggregate(from_time=Min('survey_time'),
                                                                     to_time=Max('survey_time'))
            for sr in survey_responses:
                sr.soft_delete(*args, force_delete=force_delete, user=user, skip_log=skip_log, client_deleted=True,
                               **kwargs)
            self.pg_member_deletion_manager([self.pk], response_ids, times['from_time'], times['to_time'],
                                            city=self.assigned_to.parent.address.geography.parent.name)
        return super(PrimaryGroupMember, self).soft_delete(
            *args, force_delete=force_delete, user=user, skip_log=skip_log, **kwargs)

    @classmethod
    def pg_member_deletion_manager(cls, _pgm_ids, response_ids, from_time, to_time, city):
        from undp_nuprp.approvals.models import SEFGrantDisbursement, SEFBusinessGrantee, SEFApprenticeshipGrantee, \
            SEFEducationChildMarriageGrantee, SEFNutritionGrantee, EligibleBusinessGrantee, \
            EligibleApprenticeshipGrantee, \
            EligibleEducationEarlyMarriageGrantee, EligibleEducationDropOutGrantee, SEFEducationDropoutGrantee
        from undp_nuprp.nuprp_admin.models import SavingsAndCreditGroup
        from undp_nuprp.reports.models import PGMemberInfoCache
        from undp_nuprp.survey.models import PGPovertyIndex, PGMPIIndicator, MPIIndicator

        # SEF grant disbursement deletion
        SEFGrantDisbursement.objects.filter(pg_member_id__in=_pgm_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        # SEF grantee deletion
        SEFBusinessGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        SEFApprenticeshipGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        SEFEducationChildMarriageGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        SEFEducationDropoutGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        SEFNutritionGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        # Eligible grantee deletion
        EligibleBusinessGrantee.objects.filter(survey_response_id__in=response_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        EligibleApprenticeshipGrantee.objects.filter(survey_response_id__in=response_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        EligibleEducationEarlyMarriageGrantee.objects.filter(survey_response_id__in=response_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        EligibleEducationDropOutGrantee.objects.filter(survey_response_id__in=response_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        # Delete MPI score
        print('Deleting MPIIndicator')
        MPIIndicator.objects.filter(survey_response_id__in=response_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        # Delete PGMPIIndicator
        print('Deleting PGMPIIndicator')
        PGMPIIndicator.objects.filter(survey_response_id__in=response_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        # Delete PG member cache info
        print('Deleting PGMemberInfoCache')
        if from_time and to_time:
            PGMemberInfoCache.objects.filter(from_time__gte=from_time, to_time__lte=to_time,
                                             city__name=city).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

        print('Deleting PGPovertyIndex')
        PGPovertyIndex.objects.filter(primary_group_member_id__in=_pgm_ids).update(
            deleted_level=F('deleted_level') + 1,
            is_deleted=True,
            is_active=False,
            last_updated=int(datetime.datetime.now().timestamp() * 1000)
        )

        print('Deleting SCG member')
        scg = SavingsAndCreditGroup.objects.filter(members__id__in=_pgm_ids).first()
        if scg:
            scg.members.remove(*scg.members.filter(pk__in=_pgm_ids))

    @classmethod
    def get_status_data(cls, request, *args, **kwargs):
        return {
            'pg_member_prefix': None,
            'last_pg_member_id': 0
        }

    def create_alert_for_pg_member(self, object_id, alert_group_id, app_label, model_name):
        self.create_alert_for_duplicate_id(alert_group_id=alert_group_id, model_name=model_name,
                                           app_label=app_label, object_id=object_id)
        self.create_alert_for_duplicate_phone(alert_group_id=alert_group_id, model_name=model_name,
                                              app_label=app_label, object_id=object_id)
        self.create_alert_for_duplicate_nid(alert_group_id=alert_group_id, model_name=model_name,
                                            app_label=app_label, object_id=object_id)

    @property
    def render_primary_group(self):
        try:
            return self.assigned_to
        except:
            return 'N/A'

    @property
    def render_pg_name(self):
        try:
            return self.assigned_to.name
        except:
            return ''

    @property
    def render_cdc(self):
        try:
            return self.assigned_to.parent
        except:
            return 'N/A'

    @property
    def render_cdc_name(self):
        try:
            return self.assigned_to.parent.name
        except:
            return ''

    @property
    def render_cdc_cluster_name(self):
        try:
            return self.assigned_to.parent.parent.name
        except:
            return ''

    @property
    def render_city(self):
        try:
            return self.assigned_to.parent.address.geography.parent.name
        except:
            return 'N/A'

    @property
    def render_city_corporation(self):
        try:
            return self.assigned_to.parent.address.geography.parent.name
        except:
            return 'N/A'

    @property
    def render_survey_response(self):
        if self.surveyresponse_set.first():
            return self.surveyresponse_set.first()
        else:
            return 'N/A'

    @property
    def render_location(self):
        if self.surveyresponse_set.first():
            return self.surveyresponse_set.first().location
        else:
            return 'N/A'

    @property
    def render_status(self):
        if self.status:
            return self.status
        else:
            return 'N/A'

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(assigned_to__parent__address__geography__parent__name__icontains=value)

    @classmethod
    def search_primary_group(cls, queryset, value):
        return queryset.filter(assigned_to__name__icontains=value)

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'name', 'assigned_code:Primary Group Member ID', 'render_primary_group',
            'render_city_corporation', 'render_location', 'date_created:Created On', 'created_by', 'render_status')

    @classmethod
    def sortable_columns(cls):
        return [
            'render_code', 'name', 'assigned_code:Primary Group Member ID', 'render_primary_group',
            'render_city_corporation', 'date_created:Created On', 'created_by'
        ]

    @classmethod
    def prefetch_objects(cls):
        return ["assigned_to", "assigned_to__parent__address__geography__parent"]

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        details['code'] = self.code
        details['name'] = self.name
        details['ID'] = self.assigned_code
        details['primary_group'] = self.render_primary_group
        details['CDC'] = self.render_cdc
        details['City/Town'] = self.render_city
        details['survey_response'] = self.render_survey_response
        details['location'] = self.render_location
        details['created_on'] = self.render_timestamp(self.date_created)
        details['created_by'] = self.created_by
        details['status'] = self.render_status
        details['last_updated_on'] = self.render_timestamp(self.last_updated)
        details['last_updated_by'] = self.last_updated_by
        return details

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Photos(s)',
                access_key='photos',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model=ImageFileObject,
                queryset=ImageFileObject.objects.filter(surveyresponse__respondent_client_id=self.pk).distinct(),
            )
        ]

    def details_link_config(self, **kwargs):
        details_buttons = []
        details_buttons += [
            dict(
                name='Print PG Member Info',
                action='print_pg_member_pritable_info',
                icon='fbx-rightnav-print',
                ajax='0',
                classes='manage-action popup',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Print)
            ),
            dict(
                name='Edit',
                action='edit',
                icon='fbx-rightnav-edit',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit)
            ),
            dict(
                name='Delete',
                action='delete',
                icon='fbx-rightnav-delete',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            )
        ]
        return details_buttons

    @classmethod
    def get_serializer(cls):
        _ClientSerializer = Client.get_serializer()

        class PrimaryGroupMemberSerializer(_ClientSerializer):
            class Meta:
                model = cls
                fields = ('name', 'assigned_to', 'last_updated')

        return PrimaryGroupMemberSerializer

    def create_alert_for_duplicate_id(self, alert_group_id, model_name, app_label, object_id):
        try:
            duplicate_id = PrimaryGroupMember.objects.filter(
                assigned_code=self.assigned_code, pk__lt=self.pk
            ).last()

            is_duplicate_id = duplicate_id is not None

            if is_duplicate_id:
                model_property = DuplicateIDAlertEnum.assigned_code.value  # assigned_code
                record = DuplcateIdAlert.objects.filter(
                    alert_group_id=alert_group_id, model=model_name, app_label=app_label,
                    object_id=object_id, model_property=model_property
                ).order_by('pk').last()

                if record is None:
                    record = DuplcateIdAlert()
                    record.organization_id = self.organization_id
                    record.alert_group_id = alert_group_id
                    record.model = model_name
                    record.app_label = app_label
                    record.object_id = object_id
                    record.model_property = model_property
                    record.created_by_id = self.created_by_id
                    if is_duplicate_id:
                        record.body = 'PG Member' + '\'s ID is ' + \
                                      str(self.assigned_code) + ', which is already the ID of, ' + \
                                      str(duplicate_id)
                        self.is_duplicate_id = True
                        record.save()
                    else:
                        self.is_duplicate_id = False
        except Exception as exp:
            ErrorLog.log(exp)

    def create_alert_for_duplicate_phone(self, alert_group_id, model_name, app_label, object_id):
        try:
            duplicate_phone = None
            duplicate_number = self.phone_number.phone
            if duplicate_number and duplicate_number != '98':
                duplicate_phone = PrimaryGroupMember.objects.filter(
                    phone_number__phone=duplicate_number, pk__lt=self.pk
                ).exclude(pk=self.pk).last()

            is_duplicate_phone = duplicate_phone is not None

            if is_duplicate_phone:
                model_property = DuplicateIDAlertEnum.phone_number.value  # phone_number.phone
                record = DuplcateIdAlert.objects.filter(
                    alert_group_id=alert_group_id, model=model_name, app_label=app_label,
                    object_id=object_id, model_property=model_property
                ).order_by('pk').last()

                if record is None:
                    record = DuplcateIdAlert()
                    record.organization_id = self.organization_id
                    record.alert_group_id = alert_group_id
                    record.model = model_name
                    record.app_label = app_label
                    record.object_id = object_id
                    record.model_property = model_property
                    record.created_by_id = self.created_by_id
                    if is_duplicate_phone:
                        record.body = 'PG Member' + '\'s Phone number is ' + \
                                      str(self.phone_number.phone) + ', which is already the number of, ' + \
                                      str(duplicate_phone)
                        self.is_duplicate_phone = True
                        record.save()
                    else:
                        self.is_duplicate_phone = False
        except Exception as exp:
            ErrorLog.log(exp)

    def create_alert_for_duplicate_nid(self, alert_group_id, model_name, app_label, object_id):
        try:
            duplicate_nid = None
            duplicate_nid_number = self.client_meta.national_id
            if duplicate_nid_number != 'N/A':
                duplicate_nid = PrimaryGroupMember.objects.filter(
                    client_meta__national_id=self.client_meta.national_id, pk__lt=self.pk
                ).exclude(pk=self.pk).last()

            is_duplicate_nid = duplicate_nid is not None

            if is_duplicate_nid:
                model_property = DuplicateIDAlertEnum.national_id.value  # client_meta.national_id
                record = DuplcateIdAlert.objects.filter(
                    alert_group_id=alert_group_id, model=model_name, app_label=app_label,
                    object_id=object_id, model_property=model_property
                ).order_by('pk').last()

                if record is None:
                    record = DuplcateIdAlert()
                    record.organization_id = self.organization_id
                    record.alert_group_id = alert_group_id
                    record.model = model_name
                    record.app_label = app_label
                    record.object_id = object_id
                    record.model_property = model_property
                    record.created_by_id = self.created_by_id
                    if is_duplicate_nid:
                        record.body = 'PG Member' + '\'s NID is ' + \
                                      str(self.client_meta.national_id) + ', which is already the NID of, ' + \
                                      str(duplicate_nid)
                        self.is_duplicate_nid = True
                        record.save()
                    else:
                        self.is_duplicate_nid = False
        except Exception as exp:
            ErrorLog.log(exp)

    def to_json(self, depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs):
        obj = super(PrimaryGroupMember, self).to_json(depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs)
        obj['primary_group'] = self.render_pg_name
        obj['cdc'] = self.render_cdc_name
        obj['cdc_cluster'] = self.render_cdc_cluster_name
        # obj['assigned_code'] = self.assigned_code
        return obj
