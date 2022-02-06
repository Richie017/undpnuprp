from django.http.response import JsonResponse

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.dbmediabackup.models.backup_task_queue import DBMediaBackupTaskQueue
from blackwidow.dbmediabackup.utils.serialize import obj_serialize
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions import NotEnoughPermissionException

__author__ = 'Ziaul Haque'


@decorate(override_view(model=DBMediaBackupTaskQueue, view=ViewActionEnum.Manage))
class DBMediaBackupTaskQueueView(GenericListView):
    def get_template_names(self):
        return ['_backup_list_view.html']

    def get(self, request, *args, **kwargs):
        if not request.c_user.is_super:
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")
        try:
            if request.GET.get('dbbackup', 'False') == 'True':
                DBMediaBackupTaskQueue.create_backup_task_queue()
                return JsonResponse({
                    'success': 'true'
                })
            else:
                return super(DBMediaBackupTaskQueueView, self).get(request, *args, **kwargs)
        except Exception as exp:
            return JsonResponse({
                'success': False,
                'error': exp
            })

    def get_context_data(self, **kwargs):
        context = super(DBMediaBackupTaskQueueView, self).get_context_data(**kwargs)
        all_objects = DBMediaBackupTaskQueue.objects.filter(is_deleted=False).order_by('-date_created')
        context['backup_objects'] = list(map(obj_serialize, all_objects))
        return context
