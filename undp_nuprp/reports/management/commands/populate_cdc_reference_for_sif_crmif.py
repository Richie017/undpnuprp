from django.core.management.base import BaseCommand

from undp_nuprp.approvals.models.infrastructures.crmif.crmif import CRMIF
from undp_nuprp.approvals.models.infrastructures.sif.sif import SIF
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        sif_objects = SIF.objects.all()
        for sif_object in sif_objects:
            if sif_object.contract_with_cdc_or_cluster == 'CDC' or sif_object.contract_with_cdc_or_cluster is None:
                _cdc = CDC.objects.filter(name=sif_object.cdc_or_cluster_name,
                                          assigned_code=sif_object.cdc_or_cluster_id).last()
                sif_object.contract_with_cdc_or_cluster = 'CDC'  # existing data to cdc
                sif_object.assigned_cdc = _cdc
                sif_object.assigned_city = _cdc.render_city_corporation
            else:
                _cluster = CDCCluster.objects.filter(name=sif_object.cdc_or_cluster_name,
                                                     assigned_code=sif_object.cdc_or_cluster_id).last()
                sif_object.assigned_cdc_cluster = _cluster
                sif_object.assigned_city = _cluster.address.geography.name if _cluster else ''
            sif_object.save()

        crmif_objects = CRMIF.objects.all()
        for crmif_object in crmif_objects:
            if crmif_object.contract_with_cdc_or_cluster == 'CDC' or crmif_object.contract_with_cdc_or_cluster is None:
                _cdc = CDC.objects.filter(name=crmif_object.cdc_or_cluster_name,
                                          assigned_code=crmif_object.cdc_or_cluster_id).last()
                crmif_object.contract_with_cdc_or_cluster = 'CDC'  # existing data to cdc
                crmif_object.assigned_cdc = _cdc
                crmif_object.assigned_city = _cdc.render_city_corporation
            else:
                _cluster = CDCCluster.objects.filter(name=crmif_object.cdc_or_cluster_name,
                                                     assigned_code=crmif_object.cdc_or_cluster_id).last()
                crmif_object.assigned_cdc_cluster = _cluster
                crmif_object.assigned_city = _cluster.address.geography.name if _cluster else ''
            crmif_object.save()
