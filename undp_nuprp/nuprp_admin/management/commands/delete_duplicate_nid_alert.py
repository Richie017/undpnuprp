from django.core.management.base import BaseCommand

from undp_nuprp.nuprp_admin.models import DuplcateIdAlert


class Command(BaseCommand):
    def handle(self, *args, **options):
        duplicate_queryset = DuplcateIdAlert.objects.filter(
            body__icontains="PG Member's NID is N/A, which is already the NID of,")
        count = duplicate_queryset.count()
        duplicate_queryset.delete()
        print(str(count)+" Item are deleted")