from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.core.models.information.news import News
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Tareq'


@override_view(model=News, view=ViewActionEnum.Details)
class NewsDetailsView(GenericDetailsView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_meta']['details'] = self.object.details
        context['model_meta']['subject'] = self.object.name
        return context
