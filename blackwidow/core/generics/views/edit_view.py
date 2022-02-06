from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView

from blackwidow.core.managers.contextmanager import ContextManager
from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager


class GenericEditView(ProtectedViewMixin, UpdateView):
    def get_template_names(self):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        if self.get_form_class().get_template() == '':
            return [self.model.__name__.lower() + '/create.html', 'shared/display-templates/create.html']
        return [self.get_form_class().get_template(), self.model_name + '/create.html',
                'shared/display-templates/create.html']

    @method_decorator(login_required)
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        if self.model is not None:
            if not BWPermissionManager.has_edit_permission(self.request, self.model, *args, **kwargs):
                user = ContextManager.get_current_user(self.request)
                if 'pk' in kwargs and not user['id'] == int(kwargs.get("pk", "0")) \
                        and self.model.__name__ == 'ConsoleUsr':
                    raise NotEnoughPermissionException("You do not have enough permission to edit this item.")

                if 'id' in kwargs and not user['id'] == int(kwargs.get("id", "0")) \
                        and self.model.__name__ == 'ConsoleUsr':
                    raise NotEnoughPermissionException("You do not have enough permission to edit this item.")
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        try:
            if form.is_valid():
                messages.success(request, bw_titleize(self.model_name) + ' updated successfully.')
                response = self.form_valid(form)
                if hasattr(self.object, "update_parent"):
                    getattr(self.object, "update_parent")
                return response
            else:
                messages.error(request, "Please fix the following error before continuing.")
        except Exception as err:
            messages.error(request, str(err))
            ErrorLog.log(err, organization=self.request.c_user.organization)
        return self.form_invalid(form)
