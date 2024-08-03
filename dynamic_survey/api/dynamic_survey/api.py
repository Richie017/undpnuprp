"""
    This module consists of 4 Classes:
     1. SurveyAssetViewset:
        This class determines the behaviour of listing and creating of ``DynamicSurvey`` objects from API request.
     2. TagViewset:
        This class determines the behaviour of listing and creating of ``Tag`` objects for survey questions from API
        request.
     3. LibraryAssetViewset:
        This class is simply derived from ``SurveyAssetViewset`` and trivial change is done.
     4. SurveyDraftViewSet:
        This class is simply derived from ``SurveyAssetViewset`` and trivial change is done.

    From ``surveydesign.urls.py`` these classes are called from corresponding urls. Just open ``surveydesign.urls.py``
    and you will find for which urls they are called.
"""
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from taggit.models import Tag

from blackwidow.core.api.athorization import IsAuthorized
from blackwidow.core.models import ErrorLog
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from dynamic_survey.models.design.dynamic_survey_group import DynamicSurveyGroup
from dynamic_survey.serializers.dynamic_survey.serializers import ListSurveyDraftSerializer, DetailSurveyDraftSerializer, \
    TagSerializer
from dynamic_survey.utils.dynamic_survey.survey_design_authentication import CsrfExemptSessionAuthentication


class SurveyAssetViewset(viewsets.ModelViewSet):
    """
    This class works with ``DynamicSurvey`` model and ``ListSurveyDraftSerializer`` serializer class. The authentication
    class is ``CsrfExemptSessionAuthentication`` and the permission class is ``IsAuthorized``. Pagination class is set to ``None``,
    It does basically 3 tasks.
        1. Returning list of ``DynamicSurvey`` objects from proper GET API request.
        2. Creating new ``DynamicSurvey`` object from proper POST API request.
        3. Returning a specific ``DynamicSurvey`` object with a specific primary key from proper GET API request.
    """

    model = DynamicSurvey
    serializer_class = ListSurveyDraftSerializer
    exclude_asset_type = False
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthorized,)
    pagination_class = None

    def get_queryset(self):
        """
        This method comes into play when a GET API request is invoked to get the list of ``DynamicSurvey`` objects.
        It filters all the undeleted ``DynamicSurvey`` objects and returns them ordered(descending) by modification date.
        If the user is anonymous permission is denied immediately.


        :return: returns serialized list of ``DynamicSurvey`` objects if proper GET API request is received
        :rtype: A Response object of Django Rest Framework
        """
        user = self.request.user
        if user.is_anonymous():
            raise PermissionDenied
        queryset = DynamicSurvey.objects.all()
        if self.exclude_asset_type:
            queryset = queryset.exclude(asset_type=None)
        else:
            queryset = queryset.filter(asset_type=None)

        return queryset.order_by('-date_modified')

    @transaction.atomic
    def create(self, request):
        """
        This method comes into play when a POST API request is invoked to create a  brand new ``DynamicSurvey`` object.
        If the user is anonymous permission is denied immediately. If there are any tags connected with
        questions they are removed first. Then it performs the following tasks sequentially:
        1. Creating the parent ``DynamicSurveyGroup`` object for the current survey with version 1.
        2. Checks if an ``ApprovalProcess`` exists for this model.
        3. Creating the ``DynamicSurvey`` object under the current user.
        4. Creating an ``ApprovalAction`` for the current survey and add this to the ``ApprovalProcess`` of this model.
        5. Add the the deleted tags.
        6. Return the created ``DynamicSurvey`` object object as serialized data(JSON).

        If any error occurs in the process Exception is raised and saved in Error.



        :param request: POST API request  with proper authentication and authorization
        :type request: HttpRequest
        :return: returns the serialized survey draft object created if created successfully otherwise Exception is raised
        :rtype: A Response object of Django Rest Framework
        """

        user = self.request.user
        if user.is_anonymous():
            raise PermissionDenied
        contents = request.data
        tags = contents.get('tags', [])
        if 'tags' in contents:
            del contents['tags']

        # Create a survey object first
        try:
            survey = DynamicSurveyGroup(group_name=contents['name'])
            survey.save()
        except Exception as e:
            ErrorLog.log(exp=e)
            raise Exception()

        # Then create survey draft object and keep a reference of survey object there
        try:
            survey_draft = request.user.survey_drafts.create(**contents)
            survey_draft.detail_link = str(survey_draft)
            survey_draft.survey_id = survey.id
            survey_draft.save()
        except Exception as e:
            ErrorLog.log(exp=e)
            raise Exception()

        for tag in tags:
            survey_draft.tags.add(tag)

        return Response(ListSurveyDraftSerializer(survey_draft).data)

    def retrieve(self, request, pk=None):
        """
        This method comes into play when a GET API request is invoked to get a specific DynamicSurvey with a specific
        primary key as pk. If that DynamicSurvey doesn't exist a 404 exception is raised otherwise the serialized version
        of the DynamicSurvey is returned as a response.



        :param request: GET API request with proper authentication and authorization
        :type request: HttpRequest from django.http
        :param pk: The primary key of the desired survey draft object
        :type pk: int
        :return: returns serialized survey draft of the corresponding pk if proper GET API request is received.
        :rtype: A Response object of Django Rest Framework
        """
        if request.user.is_anonymous():
            raise PermissionDenied
        queryset = DynamicSurvey.objects.all()
        survey_draft = get_object_or_404(queryset, pk=pk)
        return Response(DetailSurveyDraftSerializer(survey_draft).data)


