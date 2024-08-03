__author__ = 'ruddra'
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import *

from blackwidow.core.forms.account.reset_password_form import PasswordResetRequestForm, SetPasswordForm
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.mixins.viewmixin.json_view_mixin import JsonMixin
from config.email_config import DEFAULT_FROM_EMAIL


class ResetPasswordRequestView(FormView, JsonMixin):
    template_name = "account/reset_password.html"
    success_url = '/account/login'
    form_class = PasswordResetRequestForm

    @staticmethod
    def validate_email_address(email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data["email_or_username"]
        if self.validate_email_address(data) is True:
            email_data = EmailAddress.objects.filter(email=data)
            if email_data.exists():
                c_users = ConsoleUser.objects.filter(emails=email_data, is_active=True)
                if c_users.exists():
                    for user in c_users:
                        if user.user:
                            c = {
                                'email': user.emails.all()[0],
                                'domain': request.META['HTTP_HOST'],
                                'site_name': 'myjita',
                                'uid': urlsafe_base64_encode(force_bytes(user.user.pk)),
                                'user': user.user,
                                'token': default_token_generator.make_token(user.user),
                                'protocol': 'http',
                            }
                            subject_template_name = 'registration/password_reset_subject.txt'
                            email_template_name = 'registration/password_reset_email.html'
                            subject = loader.render_to_string(subject_template_name, c)
                            subject = ''.join(subject.splitlines())
                            email = loader.render_to_string(email_template_name, c)
                            send_mail(subject, email, DEFAULT_FROM_EMAIL, [x.email for x in user.emails.all()],
                                      fail_silently=False)
                            result = self.form_valid(form)
                            messages.success(request,
                                             'An email has been sent to ' + data + ". Please check its inbox to continue reseting password.")
                            return result
                        result = self.form_invalid(form)
                        messages.error(request,
                                       'User associated with this email address does not have authentication privileges.')
                        return result
                else:
                    messages.error(request, 'This email has not been associated with any User of the system')
                    return self.form_invalid(form)
            else:
                messages.error(request, 'This email does not exist in the system.')
                return self.form_invalid(form)
        else:
            c_users = ConsoleUser.objects.filter(user__username=str(data), is_active=True)
            if c_users.exists():
                for user in c_users:
                    if user.user:
                        c = {
                            'email': user.emails.all()[0],
                            'domain': 'myjita.info',
                            'site_name': 'myjita',
                            'uid': urlsafe_base64_encode(force_bytes(user.user.pk)),
                            'user': user.user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                        }
                        subject_template_name = 'registration/password_reset_subject.txt'
                        email_template_name = 'registration/password_reset_email.html'
                        # send_mail("asdsad","asdasd", 'jitatest@gmail.com', ['ruddra90@gmail.com'], fail_silently=False)
                        subject = loader.render_to_string(subject_template_name, c)
                        # Email subject *must not* contain newlines
                        subject = ''.join(subject.splitlines())
                        email = loader.render_to_string(email_template_name, c)

                        send_mail(subject, email, DEFAULT_FROM_EMAIL, [x.email for x in user.emails.all()],
                                  fail_silently=False)

                        result = self.form_valid(form)
                        messages.success(request,
                                         'An email has been sent to ' + data + "'s email address. Please check its inbox to continue reseting password.")
                        return result
                    result = self.form_invalid(form)
                    messages.error(request,
                                   'User associated with this username does not have authentication privileges.')
                    return result
                else:
                    return self.form_invalid(form)
            else:
                messages.error(request, 'This username does not exist in the system.')
                return self.form_invalid(form)

        messages.error(request, 'Invalid Input')
        return self.form_invalid(form)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ResetPasswordRequestView, self).dispatch(*args, **kwargs)


class PasswordResetConfirmView(FormView, JsonMixin):
    template_name = "account/reset_password_confirm.html"
    success_url = '/account/login'
    form_class = SetPasswordForm

    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        UserModel = ConsoleUser()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user.user, token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.user.set_password(new_password)
                user.user.save()
                user.save()
                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Password reset has not been unsuccessful.')
                return self.form_invalid(form)
        else:
            messages.error(request, 'The reset password link is no longer valid.')
            return self.form_invalid(form)
