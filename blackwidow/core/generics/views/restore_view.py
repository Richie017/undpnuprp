from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import DeleteView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.log.audit_log import DeletedEntityEnum
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager

__author__="tareq"


class GenericRestoreView(ProtectedViewMixin, DeleteView):
    def get_template_names(self):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        return [self.model_name + '/restore.html', 'shared/display-templates/restore.html']

    @method_decorator(login_required)
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        if self.model is not None:
            if not BWPermissionManager.has_delete_permission(self.request, self.model):
                raise NotEnoughPermissionException("You do not have enough permission to restore this item.")
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        models = None
        if kwargs.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        if request.GET.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        if models is None:
            if self.is_json_request(request) or request.is_ajax():
                return self.render_json_response({
                    'message':  'Nothing to restore.',
                    'success': False,
                    'load': 'ajax'
                })
            messages.warning(request, 'Nothing to Restore.')
            return redirect(self.get_success_url())

        try:
            for m in models:
                try:
                    model_name = m.model_name
                    model_pk = m.model_pk
                    z = ContentType.objects.get(model=model_name.lower())
                    ModelName = apps.get_model(z.app_label, model_name)
                    obj = ModelName.all_objects.get(pk=model_pk)
                    obj.restore(user=request.c_user)

                    m.deleted_status = DeletedEntityEnum.Restored.value
                    m.save()
                except Exception as ex:
                    print (ex)
                    pass
        except Exception as exp:
            messages.error(request, str(exp))
            return redirect(self.get_success_url())

        model_name = bw_titleize(self.model_name.title()) if self.model_name and self.model_name != '' else self.model.__name__.title()

        if self.is_json_request(request) or request.is_ajax():
            return self.render_json_response({
                'message':  model_name + " restored successfully.",
                'success': True,
                'load': 'ajax'
            })
        messages.success(request, model_name + " restored successfully.")
        return redirect(self.get_success_url())





