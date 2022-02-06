"""This module is built of several functions that work as views for different urls in
the survey module. You will find the usage of the functions the urls.py of the survey module """

import json

from blackwidow.core.api.athorization import IsAuthorized
from blackwidow.core.models import ErrorLog
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from dynamic_survey.enums.dynamic_survey_status_enum import DynamicSurveyStatusEnum
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from dynamic_survey.models.design.dynamic_survey_group import DynamicSurveyGroup
from dynamic_survey.serializers.dynamic_survey.serializers import DetailSurveyDraftSerializer
from dynamic_survey.utils.dynamic_survey.survey_design_authentication import CsrfExemptSessionAuthentication
from dynamic_survey.utils.pyxform_utils import convert_xls_to_csv_string, \
    convert_xls_to_csv_string_except_groups
from dynamic_survey.utils.xlform import split_apart_survey


@login_required
def bulk_delete_questions(request):
    """
    This method receives delete api request and the corresponding ids of questions it has to delete from
    the question library and deletes them from DynamicSurvey model.

    :param request: delete request
    :type request: HttpRequest object
    :return: returns a `HttpResponse` of empty string
    :rtype: HttpResponse object
    """
    question_ids = json.loads((request.body).decode('utf-8'))
    try:
        for _each_object in DynamicSurvey.objects.filter(user=request.user).filter(id__in=question_ids):
            _each_object.is_deleted = True
            _each_object.deleted_level += 1
            _each_object.save()
    except Exception as e:
        ErrorLog.log(exp=e)
    return HttpResponse('')


