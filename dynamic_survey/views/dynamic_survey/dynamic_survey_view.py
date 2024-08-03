"""This module takes care of the list view of surveys"""

import json
from collections import OrderedDict

from django.conf import settings
from django.forms import Form

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey

__author__ = 'Ziaul Haque'


@decorate(override_view(model=DynamicSurvey, view=ViewActionEnum.Manage))
class DynamicSurveyView(GenericListView):
    """ This class simply overrides two methods of `GenericListView`  and determines the view of
        the list of surveys.
    """

    def get_template_names(self):
        """

        :return: list of template names  that the view is going to provide the first one ot gets
        :rtype: list of string
        """

        return ['dynamic_survey/dynamic_survey.html']

    def get_context_data(self, **kwargs):
        """
        This method returns the context that the template is going to receive

        :param kwargs: variable number of keyword arguments
        :type kwargs: kwargs: variable number of keyword arguments
        :return: returns a dictionary that contains the context that the template is going to receive
        :rtype: dictionary
        """

        context = super().get_context_data(**kwargs)
        context['title'] = DynamicSurvey._registry[DynamicSurvey.__name__]['route']['display_name']

        page_configs = {
            'kobocatServer': "#",
            'previewServer': "#",
            'enketoServer': "#",
            'enketoPreviewUri': "webform/preview",
        }
        if self.request.user.is_authenticated():
            context['user_details'] = json.dumps({'name': self.request.user.email,
                                                  # 'gravatar': gravatar_url(request.user.email),
                                                  'gravatar': "",
                                                  'debug': True,
                                                  'username': self.request.user.username})
        else:
            context['user_details'] = "{}"
        context['page_kobo_configs'] = json.dumps(page_configs)
        context['root_url'] = DynamicSurvey._registry[DynamicSurvey.__name__]['route']['route']
        context['SECONDARY_LANGUAGE'] = settings.SECONDARY_LANGUAGE
        context["parameters"] = self.get_report_parameters(**kwargs)
        context["APPROVE_PERMISSION"] = False
        # if user has edit permission we are considering he has approve permission too
        if BWPermissionManager.has_edit_permission(request=self.request, model=DynamicSurvey):
            context["APPROVE_PERMISSION"] = True
        if settings.S3_STATIC_ENABLED:
            context['AWS_S3_CUSTOM_DOMAIN'] = settings.AWS_S3_CUSTOM_DOMAIN
        return context

    def get_wrapped_parameters(self, parameters):
        class DynamicForm(Form):
            pass

        form = DynamicForm()
        for p in parameters:
            form.fields[p['name']] = p['field']
        return form

    def get_report_parameters(self, **kwargs):
        parameters = OrderedDict()
        # parameters['G1'] = self.get_wrapped_parameters((
        #     {
        #         'name': 'infrastructure_unit_level',
        #         'field': GenericModelChoiceField(
        #             queryset=InfrastructureUnitLevel.objects.all(),
        #             initial=None,
        #             label='Infrastructure Unit Level',
        #             empty_label="Select One",
        #             required=True,
        #             widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        #         )
        #     },
        # ))
        # parameters['G1'] = self.get_wrapped_parameters((
        #     {
        #         'name': 'client_level',
        #         'field': GenericModelChoiceField(
        #             queryset=ClientLevel.objects.all(),
        #             initial=None,
        #             label='Client Level',
        #             empty_label="Select One",
        #             required=True,
        #             widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        #         )
        #     },
        # ))
        # parameters['G3'] = self.get_wrapped_parameters((
        #     {
        #         'name': 'product',
        #         'field': GenericModelChoiceField(
        #             queryset=Product.objects.all(),
        #             initial=None,
        #             label='Product',
        #             empty_label="Select One",
        #             required=True,
        #             widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        #         )
        #     },
        # ))

        return parameters
