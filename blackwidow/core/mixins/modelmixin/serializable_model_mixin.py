from modeltranslation.translator import TranslationOptions

__author__ = 'Mahmud'


class SerializableModelMixin(object):
    @property
    def serializable_fields(self):
        return ()

    @classmethod
    def get_system_fields(cls):
        return 'date_created', 'last_updated', 'is_active', 'is_deleted', 'is_locked', \
               'created_by', 'last_updated_by', 'type', 'context'

    @classmethod
    def intermediate_models(cls):
        return tuple()

    @classmethod
    def get_custom_serializers(cls):
        return tuple()

    @classmethod
    def serialize_fields(cls):
        return []

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            pass

        return DETranslationOptions

    @classmethod
    def get_api_filters(cls):
        """
        If there is any difference between the queryset for generic use and for mobile use, then the mobile based
        filters should be returned as dictionary format.
         For example:
         return {'parent__isnull': False, 'date_created__gt': 0}
        :return:
        A dictionary formatted search filters. None for no additional filter
        """
        return None

    @classmethod
    def get_model_api_queryset(cls, queryset=None, **kwargs):
        """
        If there is any difference between the queryset for generic use and for mobile use, then the mobile based
        queryset should be returned
        :return:
        A queryset. Highly recommended to use the queryset parameter as the base of returning queryset
        Example: return queryset.filter(parent__isnull=False).order_by('pk')
        """
        return queryset
