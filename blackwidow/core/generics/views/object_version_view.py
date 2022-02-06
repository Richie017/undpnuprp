from django.apps import apps
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.shortcuts import redirect

from blackwidow.core.generics.views.edit_view import GenericEditView
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager

get_model = apps.get_model


class GenericVersionActionView(GenericEditView):
    master_object = None
    version_object = None

    def load_objects(self, request=None, **kwargs):
        try:
            app_label = kwargs['app_label']
            model_name = kwargs['model']
            master_pk = int(kwargs['pk'])
            version_pk = int(kwargs['version_pk'])
            object_model = get_model(app_label, model_name)
            self.master_object = object_model.objects.get(pk=master_pk)
            self.version_object = object_model.version_objects.get(pk=version_pk)
        except:
            pass

    def get(self, request, *args, **kwargs):
        if not BWPermissionManager.has_edit_permission(self.request, self.model):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")
        self.load_objects(request=request, **kwargs)
        if self.master_object and self.version_object:
            if hasattr(self.master_object, 'restore_version'):
                self.master_object.restore_version(version_object=self.version_object, keep_version=True)
        return redirect(reverse(self.master_object.true_route_name(), kwargs={'pk':self.master_object.pk}))

    def post(self, request, *args, **kwargs):
        if not BWPermissionManager.has_edit_permission(self.request, self.model):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")
        success = False
        return JsonResponse({
            'success': success
        })
