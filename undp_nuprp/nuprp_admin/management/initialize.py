"""
Created by tareq on 2/15/18
"""
from django.apps import apps

from blackwidow.core.models import CustomField, ConsoleUser
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.geography.geography_level import GeographyLevel
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.core.models.process.approval_level import ApprovalLevel
from blackwidow.core.models.process.approval_process import ApprovalProcess
from blackwidow.core.models.roles.developer import Developer
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.system_admin import SystemAdmin
from blackwidow.engine.enums.field_type_enum import FieldTypesEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.extensions.console_debug import bw_debug
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import SCGMonthlyReport, ApprovedSCGMonthlyReport, CDCMonthlyReport, \
    ApprovedCDCMonthlyReport
from undp_nuprp.nuprp_admin.models.reports.approved_report import ApprovedReport
from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport
from undp_nuprp.nuprp_admin.models.users.enumerator import Enumerator
from undp_nuprp.nuprp_admin.models.users.mne_specialist import MNESpecialist
from undp_nuprp.nuprp_admin.models.users.town_manager import TownManager
from undp_nuprp.survey.models.entity.survey import Survey

get_model = apps.get_model

__author__ = 'Tareq'


def create_approval_levels(*args, **kwargs):
    organization = Organization.get_organization_from_cache()
    survey_approval_process, created = ApprovalProcess.objects.get_or_create(
        model_name=Survey.__name__,
        organization_id=organization.pk)
    if created:
        survey_approval_process.save()
    if survey_approval_process:
        print("Creating Survey approval process ")
        approval_level = survey_approval_process.levels.filter(
            level=1,
            organization_id=organization.pk
        ).first()
        if approval_level is None:
            created = True
            approval_level = ApprovalLevel()
            approval_level.organization_id = organization.pk
            approval_level.level = 1
        approval_level.approve_model = Survey.__name__
        approval_level.reject_model = Survey.__name__
        approval_level.save()
        if created:
            survey_approval_process.levels.add(approval_level)
    else:
        print("Survey approval process exists ... Skipping")


def create_background_user(*args, **kwargs):
    """
    background user created to perform approval action through celery task
    """
    organization = Organization.get_organization_from_cache()
    User = get_model('auth', 'User')

    role, created = Role.objects.get_or_create(name='BackgroundUser', organization=organization)
    print('adding background user...')

    if ConsoleUser.objects.filter(role=role).count() == 0:
        console_user = ConsoleUser()
        if User.objects.filter(username='BackgroundUser').count() == 0:
            auth_user = User()
            auth_user.username = 'BackgroundUser'
            auth_user.save()
            auth_user.set_password('as1234')
            auth_user.save()
            print('auth user added...')
        else:
            auth_user = User.objects.filter(username='BackgroundUser').first()
            print('auth user already exists...skipping')
        console_user.user = auth_user
        console_user.type = 'BackgroundUser'
        console_user.name = 'Background User'
        console_user.role_id = role.pk
        console_user.organization_id = organization.pk
        console_user.save()
        print('background user added...')
    else:
        print('super user already exists...skipping')


def create_background_enumerator(*args, **kwargs):
    enumerator_role = Role.objects.filter(name=Enumerator.__name__).first()
    organization = Organization.get_organization_from_cache()
    enumerator, created = Enumerator.objects.get_or_create(
        name='Background Enumerator',
        role_id=enumerator_role.pk,
        organization_id=organization.pk
    )
    if created:
        bw_debug("Background enumerator created")
    else:
        bw_debug("Background enumerator already exist... skipped")


def create_monthly_scg_report_approvals(*args, **kwargs):
    target_role_classes = [Developer, SystemAdmin, MNESpecialist, TownManager]
    target_role_names = []

    for r in target_role_classes:
        target_role_names.append(r.get_model_meta('route', 'display_name') or r.__name__)

    organization = Organization.get_organization_from_cache()
    target_roles = Role.objects.filter(name__in=target_role_names)

    scg_monthly_report_approval_process, created = ApprovalProcess.objects.get_or_create(
        model_name=SCGMonthlyReport.__name__,
        organization_id=organization.pk
    )
    if created:
        scg_monthly_report_approval_process.save()

    if scg_monthly_report_approval_process:
        print("Creating SCG Monthly Report approval process")
        approval_level = scg_monthly_report_approval_process.levels.filter(
            level=1,
            organization_id=organization.pk
        ).first()
        created = False
        if approval_level is None:
            created = True
            approval_level = ApprovalLevel()
            approval_level.organization_id = organization.pk
            approval_level.level = 1
        approval_level.approve_model = ApprovedSCGMonthlyReport.__name__
        approval_level.save()
        approval_level.roles.add(*target_roles)
        if created:
            scg_monthly_report_approval_process.levels.add(approval_level)
    else:
        print(" SCG Monthly Report approval process exists ... Skipping")


