import hashlib
import os
import re

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.template.context import RequestContext
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from blackwidow.core.managers.contextmanager import ContextManager
from blackwidow.core.models.users.settings.user_settings import TimeZoneSettingsItem
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.exceptions.exceptions import BWException
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.mixins.viewmixin.json_view_mixin import JsonMixin
from blackwidow.engine.templatetags.blackwidow_filter import remove_quote
from settings import PROJECT_PATH, STATIC_UPLOAD_ROOT

__author__ = 'mahmudul'

from django.views.generic import *
from django.shortcuts import render, redirect
from blackwidow.core.forms.account.login_form import LoginForm
from blackwidow.core.models.common.sessionkey import SessionKey


class LoginView(FormView, JsonMixin):
    template_name = "account/login.html"
    success_url = '/administration/'
    form_class = LoginForm

    def get_success_url(self):
        success_url = self.request.POST.get('next') or self.request.GET.get('next')
        if not success_url:
            success_url = '/'
        return success_url

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        context = super(LoginView, self).get_context_data(**kwargs)
        context['color'] = 'green'
        return context

    def form_invalid(self, form):
        if self.is_json_request(self.request) or self.request.is_ajax():
            storage = messages.get_messages(self.request)
            return self.render_json_response({
                'success': False,
                'message': mark_safe(', '.join([remove_quote(x.message) for x in storage]))
            })
        bw_context = ContextManager.get_current_context(self.request)
        return render(self.request, self.get_template_names(), {
            'color': 'green',
            'form': form,
            'context': bw_context,
            'context_instance': RequestContext(self.request)
        })

    def form_valid(self, form, **kwargs):
        c_user = kwargs.pop('user')

        # TODO timezone should be stored in Redis cache
        TimeZoneSettingsItem.cache_user_timezone_offset(user_id=c_user.id)
        # timezone_setting, result = TimeZoneSettingsItem.objects.get_or_create(organization=c_user.organization)
        # if result:
        #     timezone_setting.save()
        #
        # if c_user.settings_value.filter(settings_item=timezone_setting).exists():
        #     if c_user.settings_value.filter(settings_item=timezone_setting).count() > 1:
        #         user_tz_settings = c_user.settings_value.filter(settings_item=timezone_setting).last()
        #     else:
        #         user_tz_settings = c_user.settings_value.get(settings_item=timezone_setting)
        #     user_tz_settings.value = int(form.cleaned_data['timezone'] if (
        #             'timezone' in form.cleaned_data and form.cleaned_data['timezone'] != '') else '0')
        #     user_tz_settings.save()
        #     TimeZoneSettingsItem.cache_user_timezone_offset(user_id=c_user.id, offset_value=user_tz_settings.value)
        # else:
        #     tz_settings_value = SettingsItemValue.objects.create(organization=c_user.organization,
        #                                                          settings_item=timezone_setting, value=int(
        #             form.cleaned_data['timezone'] if form.cleaned_data['timezone'] is not None and form.cleaned_data[
        #                 'timezone'] != '' else '0'))
        #     c_user.settings_value.add(tz_settings_value)
        #     TimeZoneSettingsItem.cache_user_timezone_offset(user_id=c_user.id, offset_value=tz_settings_value.value)
        session_key = hashlib.md5(str(Clock.timestamp()).encode('utf-8')).hexdigest()
        # sskey = SessionKey()
        # sskey.ses_key = session_key
        # sskey.organization = c_user.organization
        # sskey.user = c_user
        # sskey.save()

        data = self.build_json_message(
            'Logged in successfully. Please save the session key and append to all requests to use the api.', [], True,
            {'authkey': session_key})
        data['id'] = c_user.id
        data['role_id'] = c_user.role.id
        data['role_name'] = c_user.role.name
        if c_user.assigned_to is not None:
            data['hub'] = c_user.assigned_to.pk
        else:
            data['hub'] = ''
        if c_user.image is not None:
            data['image'] = '/static_media/uploads' + os.sep + c_user.image.file.name.replace(
                os.path.join(PROJECT_PATH, STATIC_UPLOAD_ROOT), '')
        else:
            data['image'] = ''
        result = super().form_valid(form)
        if self.is_json_request(self.request) or self.request.is_ajax():
            storage = messages.get_messages(self.request)
            storage.used = True
            return self.render_json_response(data)
        return result

    def get(self, request, *args, **kwargs):
        has_json_next = bool(re.search(r'(\?|&)format=json', self.request.GET.get('next', '')))
        if self.is_json_request(request) or self.request.is_ajax() \
                or has_json_next:
            data = {"success": True,
                    "message": "Please provide username and password to login"}
            if has_json_next:
                data["message"] = "Your session has expired. Please re-login to get new session"
            return self.render_json_response(data)
        if hasattr(request, 'user') and request.user and request.user.is_authenticated():
            return redirect(self.get_success_url())
        form = self.form_class()
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                if form.authenticate(request):
                    users = User.objects.filter(username=form.cleaned_data['username'])
                    if len(users) > 0:
                        c_users = ConsoleUser.objects.filter(user=users[0], is_deleted=False, is_active=True)
                        if c_users.exists():
                            c_user = c_users[0]
                            # sessions = SessionKey.objects.filter(user=c_user, organization=c_user.organization,
                            #                                      is_active=True, is_deleted=False)
                            # if len(sessions) > 0:
                            #     for s in sessions:
                            #         s.is_active = False
                            #         s.is_deleted = True
                            #         s.save()
                        else:
                            logout(request)
                            request.session.flush()
                            raise BWException('Your account has been disabled')
                    else:
                        raise BWException("User not found")
                    return self.form_valid(form, user=c_user)
            except Exception as exp:
                logout(request)
                request.session.flush()
                messages.error(self.request, str(exp))
        return self.form_invalid(form)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)


    
