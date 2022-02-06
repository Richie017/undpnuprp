from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import NoReverseMatch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager


class GenericCreateView(ProtectedViewMixin, CreateView):
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
            if not BWPermissionManager.has_create_permission(self.request, self.model):
                raise NotEnoughPermissionException("You do not have enough permission to create this item.")
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        self.object = None
        form = self.get_form(self.get_form_class())
        try:
            if form.is_valid():
                result = self.form_valid(form)
                messages.success(request, bw_titleize(self.model_name) + ' added successfully.')
                return result
            else:
                message = "Please fix the following error before continuing."
                if '__all__' in form.errors:
                    message += str(form.errors['__all__'])
                messages.error(request, message)
        except NoReverseMatch:
            return self.form_valid(form)
        except Exception as err:
            messages.error(request, str(err))
            ErrorLog.log(err)
        return self.form_invalid(form)
