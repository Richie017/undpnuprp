from collections import OrderedDict

from django.db import models

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.utility import is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.approvals.models import SEFGrantee

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='sef-business-grantee', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                display_name='Business Grantees', group_order=3, item_order=9))
class SEFBusinessGrantee(SEFGrantee):
    business_sector = models.ForeignKey('nuprp_admin.BusinessSector', null=True)
    type_of_business = models.ForeignKey('nuprp_admin.BusinessType', null=True, related_name='+')

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return (
            "code", "name:Beneficiary Name", "render_contact_number", "render_PG_member_ID", "render_CDC",
            "render_city_corporation", "ward", "relation_with_pg_member:Relationship of grantee to PG member",
            "business_sector:Type of Business", "render_grant_disbursement_year",
            "date_created:Created On", "last_updated:Last Updated On"
        )

    @property
    def details_config(self):
        details = OrderedDict()

        # basic information
        basic_info = OrderedDict()
        basic_info['name'] = self.name
        basic_info['contact_number'] = self.render_contact_number
        basic_info['age'] = self.age
        basic_info['gender'] = self.gender
        basic_info['pg_member_id'] = self.render_PG_member_ID
        basic_info['CDC'] = self.render_CDC
        basic_info['city_corporation'] = self.render_city_corporation
        basic_info['ward'] = self.ward
        basic_info['grantee_status'] = self.grantee_status
        basic_info['Relationship of grantee to PG member'] = self.relation_with_pg_member
        basic_info['type_of_business'] = self.business_sector
        basic_info['grant_disbursement_year'] = self.render_grant_disbursement_year
        basic_info['remarks'] = self.remarks

        # disability status information
        disability_status_info = OrderedDict()
        disability_status_info['Has disability'] = self.has_disability
        disability_status_info['Difficulty seeing, even if wearing glasses'] = self.difficulty_in_seeing
        disability_status_info['Difficulty hearing, even if using a hearing aid'] = self.difficulty_in_hearing
        disability_status_info['Difficulty walking or climbing steps'] = self.difficulty_in_walking
        disability_status_info['Difficulty remembering or concentrating'] = self.difficulty_in_remembering
        disability_status_info['Difficulty with self-care such as washing all over or dressing'] = \
            self.difficulty_in_self_care
        disability_status_info['Difficulty communicating, for example understanding or being understood'] = \
            self.difficulty_in_communicating

        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by
        audit_info['created_on'] = self.render_timestamp(self.date_created)

        details["Grantee's Basic Information"] = basic_info
        details["Grantee's Disability Status"] = disability_status_info
        details["Audit Information"] = audit_info
        return details

    @classmethod
    def export_file_columns(cls):
        """
        this method is used to get the list of columns to be exported
        :return: a list of column properties
        """
        _table_columns = [
            "code", "name:Beneficiary Name", "render_contact_number", "render_PG_member_ID",
            "render_CDC_name", "render_CDC_ID", "render_city_corporation", "ward",
            "relation_with_pg_member:Relationship of grantee to PG member",
            "business_sector:Type of Business", "render_grant_disbursement_year",
            "date_created:Created On", "last_updated:Last Updated On"
        ]

        return _table_columns + list(cls.details_view_fields())

    @classmethod
    def details_view_fields(cls):
        """
        this method is used to get the list of fields used in the details view
        :return: list of strings (names of fields in details view)
        """
        return [
            'age', 'gender', 'grantee_status', 'remarks', 'difficulty_in_seeing', 'difficulty_in_hearing',
            'difficulty_in_walking', 'difficulty_in_remembering', 'difficulty_in_self_care',
            'difficulty_in_communicating', 'render_total_installment', 'has_disability'
        ]
