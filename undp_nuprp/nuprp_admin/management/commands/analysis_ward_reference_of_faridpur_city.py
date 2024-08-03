import csv
import os

from django.core.management import BaseCommand

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from settings import STATIC_ROOT
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember, CDC

__author__ = 'Ziaul Haque'

write_db = BWDatabaseRouter.get_write_database_name()


class Command(BaseCommand):

    @classmethod
    def load_data_from_csv(cls, csv_path):
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            data = []
            for row in csv_reader:
                data.append(row)
            return data

    @staticmethod
    def to_int(value, default):
        int_ = value
        try:
            int_ = int(int_)
        except:
            return default
        return int_

    def handle(self, *args, **options):

        self.export_pg_member_data(*args, **options)
        self.verify_cdc_data(*args, **options)

    @classmethod
    def export_pg_member_data(cls, *args, **kwargs):
        export_filepath = os.path.join(STATIC_ROOT, 'data/')
        if not os.path.exists(export_filepath):
            os.makedirs(export_filepath)

        export_file = open(export_filepath + 'FaridpurCityWardReference_v2.csv', "w", encoding='utf-8')

        export_file.write(
            'Division,City/Town,Cluster-ID,Cluster name,Ward Number,Change Ward Number,CDC,Primary Group,'
            'PG Member ID (Need to change ward number according to change ward),PG Member Name,PG Member Phone Number,'
            'PG Member PK,PG Member New ID,Duplicate PG Member Count\n'
        )

        filepath = os.path.join(STATIC_ROOT, 'data', 'FaridpurCityWardReference.csv')
        for row in cls.load_data_from_csv(filepath)[1:]:
            division = row[0]
            city_name = row[1]
            cluster_id = row[2]
            cluster_name = row[3]
            old_ward = row[4]
            new_ward = row[5]
            cdc_name = row[6]
            pg_name = row[7]
            pg_member_old_id = row[8]
            pg_member_name = row[9]
            pg_member_phone = row[10]

            if len(old_ward) == 1:
                old_ward = "0" + str(old_ward)

            if len(new_ward) == 1:
                new_ward = "0" + str(new_ward)

            try:
                pg_member_pk = PrimaryGroupMember.objects.using(write_db).get(assigned_code=pg_member_old_id).pk
            except:
                pg_member_pk = 0

            pg_member_new_id = ""
            for index, value in enumerate(list(pg_member_old_id)):
                if index == 3:
                    value = new_ward[0]
                elif index == 4:
                    value = new_ward[1]
                pg_member_new_id += value
            print("Old Ward: {}, New Ward: {}, PG Member Old ID: {}, PG Member New ID: {}".format(
                old_ward, new_ward,
                pg_member_old_id,
                pg_member_new_id
            ))

            duplicate_pg_member_count = PrimaryGroupMember.objects.using(write_db).filter(
                assigned_code=pg_member_new_id
            ).count()

            export_file.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                division, city_name, cluster_id, cluster_name, old_ward, new_ward, cdc_name, pg_name, pg_member_old_id,
                pg_member_name, pg_member_phone, pg_member_pk, pg_member_new_id, duplicate_pg_member_count
            ))

        export_file.close()

    @classmethod
    def verify_cdc_data(cls, *args, **kwargs):
        cdc_list = []
        filepath = os.path.join(STATIC_ROOT, 'data', 'FaridpurCityWardReference.csv')
        for row in cls.load_data_from_csv(filepath)[1:]:
            old_ward = row[4]
            new_ward = row[5]
            cdc_name = row[6]

            if len(old_ward) == 1:
                old_ward = "0" + str(old_ward)

            if len(new_ward) == 1:
                new_ward = "0" + str(new_ward)

            cdc_list.append((old_ward, new_ward, cdc_name))

        for old_ward, new_ward, cdc_name in set(cdc_list):
            print("CDC Name: {}, Count: {}".format(
                cdc_name, CDC.objects.using(write_db).filter(
                    address__geography__parent__name='Faridpur',
                    name=cdc_name
                ).count())
            )
