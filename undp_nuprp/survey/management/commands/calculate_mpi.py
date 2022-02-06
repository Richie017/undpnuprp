"""
    Created by tareq on 3/13/17
"""
from django.core.management.base import BaseCommand

from undp_nuprp.survey.models import PGMPIIndicator
# from undp_nuprp.survey.models.indicators.mpi_indicator import MPIIndicator
from datetime import datetime
__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        begin_time = datetime.now()
        # MPIIndicator.generate(batch_size=1000)
        PGMPIIndicator.generate(batch_size=1000)
        end_time = datetime.now()
        print('Time taken {} seconds'.format(end_time.timestamp()-begin_time.timestamp()))
