from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'activehigh'


@decorate(override_view(model=ErrorLog, view=ViewActionEnum.Details))
class ErrorDetailsView(GenericDetailsView):
    def get_template_names(self):
        return ['error/details.html']
