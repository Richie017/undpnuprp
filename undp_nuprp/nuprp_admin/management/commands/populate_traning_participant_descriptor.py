from django.core.management.base import BaseCommand
from django.db import transaction

from undp_nuprp.nuprp_admin.models.descriptors.training_participant import TrainingParticipant

__author__ = 'Shuvro'

training_participants = ['LG', 'PG', 'Non-PG', 'NUPRP staff', 'Other']


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            print('Creating Traning Participant...')
            for tp in training_participants:
                TrainingParticipant.objects.create(name=tp)
                print('{} created successfully!'.format(tp))

        print('Total {} participants created!'.format(len(training_participants)))
