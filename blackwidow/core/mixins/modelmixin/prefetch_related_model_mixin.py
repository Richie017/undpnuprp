__author__ = 'Tareq'


class PrefetchRelatedModelMixin(object):
    @classmethod
    def prefetch_objects(cls):
        """
        This method is used to define the list of related objects that need to be prefetched in the queryset
        :return: a list(any iterable) of string denoting the related fields of a model
        """
        return []

    @classmethod
    def prefetch_api_objects(cls):
        """
        This method is used to define the list of related objects that need to be prefetched in the api queryset
        :return: a list(any iterable) of string denoting the related fields of a model
        """
        return []
