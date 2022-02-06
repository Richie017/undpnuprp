from undp_nuprp.nuprp_admin.forms.users.senior_management_form import SeniorManagementForm
from undp_nuprp.nuprp_admin.forms.users.community_organizer_form import CommunityOrganizerForm
from undp_nuprp.nuprp_admin.forms.users.town_manager_form import TownManagerForm
from undp_nuprp.nuprp_admin.forms.users.mne_specialist_form import MNESpecialistForm
from undp_nuprp.nuprp_admin.forms.users.mis_specialist_form import MISSpecialistForm
from undp_nuprp.nuprp_admin.forms.users.federation_member_form import FederationMemberForm
from undp_nuprp.nuprp_admin.forms.users.mne_officer_form import MNEOfficerForm
from undp_nuprp.nuprp_admin.forms.users.town_authority_form import TownAuthorityForm
from undp_nuprp.nuprp_admin.forms.users.fa_expert_form import FAExpertForm
from undp_nuprp.nuprp_admin.forms.users.community_facilitator_form import CommunityFacilitatorForm
from undp_nuprp.nuprp_admin.forms.users.hi_expert_form import HIExpertForm
from undp_nuprp.nuprp_admin.forms.users.monitoring_official_form import MonitoringOfficialForm
from undp_nuprp.nuprp_admin.forms.users.socioeconomic_nutrition_expert_form import SocioeconomicNutritionExpertForm
from undp_nuprp.nuprp_admin.forms.users.guest_form import GuestForm
from undp_nuprp.nuprp_admin.forms.users.nuprp_admin_form import NUPRPAdminForm
from undp_nuprp.nuprp_admin.forms.users.donor_form import DonorForm
from undp_nuprp.nuprp_admin.forms.users.relu_form import RELUForm
from undp_nuprp.nuprp_admin.forms.users.nuprp_expert_form import NUPRPExportForm
from undp_nuprp.nuprp_admin.forms.users.enumerator_form import EnumeratorForm
from undp_nuprp.nuprp_admin.forms.users.mne_coordinator_form import MNECoordinatorForm
from undp_nuprp.nuprp_admin.forms.users.local_government_official_form import LocalGovernmentOfficialForm
from undp_nuprp.nuprp_admin.forms.users.coordinator_form import CoordinatorForm
from undp_nuprp.nuprp_admin.forms.citizen_participation_and_community_mobilization.social_audit_committee_form import SocialAuditCommitteeForm
from undp_nuprp.nuprp_admin.forms.citizen_participation_and_community_mobilization.cdc_assessment_form import CDCAssessmentForm
from undp_nuprp.nuprp_admin.forms.citizen_participation_and_community_mobilization.community_scorecard import CommunityScorecardForm
from undp_nuprp.nuprp_admin.forms.citizen_participation_and_community_mobilization.community_purchase_committee import CommunityPurchaseCommitteeForm
from undp_nuprp.nuprp_admin.forms.citizen_participation_and_community_mobilization.community_action_plan_form import CommunityActionPlanForm
from undp_nuprp.nuprp_admin.forms.citizen_participation_and_community_mobilization.community_mobilization_reporting_form import CommunityMobilizationReportingForm
from undp_nuprp.nuprp_admin.forms.benificieries.grantee_form import GranteeForm
from undp_nuprp.nuprp_admin.forms.urban_governance_and_planning.meeting_form import MeetingAttachmentForm
from undp_nuprp.nuprp_admin.forms.urban_governance_and_planning.meeting_form import MeetingForm
from undp_nuprp.nuprp_admin.forms.urban_governance_and_planning.urban_governance_and_planning_form import UrbanGovernanceAndPlanningForm
from undp_nuprp.nuprp_admin.forms.land_tenure_security.land_tenure_security_form import LandTenureSecurityForm
from undp_nuprp.nuprp_admin.forms.nutrition.nutrition_registration_form import NutritionRegistrationForm
from undp_nuprp.nuprp_admin.forms.nutrition.nutrition_mass_awareness_session_form import NutritionMassAwarenessSessionForm
from undp_nuprp.nuprp_admin.forms.nutrition.nutrition_reporting_form import NutritionReportingForm
from undp_nuprp.nuprp_admin.forms.nutrition.nutrition_conditional_food_transfer_form import NutritionConditionalFoodTransferForm
from undp_nuprp.nuprp_admin.forms.housing_development_fund.land_tenure_action_plan_form import LandTenureActionPlanForm
from undp_nuprp.nuprp_admin.forms.housing_development_fund.installment_payment_form import InstallmentPaymentForm
from undp_nuprp.nuprp_admin.forms.housing_development_fund.housing_development_fund_form import CommunityHousingDevelopmentFundForm
from undp_nuprp.nuprp_admin.forms.housing_development_fund.vacant_land_mapping_form import VacantLandMappingForm
from undp_nuprp.nuprp_admin.forms.operation_and_maintenance.operation_and_maintenance_form import OperationAndMaintenanceFundForm
from undp_nuprp.nuprp_admin.forms.capacity_building.capacity_building_form import CapacityBuildingForm
from undp_nuprp.nuprp_admin.forms.reports.grantee_follow_up.grantee_follow_up_form import GranteeFollowUpForm
from undp_nuprp.nuprp_admin.forms.reports.grantee_follow_up.education_grantee_follow_up_form import EducationGranteeFollowUpForm
from undp_nuprp.nuprp_admin.forms.reports.grantee_follow_up.business_grantee_follow_up_form import BusinessGranteeFollowUpForm
from undp_nuprp.nuprp_admin.forms.reports.grantee_follow_up.apprenticeship_grantee_follow_up_form import ApprenticeshipGranteeFollowUpForm
from undp_nuprp.nuprp_admin.forms.reports.savings_and_credit_report_form import SavingsAndCreditReportForm
from undp_nuprp.nuprp_admin.forms.reports.pending_report_form import PendingReportForm
from undp_nuprp.nuprp_admin.forms.workshop.workshop_form import WorkshopForm
from undp_nuprp.nuprp_admin.forms.infrastructure_units.federation_form import FederationForm
from undp_nuprp.nuprp_admin.forms.infrastructure_units.primary_group_form import PrimaryGroupForm
from undp_nuprp.nuprp_admin.forms.infrastructure_units.household_form import HouseholdForm
from undp_nuprp.nuprp_admin.forms.infrastructure_units.savings_and_credit_group_form import SavingsAndCreditGroupForm
from undp_nuprp.nuprp_admin.forms.infrastructure_units.cdc_form import CDCForm
from undp_nuprp.nuprp_admin.forms.infrastructure_units.cdc_cluster_form import CDCClusterForm
from undp_nuprp.nuprp_admin.forms.delete_test_surveys.delete_test_survey_form import DeleteTestSurveyForm
from undp_nuprp.nuprp_admin.forms.descriptors.trade_sector_form import TradeSectorForm
from undp_nuprp.nuprp_admin.forms.descriptors.training_participant_form import TrainingParticipantForm
from undp_nuprp.nuprp_admin.forms.descriptors.business_sector_form import BusinessSectorForm
from undp_nuprp.nuprp_admin.forms.descriptors.business_type_form import BusinessTypeForm
from undp_nuprp.nuprp_admin.forms.descriptors.trade_type_form import TradeTypeForm
from undp_nuprp.nuprp_admin.forms.clients.primary_group_member_form import PrimaryGroupMemberForm
from undp_nuprp.nuprp_admin.forms.training.training_form import TrainingForm
from undp_nuprp.nuprp_admin.forms.logs.app_release_log_form import AppReleaseLogForm