class TagViewset(viewsets.ModelViewSet):
    """
    This class works with ``Tag`` model and ``TagSerializer`` serializer class. The authentication class is
    ``CsrfExemptSessionAuthentication`` and the permission class is ``IsAuthorized``. Pagination class is set to ``None``.
    It does basically 2 tasks.
        1. Returning a list of ``Tag`` objects from proper GET API request.
        2. Deleting a specific ``Tag`` object with specific primary key from proper DELETE API request.
    """

    model = Tag
    serializer_class = TagSerializer
    try:
        _survey_draft_content_type = ContentType.objects.get_for_model(DynamicSurvey)
    except Exception as e:
        print(
            "WARNING: django_content_type relation is not found yet. \
            You will not see this warning after the very first migration being done. \
            Just carry on the routine commands.")

    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthorized,)
    pagination_class = None

    def get_queryset(self, *args, **kwargs):
        """
        Returns the the list of distinct ``Tag`` objects under a user if the user is authenticated else
        ``Tag.objects.none()`` is returned.


        :param args: variable number of positional arguments
        :type args:
        :param kwargs: variable number of keyword arguments
        :type kwargs:
        :return: returns list of ``Tag`` object if proper GET API request is received.
        :rtype: ``Tag`` object
        """
        user = self.request.user
        if user.is_authenticated():
            ids = user.survey_drafts.all().values_list('id', flat=True)
            return Tag.objects.filter(
                taggit_taggeditem_items__object_id__in=ids,
                taggit_taggeditem_items__content_type=self._survey_draft_content_type
            ).distinct()
        else:
            return Tag.objects.none()

    def destroy(self, request, pk):
        """
        Gets the ``Tag`` object having the corresponding primary key as pk and deletes that tag from
        each ``DynamicSurvey`` object.

        :param request: DELETE API request with proper authentication and authorization
        :type request: HttpRequest from django.http
        :param pk: The primary key of the desired ``Tag`` object to be deleted
        :type pk: int
        :return: HttpResponse with status 204 if successfully removed
        :rtype: HttpResponse from django.shortcuts
        """
        if request.user.is_authenticated():
            tag = Tag.objects.get(id=pk)
            items = DynamicSurvey.objects.filter(tags__name=tag.name)
            for item in items:
                item.tags.remove(tag)
            return HttpResponse("", status=204)


class LibraryAssetViewset(SurveyAssetViewset):
    """
    Inherited from ``SurveyAssetViewset`` class. The only changes are:
    1. ``DetailSurveyDraftSerializer`` used as serializer class.
    2. ``LibraryAssetPagination`` defined inside and set as the pagination class.
    """
    exclude_asset_type = True
    serializer_class = DetailSurveyDraftSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthorized,)

    class LibraryAssetPagination(PageNumberPagination):
        """Page size is set to 100"""

        page_size = 100

    pagination_class = LibraryAssetPagination


class SurveyDraftViewSet(SurveyAssetViewset):
    """
    Inherited from ``SurveyAssetViewset`` class. The only changes are:
    1. ``exclude_asset_type`` is set to ``False``
    """
    exclude_asset_type = False
