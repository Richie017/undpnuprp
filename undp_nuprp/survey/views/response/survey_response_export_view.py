"""
Created by tareq on 4/27/17
"""

import json

from django.http.response import HttpResponse

from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


@decorate(override_view(model=SurveyResponse, view=ViewActionEnum.AdvancedExport))
class SurveyResponseExportView(AdvancedGenericExportView):
    def get(self, request, *args, **kwargs):
        if not BWPermissionManager.has_view_permission(self.request, self.model):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")

        if request.GET.get("get_form") == '1':
            response = {
                "status": "SUCCESS",
                "message": "Successful",
                "data": {
                    "form": 0
                }
            }
            return HttpResponse(json.dumps(response))

        export_file = SurveyResponseGeneratedFile.objects.first().file
        file_name = export_file.name
        return self.render_json_response({
            'message': file_name,
            'success': True
        })
