from datetime import datetime

from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
from blackwidow.core.models import Geography
from blackwidow.engine.exceptions import BWException
from blackwidow.engine.extensions.bw_titleize import bw_compress_name
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import GranteeGeneratedFile

__author__ = 'Ziaul Haque'


class GranteeListExportView(AdvancedGenericExportView):

    def start_background_worker(self, request, organization, export_file_name, *args, **kwargs):
        _name = self.generate_file_name()

    def generate_file_name(self):
        dest_filename = self.model.get_export_file_name()
        year = self.request.GET.get('year', None)
        month = self.request.GET.get('month', None)
        city = self.request.GET.get('city', None)

        month_number = datetime.strptime(month, "%B").month

        generated_file = GranteeGeneratedFile.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).filter(year=year, month=month_number, city_id=city).first()
        if not generated_file:
            raise BWException("Grantee export file does not exist.")

        city_name = ''
        if city:
            try:
                city_name = Geography.objects.using(BWDatabaseRouter.get_export_database_name()).get(pk=city).name
            except:
                pass

        dest_filename = '_'.join(
            [dest_filename, bw_compress_name(city_name)]) if city_name else dest_filename

        dest_filename = '_'.join(
            [dest_filename, bw_compress_name(year)]) if year else dest_filename

        dest_filename = '_'.join(
            [dest_filename, bw_compress_name(month)]) if month else dest_filename

        return dest_filename
