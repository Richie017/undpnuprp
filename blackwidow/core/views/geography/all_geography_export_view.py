from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
from blackwidow.core.models import AllGeography
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Ziaul Haque'


@decorate(override_view(model=AllGeography, view=ViewActionEnum.AdvancedExport))
class AllGeographyExportView(AdvancedGenericExportView):

    def get_queryset(self, request, **kwargs):
        _queryset = super(AllGeographyExportView, self).get_queryset(request=request, **kwargs)
        # return none queryset to avoid redundant initialization of geography queryset as exportable items already
        # handled in cls.initialize_export() method
        return _queryset.none()
