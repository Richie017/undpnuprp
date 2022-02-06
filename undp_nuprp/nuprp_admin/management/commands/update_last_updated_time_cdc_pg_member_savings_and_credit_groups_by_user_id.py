"""
    Written by shuvro on 27/06/2019
"""
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from blackwidow.core.models.users.user import ConsoleUser
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_id = input('User ID: ')
        with transaction.atomic():
            try:
                c_user = ConsoleUser.objects.filter(id=int(user_id)).first()
                if not c_user:
                    print("User does not exist")
                    return
                _city_id = c_user.addresses.first().geography.parent_id

                _cur_time = int(datetime.now().timestamp() * 1000)

                updated = CDC.objects.filter(address__geography__parent_id=_city_id).update(
                    last_updated=_cur_time
                )

                print('Total {} cdc entries last updated time has updated'.format(updated))

                updated = PrimaryGroup.objects.filter(parent__address__geography__parent_id=_city_id).update(
                    last_updated=_cur_time
                )

                print('Total {} primary groups entries last updated time has updated'.format(updated))

                updated = SavingsAndCreditGroup.objects.filter(address__geography_id=_city_id).update(
                    last_updated=_cur_time
                )
                print('Total {} savings and credit groups last updated time has updated'.format(updated))

            except:
                print('Invalid user')
