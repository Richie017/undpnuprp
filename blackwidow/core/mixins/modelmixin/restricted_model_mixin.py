__author__ = 'Mahmud'


class RestrictedModelMixin(object):

    @classmethod
    def get_queryset(cls, queryset=None, **kwargs):
        return queryset