def create_monthly_cdc_report_approvals(*args, **kwargs):
    target_role_names = ['Developer', 'SystemAdmin', 'MNESpecialist', 'TownManager', 'BackgroundUser']
    organization = Organization.get_organization_from_cache()
    target_roles = Role.objects.filter(name__in=target_role_names)

    cdc_monthly_report_approval_process, created = ApprovalProcess.objects.get_or_create(
        model_name=CDCMonthlyReport.__name__,
        organization_id=organization.pk
    )
    if created:
        cdc_monthly_report_approval_process.save()

    if cdc_monthly_report_approval_process:
        print("Creating CDC Monthly Report approval process")
        approval_level = cdc_monthly_report_approval_process.levels.filter(
            level=1,
            organization_id=organization.pk
        ).first()
        created = False
        if approval_level is None:
            created = True
            approval_level = ApprovalLevel()
            approval_level.organization_id = organization.pk
            approval_level.level = 1
        approval_level.approve_model = ApprovedCDCMonthlyReport.__name__
        approval_level.save()
        approval_level.roles.add(*target_roles)
        if created:
            cdc_monthly_report_approval_process.levels.add(approval_level)
    else:
        print(" CDC Monthly Report approval process exists ... Skipping")


def initialize_geography(*args, **kwargs):
    organization = Organization.get_organization_from_cache()
    geography_levels = ['Country', 'Division', 'Pourashava/City Corporation', 'Ward', 'Mahalla', 'Poor Settlement']

    parent = None
    for level in geography_levels:
        bw_debug("Geography: " + level)
        _level, created = GeographyLevel.objects.get_or_create(name=level, parent=parent, organization=organization)
        if created:
            _level.initialize_permission(organization=organization)
        parent = _level
        if created:
            bw_debug("... Created")
        else:
            bw_debug("... Already exist. Skipped")


def initialize_city_code(*args, **kwargs):
    city_codes = [('Dhaka North', '121'), ('Savar', '122'), ('Dhaka South', '123'), ('Narayanganj', '110'),
                  ('Faridpur', '240'), ('Gopalgonj', '060'), ('Kaliakoir', '201'), ('Gazipur', '202'),
                  ('Chittagong', '010'), ('Chandpur', '250'), ('Cox\'s Bazar', '260'), ('Comilla', '140'),
                  ('Feni', '270'),
                  ('Rajshahi', '020'), ('Chapai Nawabgonj', '280'), ('Naogaon', '230'), ('Pabna', '290'),
                  ('Shahjadpur', '082'),
                  ('Satkhira', '300'), ('Magura', '310'), ('Noapara', '150'), ('Rangpur', '160'), ('Syedpur', '320'),
                  ('Kurigram', '330'), ('Dinajpur', '170'), ('Pirojpur', '350'), ('Jhalakathi', '360'),
                  ('Bhola', '370'),
                  ('Jamalpur', '380'), ('Sirajgonj', '081'), ('Khulna', '030'), ('Kushtia', '050'),
                  ('Sylhet', '190'), ('Barisal', '040'), ('Patuakhali', '340'), ('Mymensingh', '090')]

    time_now = Clock.timestamp()
    updateable_entries = list()
    for city in Geography.objects.filter(level__name__iexact='Pourashava/City Corporation'):
        city_code = [code[1] for code in city_codes if code[0] == city.name]

        if city_code and city.short_code != city_code:
            city.short_code = city_code[0]
            city.last_updated = time_now
            time_now += 1
            updateable_entries.append(city)
            print('Updateable city code: %s %s' % (city.name, city_code[0]))
    if len(updateable_entries) > 0:
        Geography.objects.bulk_update(updateable_entries)
        print('Updated %d city codes in total' % (len(updateable_entries)))


def initialize_user_role_custom_fields(*args, **kwargs):
    _designation_field, created = CustomField.objects.get_or_create(
        name='Designation',
        field_type=FieldTypesEnum.Character_Field.value
    )
    _designation_field.role_set.add(*Role.objects.all())
    if created:
        bw_debug("... Created")
    else:
        bw_debug("... Already exist. Skipped")


def initialize(*args, **kwargs):
    actions = [
        initialize_geography,
        initialize_city_code,
        create_background_enumerator,
        create_background_user,
        create_approval_levels,
        create_monthly_scg_report_approvals,
        create_monthly_cdc_report_approvals,
        initialize_user_role_custom_fields
    ]

    i = 1
    for a in actions:
        a(*args, **kwargs)
        i += 1
    print('-------successfully completed-------')
