from django.core.management import BaseCommand
from django.db.models.functions import Length

from blackwidow.engine.extensions import Clock
from undp_nuprp.nuprp_admin.models import PrimaryGroup, PrimaryGroupMember


class Command(BaseCommand):
    def handle(self, *args, **options):
        queryset = PrimaryGroupMember.objects.annotate(
            pg_code_length=Length('assigned_to__assigned_code')
        ).filter(pg_code_length=9)
        updatable_entries = []

        current_timestamp = Clock.timestamp()
        count = 0
        for pgm in queryset:
            pgm.last_2_digits_of_assigned_code = int(pgm.assigned_code[-2:])
            pgm.last_updated = current_timestamp
            current_timestamp += 1
            updatable_entries.append(pgm)
            count += 1
            if count % 100 == 1:
                print("Total processed {}".format(count))

        if len(updatable_entries) > 0:
            PrimaryGroupMember.objects.bulk_update(updatable_entries, batch_size=500)
            print("bulk updatation completed for primary group members")

        queryset = PrimaryGroup.objects.annotate(
            assigned_code_length=Length('assigned_code')
        ).filter(assigned_code_length=9)
        updatable_entries = []

        current_timestamp = Clock.timestamp()
        count = 0
        for pgm in queryset:
            pgm.last_updated = current_timestamp
            current_timestamp += 1
            updatable_entries.append(pgm)
            count += 1
            if count % 100 == 1:
                print("Total processed {}".format(count))

        if len(updatable_entries) > 0:
            PrimaryGroup.objects.bulk_update(updatable_entries, batch_size=500)
            print("bulk updatation completed for primary group")