__author__ = "generated by make_init"

__all__ = ['SeniorManagementForm']
__all__ += ['CommunityOrganizerForm']
__all__ += ['TownManagerForm']
__all__ += ['MNESpecialistForm']
__all__ += ['MISSpecialistForm']
__all__ += ['FederationMemberForm']
__all__ += ['MNEOfficerForm']
__all__ += ['TownAuthorityForm']
__all__ += ['FAExpertForm']
__all__ += ['CommunityFacilitatorForm']
__all__ += ['HIExpertForm']
__all__ += ['MonitoringOfficialForm']
__all__ += ['SocioeconomicNutritionExpertForm']
__all__ += ['GuestForm']
__all__ += ['NUPRPAdminForm']
__all__ += ['DonorForm']
__all__ += ['RELUForm']
__all__ += ['NUPRPExportForm']
__all__ += ['EnumeratorForm']
__all__ += ['MNECoordinatorForm']
__all__ += ['LocalGovernmentOfficialForm']
__all__ += ['CoordinatorForm']
__all__ += ['SocialAuditCommitteeForm']
__all__ += ['CDCAssessmentForm']
__all__ += ['CommunityScorecardForm']
__all__ += ['CommunityPurchaseCommitteeForm']
__all__ += ['CommunityActionPlanForm']
__all__ += ['CommunityMobilizationReportingForm']
__all__ += ['GranteeForm']
__all__ += ['MeetingAttachmentForm']
__all__ += ['MeetingForm']
__all__ += ['UrbanGovernanceAndPlanningForm']
__all__ += ['LandTenureSecurityForm']
__all__ += ['NutritionRegistrationForm']
__all__ += ['NutritionMassAwarenessSessionForm']
__all__ += ['NutritionReportingForm']
__all__ += ['NutritionConditionalFoodTransferForm']
__all__ += ['LandTenureActionPlanForm']
__all__ += ['CommunityHousingDevelopmentFundForm']
__all__ += ['VacantLandMappingForm']
__all__ += ['InstallmentPaymentForm']
__all__ += ['OperationAndMaintenanceFundForm']
__all__ += ['CapacityBuildingForm']
__all__ += ['EducationGranteeFollowUpForm']
__all__ += ['BusinessGranteeFollowUpForm']
__all__ += ['GranteeFollowUpForm']
__all__ += ['ApprenticeshipGranteeFollowUpForm']
__all__ += ['SavingsAndCreditReportForm']
__all__ += ['PendingReportForm']
__all__ += ['WorkshopForm']
__all__ += ['FederationForm']
__all__ += ['PrimaryGroupForm']
__all__ += ['HouseholdForm']
__all__ += ['SavingsAndCreditGroupForm']
__all__ += ['CDCForm']
__all__ += ['CDCClusterForm']
__all__ += ['DeleteTestSurveyForm']
__all__ += ['TradeSectorForm']
__all__ += ['TrainingParticipantForm']
__all__ += ['BusinessSectorForm']
__all__ += ['BusinessTypeForm']
__all__ += ['TradeTypeForm']
__all__ += ['PrimaryGroupMemberForm']
__all__ += ['TrainingForm']
__all__ += ['AppReleaseLogForm']
