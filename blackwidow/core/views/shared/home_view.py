from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.users.user import ConsoleUser

__author__ = 'mahmudul'


class HomeView(ProtectedViewMixin, TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        users = ConsoleUser.objects.filter()[:10]
        # if BWPermissionManager.has_view_permission(self.request, ConsoleUser):
            # context['users'] = ConsoleUserTable(users)
        return context

    def get(self, request, *args, **kwargs):
        try:
            return redirect(request.user.consoleuser.role.landing_url)
        except:
            return redirect('/reports/dashboard')
