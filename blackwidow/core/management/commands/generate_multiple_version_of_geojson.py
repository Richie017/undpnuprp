from django.contrib.gis.geos import Polygon, MultiPolygon, GEOSGeometry, WKTWriter
from django.core.management import BaseCommand

from blackwidow.core.models import GeoJson

TOLERANCE_MEDIUM = 0.0003
TOLERANCE_LOW = 0.0004

__author__ = "Ziaul Haque"


class Command(BaseCommand):
    def handle(self, *args, **options):
        queryset = GeoJson.objects.all()
        wkt_w = WKTWriter()  # instantiate WKT writer class
        wkt_w.precision = 8  # precision is eight to round coordinates upto 6 decimal places

        for q in queryset:
            actual = q.multi_polygon_actual
            medium = actual.simplify(TOLERANCE_MEDIUM)
            low = actual.simplify(TOLERANCE_LOW)
            q.multi_polygon_medium = MultiPolygon(medium) if type(medium) == Polygon else medium
            q.multi_polygon_low = MultiPolygon(low) if type(low) == Polygon else low

            # rounding precision of multipolygon coordinates
            q.multi_polygon_medium = GEOSGeometry(wkt_w.write(q.multi_polygon_medium))
            q.multi_polygon_low = GEOSGeometry(wkt_w.write(q.multi_polygon_low))

            q.save()
            print(q)
