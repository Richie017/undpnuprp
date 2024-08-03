from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import DeleteView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.log.audit_log import DeletedEntityEnum
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException, EntityNotDeletableException
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager


class GenericDeleteView(ProtectedViewMixin, DeleteView):
    def get_template_names(self):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        return [self.model_name + '/delete.html', 'shared/display-templates/delete.html']

    @method_decorator(login_required)
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        if self.model is not None:
            if not BWPermissionManager.has_delete_permission(self.request, self.model):
                raise NotEnoughPermissionException("You do not have enough permission to delete this item.")
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        models = None
        if kwargs.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        if request.GET.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        hard_delete = False
        is_reffered = True
        if int(request.GET.get('hard_delete', '0')) > 0:
            hard_delete = True

        if models is None:
            if self.is_json_request(request) or request.is_ajax():
                return self.render_json_response({
                    'message': 'Nothing to delete.',
                    'success': False,
                    'load': 'ajax'
                })
            messages.warning(request, 'Nothing to delete.')
            return redirect(self.get_success_url())
        else:
            decorators = self.model._decorators
            for decorator in decorators:
                name = decorator.__name__
                if decorator.__name__ == 'direct_delete':
                    hard_delete = True
                    is_reffered = False
                    break

        if request.GET.get('force_delete', '') == 'True':
            try:
                for m in models:
                    if hard_delete:
                        if not self.request.c_user.is_super:
                            raise NotEnoughPermissionException('Only super-user can delete data permanently.')
                        if not is_reffered:
                            m.delete(user=request.c_user, force_delete=True)
                        else:
                            model_name = m.model_name
                            model_pk = m.model_pk
                            z = ContentType.objects.get(model=model_name.lower())
                            ModelName = apps.get_model(z.app_label, model_name)
                            obj = ModelName.objects.get(pk=model_pk)
                            obj.delete(user=request.c_user, force_delete=True)

                            m.deleted_status = DeletedEntityEnum.HardDeleted.value
                            m.save()
                    else:
                        m.soft_delete(user=request.c_user, force_delete=True)
            except Exception as exp:
                messages.error(request, str(exp))
                return redirect(self.get_success_url())
        else:
            try:
                for m in models:
                    if hard_delete:
                        if not self.request.c_user.is_super:
                            raise NotEnoughPermissionException('Only super-user can delete data permanently.')
                        if is_reffered:
                            model_name = m.model_name
                            model_pk = m.model_pk
                            z = ContentType.objects.get(model=model_name.lower())
                            ModelName = apps.get_model(z.app_label, model_name)
                            obj = ModelName.objects.get(pk=model_pk)
                            obj.delete(user=request.c_user)

                            m.deleted_status = DeletedEntityEnum.HardDeleted.value
                            m.save()
                        else:
                            m.delete(user=request.c_user)
                    else:
                        m.soft_delete(user=request.c_user)
            except EntityNotDeletableException as exp:
                # Uncomment the following line to give "Force Delete" access only to admin
                # if request.c_user.is_super is True:
                from_url = str(request.build_absolute_uri())
                if '?' in from_url:
                    to_url = from_url + '&force_delete=True'
                else:
                    to_url = from_url + '/?force_delete=True'
                messages.error(request, str(exp) + str(mark_safe(
                    '<br/><strong><a class="btn btn-small btn-danger" href="' + to_url + '">Continue remove anyway?</a></strong>')))

                # Uncomment the following line to give "Force Delete" access only to admin
                # else:
                #     messages.error(request, str(exp))
                return redirect(self.get_success_url())
            except Exception as exp:
                messages.error(request, str(exp))
                return redirect(self.get_success_url())

        model_name = bw_titleize(
            self.model_name.title()) if self.model_name and self.model_name != '' else self.model.__name__.title()

        if self.is_json_request(request) or request.is_ajax():
            return self.render_json_response({
                'message': model_name + " deleted successfully.",
                'success': True,
                'load': 'ajax',
                'success_url': self.model.success_url() if hasattr(self.model, 'success_url') else None,
            })
        messages.success(request, model_name + " deleted successfully.")
        return redirect(self.get_success_url())
