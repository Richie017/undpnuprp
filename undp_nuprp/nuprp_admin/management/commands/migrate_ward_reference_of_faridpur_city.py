import csv
import os

from django.core.management import BaseCommand

from blackwidow.core.models import Geography, ContactAddress
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from settings import STATIC_ROOT
from undp_nuprp.approvals.models import SEFBusinessGrantee, SEFEducationChildMarriageGrantee, \
    SEFEducationDropoutGrantee, SEFApprenticeshipGrantee, SEFNutritionGrantee, SEFGrantDisbursement, SEFTracker
from undp_nuprp.nuprp_admin.models import CDC, PrimaryGroupMember, CommunityHousingDevelopmentFund

__author__ = 'Ziaul Haque'

write_db = BWDatabaseRouter.get_write_database_name()
city_name = 'Faridpur'
filepath = os.path.join(STATIC_ROOT, 'data', 'FaridpurCityWardReference_v2.csv')


class Command(BaseCommand):

    @classmethod
    def load_data_from_csv(cls, csv_path):
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            data = []
            for row in csv_reader:
                data.append(row)
            return data

    def handle(self, *args, **options):
        actions = [
            self.migrate_cdc_ward_reference,
            self.migrate_pg_member_ward_reference,
            self.migrate_sef_grantee_ward_reference,
            self.migrate_sef_grant_disbursement_ward_reference,
            self.migrate_sef_tracker_ward_reference,
            self.migrate_housing_development_fund_pg_member_reference,
            # self.migrate_pg_member_reference_of_eligible_grantee_exported_file,
        ]
        _index = 1
        _max = len(actions)
        for a in actions:
            self.stdout.write("step: " + str(_index) + "/" + str(_max))
            a(*args, **options)
            self.stdout.write('\n')
            _index += 1

    @classmethod
    def migrate_cdc_ward_reference(cls, *args, **kwargs):
        cdc_list = []
        for row in cls.load_data_from_csv(filepath)[1:]:
            old_ward = row[4]
            new_ward = row[5]
            cdc_name = row[6]
            cdc_list.append((old_ward, new_ward, cdc_name))

        updatable_addresses = []
        for old_ward, new_ward, cdc_name in set(cdc_list):
            cdc_instance = CDC.objects.using(write_db).get(
                address__geography__parent__name=city_name,
                name=cdc_name
            )
            ward_instance = Geography.objects.using(write_db).get(
                level__name="Ward", parent__name=city_name,
                name=new_ward
            )
            address_instance = cdc_instance.address
            if address_instance:
                address_instance.geography = ward_instance
                updatable_addresses.append(address_instance)

            cdc_old_id = cdc_instance.assigned_code
            cdc_new_id = ""
            for index, value in enumerate(list(cdc_old_id)):
                if index == 3:
                    value = new_ward[0]
                elif index == 4:
                    value = new_ward[1]
                cdc_new_id += value

            cdc_instance.assigned_code = cdc_new_id
            cdc_instance.save()
            print("CDC: {}, Old Ward: {}, New Ward: {}, Old ID: {}, New ID: {}".format(
                cdc_name, old_ward, new_ward, cdc_old_id, cdc_new_id))

        if len(updatable_addresses) > 0:
            print("Updating {} ContactAddress items".format(len(updatable_addresses)))
            ContactAddress.objects.bulk_update(objs=updatable_addresses, using=write_db)
            print("Updated...")

    @classmethod
    def migrate_pg_member_ward_reference(cls, *args, **kwargs):
        updatable_pg_members = []
        for row in cls.load_data_from_csv(filepath)[1:]:
            pg_member_old_id = row[8]
            pg_member_pk = row[11]
            pg_member_new_id = row[12]

            try:
                pg_member_instance = PrimaryGroupMember.objects.using(write_db).get(pk=pg_member_pk)
                pg_member_instance.assigned_code = pg_member_new_id
                updatable_pg_members.append(pg_member_instance)
                print(pg_member_pk)
            except:
                print("PG Member Old ID: {} Not Found".format(pg_member_old_id))

            if len(updatable_pg_members) == 500:
                print("Updating 500 PrimaryGroupMember items.")
                PrimaryGroupMember.objects.bulk_update(objs=updatable_pg_members, using=write_db)
                print("Updated...")
                updatable_pg_members = []

        if len(updatable_pg_members) > 0:
            print("Updating {} PrimaryGroupMember items".format(len(updatable_pg_members)))
            PrimaryGroupMember.objects.bulk_update(objs=updatable_pg_members, using=write_db)
            print("Updated...")

    @classmethod
    def migrate_sef_grantee_ward_reference(cls, *args, **kwargs):
        updatable_sef_business_grantees = []
        updatable_sef_child_marriage_grantees = []
        updatable_sef_education_dropout_grantees = []
        updatable_sef_apprenticeship_grantees = []
        updatable_sef_nutrition_grantees = []
        for row in cls.load_data_from_csv(filepath)[1:]:
            pg_member_old_id = row[8]
            pg_member_pk = row[11]
            pg_member_new_id = row[12]

            print("PG Member Old ID: {}, PG Member PK: {}, PG Member New ID: {}".format(
                pg_member_old_id, pg_member_pk, pg_member_new_id))

            # sef business grantee
            sef_business_grantee_queryset = SEFBusinessGrantee.objects.using(write_db).filter(
                pg_member_id=pg_member_pk
            ) | SEFBusinessGrantee.objects.using(write_db).filter(
                pg_member_assigned_code=pg_member_old_id
            )

            for sef_business_grantee_instance in sef_business_grantee_queryset:
                sef_business_grantee_instance.pg_member_assigned_code = pg_member_new_id
                updatable_sef_business_grantees.append(sef_business_grantee_instance)

                if len(updatable_sef_business_grantees) == 500:
                    print("Updating 500 SEFBusinessGrantee items")
                    SEFBusinessGrantee.objects.bulk_update(objs=updatable_sef_business_grantees, using=write_db)
                    print("Updated...")
                    updatable_sef_business_grantees = []

            # sef child marriage grantee
            sef_child_marriage_queryset = SEFEducationChildMarriageGrantee.objects.using(write_db).filter(
                pg_member_id=pg_member_pk
            ) | SEFEducationChildMarriageGrantee.objects.using(write_db).filter(
                pg_member_assigned_code=pg_member_old_id
            )

            for sef_child_marriage_instance in sef_child_marriage_queryset:
                sef_child_marriage_instance.pg_member_assigned_code = pg_member_new_id
                updatable_sef_child_marriage_grantees.append(sef_child_marriage_instance)

                if len(updatable_sef_child_marriage_grantees) == 500:
                    print("Updating 500 SEFEducationChildMarriageGrantee items")
                    SEFEducationChildMarriageGrantee.objects.bulk_update(
                        objs=updatable_sef_child_marriage_grantees, using=write_db)
                    print("Updated...")
                    updatable_sef_child_marriage_grantees = []

            # sef education dropout grantee
            sef_education_dropout_queryset = SEFEducationDropoutGrantee.objects.using(write_db).filter(
                pg_member_id=pg_member_pk
            ) | SEFEducationDropoutGrantee.objects.using(write_db).filter(
                pg_member_assigned_code=pg_member_old_id
            )

            for sef_education_dropout_instance in sef_education_dropout_queryset:
                sef_education_dropout_instance.pg_member_assigned_code = pg_member_new_id
                updatable_sef_education_dropout_grantees.append(sef_education_dropout_instance)

                if len(updatable_sef_education_dropout_grantees) == 500:
                    print("Updating 500 SEFEducationDropoutGrantee items")
                    SEFEducationDropoutGrantee.objects.bulk_update(
                        objs=updatable_sef_education_dropout_grantees, using=write_db)
                    print("Updated...")
                    updatable_sef_education_dropout_grantees = []

            # sef apprenticeship grantee
            sef_apprenticeship_queryset = SEFApprenticeshipGrantee.objects.using(write_db).filter(
                pg_member_id=pg_member_pk
            ) | SEFApprenticeshipGrantee.objects.using(write_db).filter(
                pg_member_assigned_code=pg_member_old_id
            )

            for sef_apprenticeship_instance in sef_apprenticeship_queryset:
                sef_apprenticeship_instance.pg_member_assigned_code = pg_member_new_id
                updatable_sef_apprenticeship_grantees.append(sef_apprenticeship_instance)
                if len(updatable_sef_apprenticeship_grantees) == 500:
                    print("Updating 500 SEFApprenticeshipGrantee items")
                    SEFApprenticeshipGrantee.objects.bulk_update(
                        objs=updatable_sef_apprenticeship_grantees, using=write_db)
                    print("Updated...")
                    updatable_sef_apprenticeship_grantees = []

            # sef nutrition grantee
            sef_nutrition_queryset = SEFNutritionGrantee.objects.using(write_db).filter(
                pg_member_id=pg_member_pk
            ) | SEFNutritionGrantee.objects.using(write_db).filter(
                pg_member_assigned_code=pg_member_old_id
            )

            for sef_nutrition_instance in sef_nutrition_queryset:
                sef_nutrition_instance.pg_member_assigned_code = pg_member_new_id
                updatable_sef_nutrition_grantees.append(sef_nutrition_instance)
                if len(updatable_sef_nutrition_grantees) == 500:
                    print("Updating 500 SEFNutritionGrantee items")
                    SEFNutritionGrantee.objects.bulk_update(objs=updatable_sef_nutrition_grantees, using=write_db)
                    print("Updated...")
                    updatable_sef_nutrition_grantees = []

        sef_business_grantee_count = len(updatable_sef_business_grantees)
        sef_child_marriage_grantee_count = len(updatable_sef_child_marriage_grantees)
        sef_education_dropout_grantee_count = len(updatable_sef_education_dropout_grantees)
        sef_apprenticeship_grantee_count = len(updatable_sef_apprenticeship_grantees)
        sef_nutrition_grantee_count = len(updatable_sef_nutrition_grantees)

        if sef_business_grantee_count > 0:
            print("Updating {} SEFBusinessGrantee items".format(sef_business_grantee_count))
            SEFBusinessGrantee.objects.bulk_update(objs=updatable_sef_business_grantees, using=write_db)
            print("Updated...")

        if sef_child_marriage_grantee_count > 0:
            print("Updating {} SEFEducationChildMarriageGrantee items".format(sef_child_marriage_grantee_count))
            SEFEducationChildMarriageGrantee.objects.bulk_update(
                objs=updatable_sef_child_marriage_grantees, using=write_db)
            print("Updated...")

        if sef_education_dropout_grantee_count > 0:
            print("Updating {} SEFEducationDropoutGrantee items".format(sef_education_dropout_grantee_count))
            SEFEducationDropoutGrantee.objects.bulk_update(
                objs=updatable_sef_education_dropout_grantees, using=write_db)
            print("Updated...")

        if sef_apprenticeship_grantee_count > 0:
            print("Updating {} SEFApprenticeshipGrantee items".format(sef_apprenticeship_grantee_count))
            SEFApprenticeshipGrantee.objects.bulk_update(objs=updatable_sef_apprenticeship_grantees, using=write_db)
            print("Updated...")

        if sef_nutrition_grantee_count > 0:
            print("Updating {} SEFNutritionGrantee items".format(sef_nutrition_grantee_count))
            SEFNutritionGrantee.objects.bulk_update(objs=updatable_sef_nutrition_grantees, using=write_db)
            print("Updated...")

    @classmethod
    def migrate_sef_grant_disbursement_ward_reference(cls, *args, **kwargs):
        updatable_sef_grant_disbursements = []
        for row in cls.load_data_from_csv(filepath)[1:]:
            pg_member_old_id = row[8]
            pg_member_pk = row[11]
            pg_member_new_id = row[12]

            print("PG Member Old ID: {}, PG Member PK: {}, PG Member New ID: {}".format(
                pg_member_old_id, pg_member_pk, pg_member_new_id))

            # sef grant disbursement
            queryset = SEFGrantDisbursement.objects.using(write_db).filter(
                pg_member_id=pg_member_pk
            ) | SEFGrantDisbursement.objects.using(write_db).filter(
                pg_member_assigned_code=pg_member_old_id
            )

            for sef_grant_disbursement_instance in queryset:
                sef_grant_disbursement_instance.pg_member_assigned_code = pg_member_new_id
                updatable_sef_grant_disbursements.append(sef_grant_disbursement_instance)

                if len(updatable_sef_grant_disbursements) == 500:
                    print("Updating 500 SEFGrantDisbursement items")
                    SEFGrantDisbursement.objects.bulk_update(objs=updatable_sef_grant_disbursements, using=write_db)
                    print("Updated...")
                    updatable_sef_grant_disbursements = []

        sef_grant_disbursement_count = len(updatable_sef_grant_disbursements)
        if sef_grant_disbursement_count > 0:
            print("Updating {} SEFGrantDisbursement items".format(sef_grant_disbursement_count))
            SEFGrantDisbursement.objects.bulk_update(objs=updatable_sef_grant_disbursements, using=write_db)
            print("Updated...")

    @classmethod
    def migrate_sef_tracker_ward_reference(cls, *args, **kwargs):
        cdc_list = []
        for row in cls.load_data_from_csv(filepath)[1:]:
            old_ward = row[4]
            new_ward = row[5]
            cdc_name = row[6]
            cdc_list.append((old_ward, new_ward, cdc_name))

        updatable_sef_trackers = []
        for old_ward, new_ward, cdc_name in set(cdc_list):
            cdc_instance = CDC.objects.using(write_db).get(
                address__geography__parent__name=city_name,
                name=cdc_name
            )
            sef_tracker_queryset = SEFTracker.objects.using(write_db).filter(
                cdc=cdc_instance
            )
            print("CDC: {}, Old Ward: {}, New Ward: {}".format(cdc_name, old_ward, new_ward, ))
            for sef_tracker_instance in sef_tracker_queryset:
                sef_tracker_instance.ward = new_ward
                updatable_sef_trackers.append(sef_tracker_instance)

                if len(updatable_sef_trackers) == 500:
                    print("Updating 500 SEFTracker items")
                    SEFTracker.objects.bulk_update(objs=updatable_sef_trackers, using=write_db)
                    print("Updated...")
                    updatable_sef_trackers = []

        if len(updatable_sef_trackers) > 0:
            print("Updating {} SEFTracker items".format(len(updatable_sef_trackers)))
            SEFTracker.objects.bulk_update(objs=updatable_sef_trackers, using=write_db)
            print("Updated...")

    @classmethod
    def migrate_housing_development_fund_pg_member_reference(cls, *args, **kwargs):
        updatable_items = []
        for row in cls.load_data_from_csv(filepath)[1:]:
            pg_member_old_id = row[8]
            pg_member_new_id = row[12]

            print("PG Member Old ID: {}, PG Member New ID: {}".format(pg_member_old_id, pg_member_new_id))

            queryset = CommunityHousingDevelopmentFund.objects.using(write_db).filter(pg_member_number=pg_member_old_id)
            for item in queryset:
                item.pg_member_number = pg_member_new_id
                updatable_items.append(item)
                if len(updatable_items) == 500:
                    print("Updating 500 CommunityHousingDevelopmentFund items")
                    CommunityHousingDevelopmentFund.objects.bulk_update(objs=updatable_items, using=write_db)
                    print("Updated...")
                    updatable_items = []

        if len(updatable_items) > 0:
            print("Updating {} CommunityHousingDevelopmentFund items".format(len(updatable_items)))
            CommunityHousingDevelopmentFund.objects.bulk_update(objs=updatable_items, using=write_db)
            print("Updated...")

    @classmethod
    def migrate_pg_member_reference_of_eligible_grantee_exported_file(cls, *args, **kwargs):
        filenames = [
            'eligibleapprenticeshipgrantee_Faridpur_2019_April.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2019_June.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2019_May.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2019_November.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2020_August.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2020_December.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2020_July.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2020_June.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2020_May.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2020_November.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2020_October.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2021_April.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2021_February.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2021_January.csv',
            'eligibleapprenticeshipgrantee_Faridpur_2021_March.csv',

            'eligiblebusinessgrantee_Faridpur_2019_April.csv',
            'eligiblebusinessgrantee_Faridpur_2019_June.csv',
            'eligiblebusinessgrantee_Faridpur_2019_May.csv',
            'eligiblebusinessgrantee_Faridpur_2019_November.csv',
            'eligiblebusinessgrantee_Faridpur_2020_August.csv',
            'eligiblebusinessgrantee_Faridpur_2020_December.csv',
            'eligiblebusinessgrantee_Faridpur_2020_July.csv',
            'eligiblebusinessgrantee_Faridpur_2020_June.csv',
            'eligiblebusinessgrantee_Faridpur_2020_May.csv',
            'eligiblebusinessgrantee_Faridpur_2020_November.csv',
            'eligiblebusinessgrantee_Faridpur_2020_October.csv',
            'eligiblebusinessgrantee_Faridpur_2021_April.csv',
            'eligiblebusinessgrantee_Faridpur_2021_February.csv',
            'eligiblebusinessgrantee_Faridpur_2021_January.csv',
            'eligiblebusinessgrantee_Faridpur_2021_March.csv',

            'eligibleeducationdropoutgrantee_Faridpur_2019_April.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2019_June.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2019_May.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2019_November.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2020_August.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2020_December.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2020_July.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2020_June.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2020_May.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2020_November.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2020_October.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2021_April.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2021_February.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2021_January.csv',
            'eligibleeducationdropoutgrantee_Faridpur_2021_March.csv',

            'eligibleeducationearlymarriagegrantee_Faridpur_2019_April.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2019_June.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2019_May.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2019_November.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2020_August.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2020_December.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2020_July.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2020_June.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2020_May.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2020_November.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2020_October.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2021_April.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2021_February.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2021_January.csv',
            'eligibleeducationearlymarriagegrantee_Faridpur_2021_March.csv'
        ]

        for filename in filenames:
            print("Processing File: {}".format(filename))
            fin = open("static_media/data/Faridpur_Eligible_Grantee/v1/" + filename, "rt")
            # read file contents to string
            data = fin.read()
            for row in cls.load_data_from_csv(filepath)[1:]:
                pg_member_old_id = row[8]
                pg_member_new_id = row[12]

                if pg_member_old_id in data:
                    print(pg_member_old_id)
                # replace all occurrences of the required string
                data = data.replace(pg_member_old_id, pg_member_new_id)
            # close the input file
            fin.close()

            # open the input file in write mode
            fin = open("static_media/data/Faridpur_Eligible_Grantee/v2/" + filename, "wt")
            # override the input file with the resulting data
            fin.write(data)
            # close the file
            fin.close()
            print("Processing completed.")
