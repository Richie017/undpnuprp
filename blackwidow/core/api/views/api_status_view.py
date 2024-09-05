from django.urls import Resolver404
from django.db.models.aggregates import Max
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from blackwidow.core.api.athorization.is_authorized import IsAuthorized
from blackwidow.core.api.athorization.token_authentication import BWTokenAuthentication
from blackwidow.core.api.renderers.generic_renderer import GenericJsonRenderer
from blackwidow.core.models.log.api_call_log import ApiCallLog
from blackwidow.core.models.log.audit_log import DeleteLog, RestoreLog
from blackwidow.engine.constants.cache_constants import STATUS_API_PREFIX, ONE_MONTH_TIMEOUT, DELETED_LIST_PREFIX, \
    USER_LOGIN_INFO_PREFIX, ONE_DAY_TIMEOUT, HELP_INFO_PREFIX
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.extensions.model_descriptor import get_model_by_name
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.apps import INSTALLED_APPS

__author__ = 'Mahmud'


class ApiStatusView(APIView):
    authentication_classes = (BWTokenAuthentication,)
    permission_classes = (IsAuthorized,)
    renderer_classes = (GenericJsonRenderer,)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        log = ApiCallLog.log(request=request, log_time=True)
        if log:
            self._api_log = log
        return super(ApiStatusView, self).dispatch(request, *args, **kwargs)

    def populate_child_model_list(self, models=[]):
        name_list = list()
        for model in models:
            name_list.append(model.__name__)
            name_list += self.populate_child_model_list(model.__subclasses__())
        return name_list

    def get_candidate_model_names(self, model):
        decorators = [x.__name__ for x in model._decorators]
        if 'travarse_child_for_status' in decorators:
            return [model.__name__] + self.populate_child_model_list(model.__subclasses__())
        return [model.__name__]

    def finalize_response(self, request, response, *args, **kwargs):
        _api_log = None
        if hasattr(self, '_api_log'):
            _api_log = self._api_log
        log = ApiCallLog.log(request=request, response=response, log_instance=_api_log, log_time=False)
        if log:
            self._api_log = log
        return super().finalize_response(request, response, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        models = get_models_with_decorator('save_audit_log', INSTALLED_APPS, include_class=True)
        m2m_tracking_models = get_models_with_decorator('enable_m2m_tracking', INSTALLED_APPS, include_class=True)
        for m2m_model in m2m_tracking_models:
            if not m2m_model in models:
                models += [m2m_model]
        m_models = get_models_with_decorator('is_profile_content', INSTALLED_APPS, include_class=True)
        for m in models:
            status_key = m.get_status_api_key()
            if m in m_models:
                try:
                    last_updated = CacheManager.get_from_cache_by_key(STATUS_API_PREFIX + status_key)
                    if last_updated is None:
                        last_updated = \
                            m.get_queryset(queryset=m.objects.using(BWDatabaseRouter.get_read_database_name()).all(),
                                           user=request.c_user).aggregate(
                                last_updated=Max('last_updated'))['last_updated']
                        last_updated = (last_updated if last_updated is not None else 0)
                        data[status_key] = {
                            'last_updated': last_updated
                        }
                        CacheManager.set_cache_element_by_key(STATUS_API_PREFIX + status_key, last_updated,
                                                              ONE_MONTH_TIMEOUT)
                    else:
                        data[status_key] = {'last_updated': last_updated}
                        # data[status_key]['deleted'] = [x['model_pk'] for x in DeleteLog.objects.filter(model_name=m.__name__).values('model_pk')]
                except Resolver404 as exp:
                    pass
            else:
                try:
                    lookup_field = 'last_updated'
                    last_updated = CacheManager.get_from_cache_by_key(STATUS_API_PREFIX + status_key)
                    if last_updated is None:
                        last_updated = m.objects.using(BWDatabaseRouter.get_read_database_name()).aggregate(
                            last_updated=Max(lookup_field))['last_updated']
                        last_updated = last_updated if last_updated is not None else 0
                        data[status_key] = {
                            'last_updated': last_updated
                        }
                        CacheManager.set_cache_element_by_key(STATUS_API_PREFIX + status_key, last_updated,
                                                              ONE_MONTH_TIMEOUT)
                    else:
                        data[status_key] = {'last_updated': last_updated}

                    one_month = 30 * 24 * 60 * 60 * 1000

                    candidate_deleted_list = CacheManager.get_from_cache_by_key(DELETED_LIST_PREFIX + status_key)
                    if candidate_deleted_list is None:
                        deleted_items = DeleteLog.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                            model_name__in=self.get_candidate_model_names(m),
                            date_created__gte=(
                                    Clock.timestamp() - (2 * one_month))).values(
                            'model_pk').annotate(latest=Max('date_created')).values('model_pk', 'latest')
                        deleted_dict = dict()
                        for _item in deleted_items:
                            deleted_dict[_item['model_pk']] = _item['latest']

                        restored_items = RestoreLog.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                            model_name__in=self.get_candidate_model_names(m),
                            date_created__gte=(
                                    Clock.timestamp() - (2 * one_month))).values(
                            'model_pk').annotate(latest=Max('date_created')).values('model_pk', 'latest')
                        restored_dict = dict()
                        for _item in restored_items:
                            restored_dict[_item['model_pk']] = _item['latest']

                        deleted_items = list()
                        for _d_id in deleted_dict.keys():
                            if _d_id in restored_dict:  # Check if item was restored
                                if deleted_dict[_d_id] > restored_dict[
                                    _d_id]:  # Check if item was delete again after restoration
                                    deleted_items.append(_d_id)
                            else:
                                deleted_items.append(_d_id)

                        data[status_key]['deleted'] = deleted_items
                        CacheManager.set_cache_element_by_key(DELETED_LIST_PREFIX + status_key, deleted_items,
                                                              ONE_MONTH_TIMEOUT)

                        _max_delete = \
                            DeleteLog.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                                model_name__in=self.get_candidate_model_names(m)).aggregate(
                                last_updated=Max('last_updated'))[
                                'last_updated']
                        if _max_delete is None:
                            _max_delete = 0
                        if _max_delete > data[status_key]['last_updated']:
                            data[status_key]['last_updated'] = _max_delete
                            CacheManager.set_cache_element_by_key(STATUS_API_PREFIX + status_key, _max_delete,
                                                                  ONE_MONTH_TIMEOUT)
                    else:
                        data[status_key]['deleted'] = candidate_deleted_list
                except Resolver404 as exp:
                    pass

        extra_data_models = get_models_with_decorator('has_status_data', INSTALLED_APPS, include_class=True)
        for extra_model in extra_data_models:
            extra_data = extra_model.get_status_data(request=request, *args, **kwargs)
            for key, value in extra_data.items():
                data[key] = value

        logged_in_information = CacheManager.get_from_cache_by_key(USER_LOGIN_INFO_PREFIX + str(request.c_user.pk))
        if logged_in_information is None:
            data['logged_in_information'] = request.c_user.to_json()
            CacheManager.set_cache_element_by_key(USER_LOGIN_INFO_PREFIX + str(request.c_user.pk),
                                                  data['logged_in_information'],
                                                  ONE_DAY_TIMEOUT)  # Set for one day
        else:
            data['logged_in_information'] = logged_in_information

        help_info = CacheManager.get_from_cache_by_key(HELP_INFO_PREFIX + str(request.c_user.pk))
        if help_info is None:
            default_superior = {
                'name': 'Mr. Update Me',
                'phone': '+0000000000'
            }

            try:
                user_model = get_model_by_name(request.c_user.type)
                superior = user_model.get_superior(instance=request.c_user) if hasattr(user_model,
                                                                                       'get_superior') else None
            except:
                superior = None

            if superior is not None:
                default_superior = {
                    'name': superior.name,
                    'phone': superior.phones.first().phone
                }
            data['help_info'] = {
                'helpdesk': '',
                'supervisor': default_superior
            }
            CacheManager.set_cache_element_by_key(HELP_INFO_PREFIX + str(request.c_user.pk), data['help_info'],
                                                  ONE_DAY_TIMEOUT)  # set for one day
        else:
            data['help_info'] = help_info

        return Response({'data': data, 'success': True})
