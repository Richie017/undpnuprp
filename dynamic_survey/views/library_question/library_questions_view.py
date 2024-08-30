""" This module handles the view of Question Library """

import json

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.core.generics.views.list_view import GenericListView

from dynamic_survey.models.design.library_questions import LibraryQuestions
from django.conf import settings

__author__ = 'Ziaul Haque'


@decorate(override_view(model=LibraryQuestions, view=ViewActionEnum.Manage))
class LibraryQuestionsView(GenericListView):
    """ This class simply overrides two methods of `GenericListView`  and determines the view of
        Question library.
    """

    def get_template_names(self):
        """

        :return: list of template names  that the view is going to provide the first one ot gets
        :rtype: list of string
        """
        return ['library_question/library_question.html']

    def get_context_data(self, **kwargs):
        """
        This method returns the context that the template is going to receive

        :param kwargs: variable number of keyword arguments
        :type kwargs: kwargs: variable number of keyword arguments
        :return: returns a dictionary that contains the context that the template is going to receive
        :rtype: dictionary
        """
        context = super().get_context_data(**kwargs)
        context['title'] = LibraryQuestions._registry[LibraryQuestions.__name__]['route']['display_name']

        page_configs = {
            'kobocatServer': "#",
            'previewServer': "#",
            'enketoServer': "#",
            'enketoPreviewUri': "webform/preview",
        }
        if self.request.user.is_authenticated:
            context['user_details'] = json.dumps({'name': self.request.user.email,
                                                  # 'gravatar': gravatar_url(request.user.email),
                                                  'gravatar': "",
                                                  'debug': True,
                                                  'username': self.request.user.username})
        else:
            context['user_details'] = "{}"
        context['page_kobo_configs'] = json.dumps(page_configs)
        context['root_url'] = LibraryQuestions._registry[LibraryQuestions.__name__]['route']['route']
        if settings.S3_STATIC_ENABLED:
            context['AWS_S3_CUSTOM_DOMAIN'] = settings.AWS_S3_CUSTOM_DOMAIN
        return context
