"""survey-design URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from rest_framework import routers

from dynamic_survey.api.dynamic_survey.api import *
from dynamic_survey.models.design.library_questions import LibraryQuestions
from dynamic_survey.views.dynamic_survey.views import *

router_survey_draft = routers.DefaultRouter(trailing_slash=False)
router_library_questions = routers.DefaultRouter(trailing_slash=False)

router_survey_draft.register(r'survey_drafts', SurveyDraftViewSet, 'SurveyDraft')
router_library_questions.register(r'library_assets', LibraryAssetViewset, 'LibraryAsset')
router_library_questions.register(r'tags', TagViewset, 'Tag')

try:
    survey_design_prefix_url = DynamicSurvey._registry[DynamicSurvey.__name__]['route']['route']
    library_questions_prefix_url = LibraryQuestions._registry[LibraryQuestions.__name__]['route']['route']
except KeyError:
    raise KeyError
urlpatterns = [
    url(r'^import_survey_draft$', import_survey_draft),
    url(r'^import_questions$', import_questions),
]


urlpatterns += i18n_patterns(
    url(r'^' + library_questions_prefix_url + '/api/bulk_delete/library_assets', bulk_delete_questions),
    url(r'^' + library_questions_prefix_url + '/api/library_assets/(?P<pk>\d+)$', survey_draft_detail),
    url(r'^' + library_questions_prefix_url + '/api/', include(router_library_questions.urls)),

    url(r'^' + survey_design_prefix_url + '/api/survey_drafts/(?P<pk>\d+)$', survey_draft_detail),
    url(r'^' + survey_design_prefix_url + '/api/', include(router_survey_draft.urls + router_library_questions.urls)),
    url(r'^' + survey_design_prefix_url + '/forms/(?P<id>\d+)', export_form),
    url(r'^' + survey_design_prefix_url + '/assets/(\d+)', export_form),
    # url(r'^' + survey_design_prefix_url + '/parser/(\d+)', parse_survey)

)
