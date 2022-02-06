from datetime import datetime

from django.db import models, transaction

from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_instalment import SEFGrantInstalment
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = 'Shuvro'


class SEFGrantDisbursement(OrganizationDomainEntity):
    name = models.CharField(max_length=255, blank=True, null=True)
    pg_member_assigned_code = models.CharField(max_length=255, blank=True, null=True)
    pg_member_name = models.CharField(max_length=255, blank=True, null=True)
    pg_member = models.ForeignKey('nuprp_admin.PrimaryGroupMember', null=True, on_delete=models.SET_NULL)
    account_number = models.CharField(max_length=128, blank=True, null=True)
    cdc = models.ForeignKey('nuprp_admin.CDC', null=True)
    assigned_city = models.CharField(max_length=128, blank=True, null=True)
    instalments = models.ManyToManyField(SEFGrantInstalment)
    grant_disbursement_year = models.IntegerField(default=None, null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedImport, ViewActionEnum.Delete]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit, ViewActionEnum.AdvancedExport]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedImport:
            return "Import"

    @property
    def render_PG_member_ID(self):
        return self.pg_member.assigned_code if self.pg_member and self.pg_member.assigned_code else "N/A"

    @property
    def render_pg_member_name(self):
        return self.pg_member_name if self.pg_member_name else "N/A"

    @property
    def render_linked_PG_member(self):
        return self.pg_member or 'N/A'

    @property
    def render_city_corporation(self):
        if self.pg_member and self.pg_member.assigned_to:
            return self.pg_member.assigned_to.parent.address.geography.parent.name
        else:
            return 'N/A'

    @property
    def render_account_number(self):
        return self.account_number if self.account_number else 'N/A'

    @property
    def render_grant_disbursement_year(self):
        return self.grant_disbursement_year if self.grant_disbursement_year else "N/A"

    # @property
    # def render_CDC(self):
    #     if self.pg_member and self.pg_member.assigned_to and self.pg_member.assigned_to.parent:
    #         return self.pg_member.assigned_to.parent

    @classmethod
    def table_columns(cls):
        return (
            "code", "name:Beneficiary Name", "account_number", "pg_member_assigned_code:PG member ID",
            "pg_member_name:PG member name", "render_linked_PG_member", "cdc:CDC", "assigned_city:City corporation",
            "render_grant_disbursement_year", "date_created:Created On", "last_updated:Last Updated On"
        )

    @classmethod
    def details_view_fields(cls):
        return [
            "code", "name:Beneficiary Name", "account_number", "pg_member_assigned_code:PG member ID",
            "pg_member_name:PG member name", "render_linked_PG_member", "cdc:CDC", "assigned_city:City corporation",
            "render_grant_disbursement_year", "date_created:Created On", "last_updated:Last Updated On"
        ]

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Instalment(s)',
                access_key='instalments',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=SEFGrantInstalment,
                property=self.instalments,
            )]

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        importer_config = ImporterConfig.objects.filter(model=cls.__name__, organization=organization).first()
        if not importer_config:
            importer_config, result = ImporterConfig.objects.get_or_create(
                model=cls.__name__, organization=organization
            )
            importer_config.starting_row = 1
            importer_config.starting_column = 0
            importer_config.save(**kwargs)

        importer_config.columns.clear()

        columns = [
            ImporterColumnConfig(column=0, column_name='PG ID', property_name='pg_member_assigned_code', ignore=False),
            ImporterColumnConfig(column=1, column_name='PG Member Name', property_name='pg_member_name', ignore=False),
            ImporterColumnConfig(column=2, column_name='Beneficiary name', property_name='name', ignore=False),
            ImporterColumnConfig(column=3, column_name='Account Number', ignore=False),
            ImporterColumnConfig(column=4, column_name='Disbursement Date', ignore=False),
            ImporterColumnConfig(column=5, column_name='Grant Disbursement Year', ignore=False),
            ImporterColumnConfig(column=6, column_name='BDT', ignore=False),
            ImporterColumnConfig(column=7, column_name='Status', ignore=False),
            ImporterColumnConfig(column=8, column_name='Relationship of grantee to PG member', ignore=False),
            ImporterColumnConfig(column=9, column_name='Type of Business', ignore=False),
            ImporterColumnConfig(column=10, column_name='Type of trade', ignore=False),
            ImporterColumnConfig(column=11, column_name='Age', ignore=False),
            ImporterColumnConfig(column=12, column_name='Gender', ignore=False),
            ImporterColumnConfig(column=13, column_name='Has disability', ignore=False),
            ImporterColumnConfig(column=14, column_name='Difficulty in seeing', ignore=False),
            ImporterColumnConfig(column=15, column_name='Difficulty in hearing', ignore=False),
            ImporterColumnConfig(column=16, column_name='Difficulty in walking', ignore=False),
            ImporterColumnConfig(column=17, column_name='Difficulty in remembering', ignore=False),
            ImporterColumnConfig(column=18, column_name='Difficulty in self care', ignore=False),
            ImporterColumnConfig(column=19, column_name='Difficulty in communicating', ignore=False),
            ImporterColumnConfig(column=20, column_name='Which class?', ignore=False),
            ImporterColumnConfig(column=21, column_name='Beneficiary Married?', ignore=False),
            ImporterColumnConfig(column=22, column_name='Grantee status', ignore=False),
            ImporterColumnConfig(column=23, column_name='Remarks', ignore=False),
        ]
        print(columns)
        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        importer_config = ImporterConfig.objects.get(pk=importer_config.pk)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        for index, item in enumerate(items):
            pg_member_assigned_code = str(item['0']) if item['0'] else ''
            pg_member_name = str(item['1'])
            name = str(item['2'])
            account_number = str(item['3'])
            disbursement_date = item['4'].strftime("%d/%m/%Y") if type(item['4']) == datetime else item['4']
            grant_disbursement_year = str(item['5'])
            disbursement_value = str(item['6'])
            disbursement_status = str(item['7'])
            relationship_of_grantee = str(item['8'])
            type_of_business = str(item['9'])
            type_of_trade = str(item['10'])
            age = str(item['11'])
            gender = str(item['12'])
            has_disability = str(item['13'])
            difficulty_in_seeing = str(item['14'])
            difficulty_in_hearing = str(item['15'])
            difficulty_in_walking = str(item['16'])
            difficulty_in_remembering = str(item['17'])
            difficulty_in_self_care = str(item['18'])
            difficulty_in_communicating = str(item['19'])
            education_level = str(item['20'])
            marital_status = str(item['21'])
            grantee_status = str(item['22'])
            remarks = str(item['23'])

            if not pg_member_assigned_code:
                continue

            _pgm_queryset = PrimaryGroupMember.objects.filter(assigned_code=pg_member_assigned_code)
            _pgm_queryset = PrimaryGroupMember.objects.filter(
                assigned_code='0' + pg_member_assigned_code) if not _pgm_queryset else _pgm_queryset

            _pgm = _pgm_queryset.last()

            if disbursement_value and isinstance(disbursement_value, int):
                ErrorLog.log(
                    'Import file row {}, amount must be a number'.format(index + 1))
                continue

            try:
                disbursement_date = datetime.strptime(disbursement_date.split()[0],
                                                      '%d/%m/%Y') if disbursement_date else None
            except Exception:
                ErrorLog.log('Import file row {}, Invalid Date'.format(index + 1))
                continue

            try:
                grant_disbursement_year = int(grant_disbursement_year) if grant_disbursement_year else None
            except Exception:
                ErrorLog.log('Import file row {}, Invalid grant disbursement year'.format(index + 1))
                continue

            with transaction.atomic():
                sef_grant_disbursement = cls.objects.filter(pg_member=_pgm).first() if _pgm else \
                    cls.objects.filter(pg_member_assigned_code=pg_member_assigned_code).first()

                if not sef_grant_disbursement:
                    sef_grant_disbursement = cls()
                    sef_grant_disbursement.pg_member = _pgm if _pgm else None
                    sef_grant_disbursement.pg_member_name = _pgm.name if _pgm else pg_member_name
                    sef_grant_disbursement.pg_member_assigned_code = _pgm.assigned_code if _pgm \
                        else pg_member_assigned_code

                sef_grant_disbursement.account_number = account_number
                sef_grant_disbursement.name = name

                _city = sef_grant_disbursement.pg_member.assigned_to.parent.address.geography.parent.name if \
                    sef_grant_disbursement.pg_member else ''
                _cdc = sef_grant_disbursement.pg_member.assigned_to.parent if sef_grant_disbursement.pg_member \
                    else None
                sef_grant_disbursement.assigned_city = _city
                sef_grant_disbursement.cdc = _cdc
                sef_grant_disbursement.grant_disbursement_year = grant_disbursement_year
                sef_grant_disbursement.save()

                _instalment = sef_grant_disbursement.instalments.filter(date=disbursement_date).first()

                _instalment = _instalment if _instalment else SEFGrantInstalment()

                _instalment.value = disbursement_value if disbursement_value else 0
                _instalment.status = disbursement_status if disbursement_status else ''
                _instalment.date = disbursement_date if disbursement_date else None

                if _instalment.pk:
                    _instalment.save()
                else:
                    _last_instalment = sef_grant_disbursement.instalments.last()
                    _instalment.number = int(_last_instalment.number) + 1 if _last_instalment else 1
                    _instalment.save()
                    sef_grant_disbursement.instalments.add(_instalment)

                sef_grant_disbursement.get_or_create_sef_grant(pg_member=_pgm, **{
                    'age': age,
                    'gender': gender,
                    'contact_number': account_number,
                    'has_disability': has_disability,
                    'relationship_of_grantee': relationship_of_grantee,
                    'type_of_business': type_of_business,
                    'type_of_trade': type_of_trade,
                    'difficulty_in_seeing': difficulty_in_seeing,
                    'difficulty_in_hearing': difficulty_in_hearing,
                    'difficulty_in_walking': difficulty_in_walking,
                    'difficulty_in_remembering': difficulty_in_remembering,
                    'difficulty_in_self_care': difficulty_in_self_care,
                    'difficulty_in_communicating': difficulty_in_communicating,
                    'education_level': education_level,
                    'marital_status': marital_status,
                    'grantee_status': grantee_status,
                    'remarks': remarks
                })
