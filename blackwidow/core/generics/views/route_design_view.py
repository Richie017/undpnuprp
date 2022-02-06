from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.model_descriptor import get_model_by_name


class GenericRouteDesignView(ProtectedViewMixin, UpdateView):
    def get_template_names(self):
        self.model = get_model_by_name(app_label='gdfl', model_name='RouteDesign')
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        return [self.model_name + '/create.html', 'shared/display-templates/routedesign/create.html']

    @method_decorator(login_required)
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        # if self.model is not None:
        #     if not BWPermissionManager.has_edit_permission(self.request, self.model):
        #         raise NotEnoughPermissionException("You do not have enough permission to edit this item.")
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        try:
            if form.is_valid():
                messages.success(request, bw_titleize(self.model_name) + ' updated successfully.')
                return self.form_valid(form)
            else:
                messages.error(request, "Please fix the following error before continuing.")
        except Exception as err:
            messages.error(request, str(err))
            ErrorLog.log(err, organization=self.request.c_user.organization)
        return self.form_invalid(form)
