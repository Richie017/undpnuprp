from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import is_object_context, decorate
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_disbursement import SEFGrantDisbursement
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_nutrition_grantee import SEFNutritionGrantee

__author__ = 'Shuvro'


@decorate(is_object_context, enable_import, route(
    route='sef-nutrition-grant-disbursement', module=ModuleEnum.Analysis,
    group='Local Economy Livelihood and Financial Inclusion',
    group_order=3, item_order=18, display_name='Nutrition Grant Disbursement'
))
class SEFNutritionGrantDisbursement(SEFGrantDisbursement):
    class Meta:
        app_label = 'approvals'
        proxy = True

    @classmethod
    def table_columns(cls):
        return (
            "code", "name:Beneficiary Name", "account_number", "pg_member_assigned_code:PG member ID",
            "pg_member_name:PG member name", "render_linked_PG_member", "cdc:CDC", "assigned_city:City corporation",
            "date_created:Created On", "last_updated:Last Updated On"
        )

    @classmethod
    def details_view_fields(cls):
        return [
            "code", "name:Beneficiary Name", "account_number", "pg_member_assigned_code:PG member ID",
            "pg_member_name:PG member name", "render_linked_PG_member", "cdc:CDC", "assigned_city:City corporation",
            "date_created:Created On", "last_updated:Last Updated On"
        ]

    def get_or_create_sef_grant(self, pg_member, **kwargs):
        sef_grant = SEFNutritionGrantee.objects.filter(
            pg_member_name=self.pg_member_name,
            pg_member_assigned_code=self.pg_member_assigned_code
        ).last()

        if not sef_grant:
            _ward = self.pg_member_assigned_code[3:5] if self.pg_member_assigned_code and len(
                self.pg_member_assigned_code) > 4 else ""
            if len(_ward) == 1:
                _ward = "0" + str(_ward)
            sef_grant = SEFNutritionGrantee.objects.create(
                pg_member_name=self.pg_member_name,
                pg_member_assigned_code=self.pg_member_assigned_code,
                pg_member=pg_member,
                ward=_ward
            )
            sef_grant.sef_grant_disbursement = self

        sef_grant.name = self.name
        age = kwargs.get('age', None)
        gender = kwargs.get('gender', '')
        has_disability = kwargs.get('has_disability', '')
        if age:
            sef_grant.age = age
        if gender:
            sef_grant.gender = gender
        if has_disability:
            sef_grant.has_disability = has_disability
        sef_grant.save()

    def soft_delete(self, *args, force_delete=False, user=None, skip_log=False, **kwargs):
        try:
            referred_grantee = self.sefnutritiongrantee
            if referred_grantee:
                referred_grantee.sef_grant_disbursement = None
                referred_grantee.save()

                referred_grantee.soft_delete(*args, force_delete=True, user=user, skip_log=skip_log, **kwargs)
        except:
            pass
        super().soft_delete(*args, force_delete, user, skip_log, **kwargs)
