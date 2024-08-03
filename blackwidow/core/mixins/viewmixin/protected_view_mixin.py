from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, NoReverseMatch
from django.shortcuts import render
from django.template.context import RequestContext
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe

from blackwidow.core.managers.contextmanager import ContextManager
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.mixins.viewmixin.protected_details_link_config_view_mixin import \
    ProtectedDetailsLinkConfigViewMixin
from blackwidow.core.mixins.viewmixin.protected_inline_manage_button_view_mixin import \
    ProtectedInlineManageButtonDecisionViewMixin
from blackwidow.core.mixins.viewmixin.protected_manage_button_view_mixin import ProtectedManageButtonViewMixin
from blackwidow.core.mixins.viewmixin.protected_queryset_mixin import ProtectedQuerySetMixin
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.pluralize import pluralize
from blackwidow.engine.mixins.viewmixin.json_view_mixin import JsonMixin
from blackwidow.engine.templatetags.blackwidow_filter import remove_quote

LANGUAGES = settings.LANGUAGES
USE_I18N = settings.USE_I18N
GOOGLE_MAP_API_KEY = settings.GOOGLE_MAP_API_KEY
GOOGLE_MAP_DEFAULT_LOCATION = settings.GOOGLE_MAP_DEFAULT_LOCATION
ENABLE_JS_MENU_RENDERING = settings.ENABLE_JS_MENU_RENDERING


class ProtectedViewMixin(ProtectedQuerySetMixin, ProtectedManageButtonViewMixin, ProtectedDetailsLinkConfigViewMixin,
                         ProtectedInlineManageButtonDecisionViewMixin, JsonMixin):
    form_class = GenericFormMixin
    model = None
    initial = None
    success_url_name = ''
    success_url = ''
    model_name = ''
    module_name = ''
    template_name = ''
    action = ViewActionEnum.Details
    object = None

    @classmethod
    def get_view_meta(cls, decorator_name, name):
        try:
            if name in cls._registry[cls.__name__][decorator_name]:
                return cls._registry[cls.__name__][decorator_name][name]
        except Exception as exp:
            if name == 'display_name':
                return bw_titleize(cls.__name__)

            if name == 'route':
                return pluralize(cls.__name__.lower())

            return None

    def get_success_url(self):
        if self.success_url != '':
            return self.success_url
        if self.object is not None:
            try:
                if hasattr(self.object, 'get_success_url'):
                    _success_url = self.object.get_success_url(request=self.request)
                    if _success_url:
                        return _success_url
            except:
                if hasattr(self.object, 'get_success_url'):
                    _success_url = self.object.get_success_url()
                    if _success_url:
                        return _success_url
            try:
                return reverse(self.success_url_name, kwargs={'pk': self.object.id})
            except NoReverseMatch:
                if self.request.is_ajax() or self.is_json_request(self.request):
                    return ''
                return reverse(self.success_url_name)
        return reverse(self.success_url_name)

    def is_json_request(self, request):
        if request.GET.get('format', 'html') == 'json' \
                or request.POST.get('format', 'html') == 'json':
            return True
        return False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    def get_urls(self, urllist, depth=0):
        urls = list()
        for entry in urllist:
            urls.append("  " * depth + entry.regex.pattern)
            if hasattr(entry, 'url_patterns'):
                urls += self.get_urls(entry.url_patterns, depth + 1)
        return urls

    def get_context_data(self, **kwargs):
        context = super(ProtectedViewMixin, self).get_context_data(**kwargs)
        n_context = ContextManager.get_current_context(self.request)
        if n_context is None and self.request.user is not None:
            c_users = ConsoleUser.objects.filter(user__id=self.request.user.id)
            if len(c_users) > 0:
                ContextManager.initialize_context(self.request, {'user': c_users[0].id})

        context['context'] = ContextManager.get_current_context(self.request)
        if self.model is not None:
            context['model_meta'] = {
                'model_name': bw_titleize(
                    self.model.__name__ if self.model_name == '' or self.model_name is None else self.model_name),
            }
        # if self.form_class is not None:
        #     context[self.form_class.__name__.lower()] = self.form_class.get_form_context()
        context['map_api_key'] = GOOGLE_MAP_API_KEY
        context['map_default_latitude'] = GOOGLE_MAP_DEFAULT_LOCATION[0]
        context['map_default_longitude'] = GOOGLE_MAP_DEFAULT_LOCATION[1]
        context['color'] = 'green'
        context['languages'] = LANGUAGES
        context['USE_I18N'] = USE_I18N
        context['enable_js_menu_rendering'] = ENABLE_JS_MENU_RENDERING
        return context

    def form_invalid(self, form):
        if self.is_json_request(self.request) or self.request.is_ajax():
            storage = messages.get_messages(self.request)
            return self.render_json_response({
                'success': False,
                'message': mark_safe(',<br/> '.join([x + ': ' + remove_quote(form.errors[x][0]) for x in form.errors]))
            })
        view_context = self.get_context_data(form=form)
        bw_context = ContextManager.get_current_context(self.request)
        _context = {
            'color': 'green',
            'form': form,
            'context': bw_context,
            'model_meta': view_context['model_meta'],
            'context_instance': RequestContext(self.request)
        }
        _context = {**_context, **view_context}  # merging two dictionary
        return render(self.request, self.get_template_names(), _context)

    def form_valid(self, form):
        result = super().form_valid(form)
        if self.is_json_request(self.request) or self.request.is_ajax():
            storage = messages.get_messages(self.request)
            storage.used = True
            return self.render_json_response({
                'success': True,
                'message': 'Operation completed successfully.',
                'load': 'ajax'
            })
        return result

    def get_prefix(self):
        return ''

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_initial(self):
        if self.initial is None:
            self.initial = {}
        return self.initial
