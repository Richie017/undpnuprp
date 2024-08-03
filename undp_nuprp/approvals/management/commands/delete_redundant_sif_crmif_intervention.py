"""
    Created by Sayem on 08 February, 2021
    Organization Field Buzz
"""

__author__ = "Sayem"

from django.core.management import BaseCommand

from blackwidow.core.models import Location
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import SIFAndCRMIFIntervention


class Command(BaseCommand):
    """
    This command is prepared only for deleting redundant entries due to wrong implementation via import in
    SIF and CRMIF Intervention feature.
    Only needed for the *Production* server for ONE SINGLE time only.
    Reference Issue:https://redmine.field.buzz/issues/20477/
    """

    @staticmethod
    def delete_redundant_sif_crmif_intervention(*args, **kwargs):
        write_db = BWDatabaseRouter.get_write_database_name()
        sif_crmif_loc_img_pks = SIFAndCRMIFIntervention.objects.using(write_db).values("location_id", "image_id")
        location_ids = [inst.get("location_id") for inst in sif_crmif_loc_img_pks]
        if location_ids != [None] * len(location_ids):
            print("Start deleting redundant foreign key related `Location` data >>>>>>>")
            Location.objects.using(write_db).filter(id__in=location_ids).delete()
            print("<<<<<<< End deleting redundant foreign key related `Location` data")
        print("Start deleting all SIF and CRMIF intervention >>>>>")
        SIFAndCRMIFIntervention.objects.using(write_db).all().delete()
        print("<<<<<<< End deleting all SIF and CRMIF intervention")

    def handle(self, *args, **options):
        self.delete_redundant_sif_crmif_intervention(*args, **options)
