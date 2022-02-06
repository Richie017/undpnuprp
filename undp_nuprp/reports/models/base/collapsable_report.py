from blackwidow.engine.extensions.bw_titleize import bw_titleize
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.models.base.cache.cache_base import CacheBase

__author__ = 'Tareq'


class CollapsableReport(Report):
    independent_field_values = None
    dependent_field_values = None
    annotations = None
    orders = None

    @classmethod
    def get_cache_class(cls):
        return CacheBase

    def get_base_queryset(self, filter=dict(), *args, **kwargs):
        return self.get_cache_class().objects.filter(**filter)

    def get_report_dataset_queryset(self, queryset=None, filter=dict(), *args, **kwargs):
        if self.independent_field_values is None:
            self.independent_field_values = self.get_independent_field_values(*args, **kwargs)
        if self.dependent_field_values is None:
            self.dependent_field_values = self.get_dependent_field_values(*args, **kwargs)
        if self.annotations is None:
            self.annotations = self.get_annotations(*args, **kwargs)
        if self.orders is None:
            self.orders = self.get_orders(*args, **kwargs)
        if queryset is None:
            queryset = self.get_base_queryset(filter=filter, *args, **kwargs)
        report_dataset = queryset.order_by(*self.orders).values(
            *(self.dependent_field_values + self.independent_field_values)).annotate(**self.annotations)
        return report_dataset

    @classmethod
    def get_independent_field_values(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: The tuple of values, that are not dependent on drilldown level.
        """
        return tuple()

    @classmethod
    def get_dependent_field_values(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: The tuple of values, that are dependent on drilldown level.
        """
        return tuple()

    @classmethod
    def get_annotations(cls, *args, **kwargs):
        """
        :return: Returns a dictionary of annotations
        """
        return dict()

    @classmethod
    def get_orders(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: the order of the queryset
        """
        return tuple()

    def get_column_headers(self, *args, **kwargs):
        if self.independent_field_values is None:
            self.independent_field_values = self.get_independent_field_values(*args, **kwargs)
        if self.dependent_field_values is None:
            self.dependent_field_values = self.get_dependent_field_values(*args, **kwargs)
        if self.annotations is None:
            self.annotations = self.get_annotations(*args, **kwargs)
        headers = [bw_titleize(v) for v in (self.dependent_field_values + self.independent_field_values)]
        headers += [bw_titleize(k) for k in self.annotations.keys()]
        return headers

    def build_report(self, styled=False, *args, **kwargs):
        report = list()
        headers = self.get_column_headers(*args, **kwargs)
        if styled:
            headers = tuple(headers)
        report.append(headers)
        dataset = self.get_report_dataset_queryset(*args, **kwargs)
        for data in dataset:
            if styled:
                report.append(tuple(data.values()))
            else:
                report.append(list(data.values()))
        return report