@login_required
@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
@authentication_classes((CsrfExemptSessionAuthentication,))
@permission_classes((IsAuthorized,))
def survey_draft_detail(request, pk, format=None):
    """
    This function handles the detail api for DynamicSurvey model. The get, put, delete and patch request for
    a specific survey with the given id is handled in this function

    :param request: api request for either get, put, delete or patch
    :type request: HttpRequest object
    :param pk: primary key of the survey to be processed
    :type pk: integer
    :param format: format of api response
    :type format: str
    :return: Response object of DRF
    :rtype: Response object of DRF
    """
    kwargs = {'pk': pk}
    # if not request.user.is_superuser:
    #     kwargs['user'] = request.user

    # First we get the specific object
    try:
        survey_draft = DynamicSurvey.objects.get(**kwargs)
    except DynamicSurvey.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # For GET method we just return the serialized object
    if request.method == 'GET':
        # The object with the specific id is simply returned
        serializer = DetailSurveyDraftSerializer(survey_draft)
        return Response(serializer.data)

    # For PUT method first we check if the survey is in draft mode or if the survey is deleted or not.
    # If it's not in draft mode then a 400_Bad_Request Response is sent back. Otherwise the new survey is
    # saved
    elif request.method == 'PUT':
        if survey_draft.status != DynamicSurveyStatusEnum.Draft.value:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = DetailSurveyDraftSerializer(survey_draft, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # For Patch method we do exact same check as Put method. But while updating the survey
    # we update the specefic keys of the syrvey, instead of the whole survey
    elif request.method == 'PATCH':
        if survey_draft.status != DynamicSurveyStatusEnum.Draft.value:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for key, value in request.data.items():
            if key == 'tags':
                survey_draft.tags.clear()
                for val in value: survey_draft.tags.add(val)
            else:
                survey_draft.__setattr__(key, value)

        survey_draft.detail_link = str(survey_draft)

        survey_draft.save()

        return Response(DetailSurveyDraftSerializer(survey_draft).data)

    # We are soft deleting the survey. Survey is still there but user will not know this and will have a
    # chance to restore data
    elif request.method == 'DELETE':
        try:
            survey_draft.is_deleted = True
            survey_draft.deleted_level += 1
            survey_draft.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            ErrorLog.log(exp=e)


@login_required
def export_form(request, id):
    """
    This method is responsible for the downloading option of the survey as an excel sheet

    :param request: API request for downloading the form
    :type request: HttpRequest
    :param id: Primary key of the survey to be downloaded
    :type id: integer
    :return: HttpResponse which contains the xls file inside it
    :rtype: HttpResponse
    """
    survey_draft = DynamicSurvey.objects.get(pk=id)
    file_format = request.GET.get('format', 'xls')
    if file_format == "xls":
        contents = survey_draft.to_xls()
        mimetype = 'application/vnd.ms-excel; charset=utf-8'
    else:
        return HttpResponseBadRequest(
            "Format not supported: '%s'. Currently Supported format is only [xls]." % file_format)
    response = HttpResponse(contents, content_type=mimetype)
    response['Content-Disposition'] = 'attachment; filename=%s.%s' % (survey_draft.id_string,
                                                                      file_format)
    return response


XLS_CONTENT_TYPES = [
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/octet-stream",
]


@transaction.atomic
@login_required
def import_survey_draft(request):
    """
    Imports an XLS or CSV file into the user's DynamicSurvey list.
    Returns an error in JSON if the survey was not valid.


    :param request: API request for importing file
    :type request: HttpRequest
    :return: HttpResponse
    :rtype: HttpResponse
    """
    output = {}
    posted_file = request.FILES.get('files')
    response_code = 200
    if not posted_file:
        response_code = 204  # Error 204: No input
        output['error'] = "No file posted"
    else:

        # create and validate the xform but ignore the results
        warnings = []
        output['xlsform_valid'] = True

        posted_file.seek(0)
        if posted_file.content_type in XLS_CONTENT_TYPES:
            _csv = convert_xls_to_csv_string(posted_file)
        elif posted_file.content_type == "text/csv":
            _csv = posted_file.read()
        else:
            raise Exception("Content-type not recognized: '%s'" % posted_file.content_type)

        # Create a survey object first
        try:
            if "." in str(posted_file.name):
                new_name = str(posted_file.name)[:str(posted_file.name).index(".")]
                survey = DynamicSurveyGroup(group_name=new_name)
            else:
                survey = DynamicSurveyGroup(group_name=str(posted_file.name))
            survey.save()
        except Exception as e:
            ErrorLog.log(exp=e)
            raise Exception()

        # Then create the survey draft object and keep a reference of survey object there
        try:
            new_survey_draft = DynamicSurvey.objects.create(**{
                'body': str(_csv),
                'name': posted_file.name,
                'user': request.user,
            })
            new_survey_draft.detail_link = str(new_survey_draft)
            new_survey_draft.survey_id = survey.id
            new_survey_draft.save()
        except Exception as e:
            ErrorLog.log(exp=e)
            raise Exception()

        output['survey_draft_id'] = new_survey_draft.id
    return HttpResponse(json.dumps(output), content_type="application/json", status=response_code)


@transaction.atomic
@login_required
def import_questions(request):
    """
    Imports an XLS or CSV file into the user's Question Library list.
    Returns an error in JSON if the survey was not valid.

    :param request: API request for importing file
    :type request: HttpRequest
    :return: HttpResponse
    :rtype: HttpResponse
    """
    output = {}
    posted_file = request.FILES.get('files')
    response_code = 200
    if posted_file:
        posted_file.seek(0)

        if posted_file.content_type in XLS_CONTENT_TYPES:
            imported_sheets_as_csv = convert_xls_to_csv_string_except_groups(posted_file)
        elif posted_file.content_type == "text/csv":
            imported_sheets_as_csv = posted_file.read()
        else:
            raise Exception("Content-type not recognized: '%s'" % posted_file.content_type)

        split_surveys = split_apart_survey(imported_sheets_as_csv)

        for _split_survey in split_surveys:
            sd = DynamicSurvey(name='New Form',
                               body=_split_survey[0],
                               user=request.user,
                               asset_type='question',
                               organization=request.c_user.organization
                               )
            sd._summarize()
            sd.save()

        output['survey_draft_id'] = -1
    else:
        response_code = 204  # Error 204: No input
        output['error'] = "No file posted"
    return HttpResponse(json.dumps(output), content_type="application/json", status=response_code)
