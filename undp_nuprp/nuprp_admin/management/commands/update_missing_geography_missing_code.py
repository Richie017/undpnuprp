from django.core.management.base import BaseCommand

from blackwidow.core.models.geography.geography import Geography

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        Geography.generate_missing_codes()

        print("Missing code updated successfully")
