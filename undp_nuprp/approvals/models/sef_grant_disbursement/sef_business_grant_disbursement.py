from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import is_object_context, decorate
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_disbursement import SEFGrantDisbursement
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_business_grantee import SEFBusinessGrantee
from undp_nuprp.nuprp_admin.models.descriptors.business_sector import BusinessSector

__author__ = 'Md Shaheen Alam'


@decorate(is_object_context, enable_import, route(
    route='sef-business-grant-disbursement', module=ModuleEnum.Analysis,
    group='Local Economy Livelihood and Financial Inclusion', group_order=3,
    item_order=14, display_name='Business Grant Disbursement'
))
class SEFBusinessGrantDisbursement(SEFGrantDisbursement):
    class Meta:
        app_label = 'approvals'
        proxy = True

    def get_or_create_sef_grant(self, pg_member, **kwargs):
        sef_grant = SEFBusinessGrantee.objects.filter(
            pg_member_name=self.pg_member_name,
            pg_member_assigned_code=self.pg_member_assigned_code
        ).last()

        if not sef_grant:
            _ward = self.pg_member_assigned_code[3:5] if self.pg_member_assigned_code and len(self.pg_member_assigned_code) > 4 else ""
            if len(_ward) == 1:
                _ward = "0" + str(_ward)
            sef_grant = SEFBusinessGrantee.objects.create(
                pg_member_name=self.pg_member_name,
                pg_member_assigned_code=self.pg_member_assigned_code,
                pg_member=pg_member,
                ward=_ward
            )
            sef_grant.sef_grant_disbursement = self

        age = kwargs.get('age', None)
        gender = kwargs.get('gender', '')
        has_disability = kwargs.get('has_disability', '')
        has_disability_family = kwargs.get('has_disability_family', '')
        contact_number = kwargs.get('contact_number', '')
        type_of_business = kwargs.get('type_of_business', '').strip()
        # difficulty_in_seeing = kwargs.get('difficulty_in_seeing', '')
        # difficulty_in_hearing = kwargs.get('difficulty_in_hearing', '')
        # difficulty_in_walking = kwargs.get('difficulty_in_walking', '')
        # difficulty_in_remembering = kwargs.get('difficulty_in_remembering', '')
        # difficulty_in_self_care = kwargs.get('difficulty_in_self_care', '')
        # difficulty_in_communicating = kwargs.get('difficulty_in_communicating', '')
        relationship_of_grantee = kwargs.get('relationship_of_grantee', '')
        grantee_status = kwargs.get('grantee_status', '')
        remarks = kwargs.get('remarks', '')

        sef_grant.name = self.name
        sef_grant.age = age
        sef_grant.gender = gender
        sef_grant.contact_number = contact_number
        sef_grant.has_disability = has_disability
        sef_grant.has_disability_family = has_disability_family
        # sef_grant.difficulty_in_seeing = difficulty_in_seeing
        # sef_grant.difficulty_in_hearing = difficulty_in_hearing
        # sef_grant.difficulty_in_walking = difficulty_in_walking
        # sef_grant.difficulty_in_remembering = difficulty_in_remembering
        # sef_grant.difficulty_in_self_care = difficulty_in_self_care
        # sef_grant.difficulty_in_communicating = difficulty_in_communicating
        sef_grant.relationship_of_grantee = relationship_of_grantee
        sef_grant.grantee_status = grantee_status
        sef_grant.remarks = remarks

        if type_of_business:
            bt = BusinessSector.objects.filter(name__iexact=type_of_business).first()
            if not bt:
                bt = BusinessSector(name=type_of_business)
                bt.save()
            sef_grant.business_sector = bt
        sef_grant.save()

    def soft_delete(self, *args, force_delete=False, user=None, skip_log=False, **kwargs):
        try:
            referred_grantee = self.sefbusinessgrantee
            if referred_grantee:
                referred_grantee.sef_grant_disbursement = None
                referred_grantee.save()

                referred_grantee.soft_delete(*args, force_delete=True, user=user, skip_log=skip_log, **kwargs)
        except:
            pass
        super().soft_delete(*args, force_delete, user, skip_log, **kwargs)
