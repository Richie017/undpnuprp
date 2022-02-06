from django.shortcuts import redirect

import settings
from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.core.managers.contextmanager import ContextManager
from blackwidow.core.models.organizations.organization import Organization


__author__ = 'mahmudul'


class SettingsView(GenericDetailsView):
    template_name = "organization/details.html"
    model = None

    def get(self, request, *args, **kwargs):
        context = ContextManager.get_current_context(self.request)
        org = Organization.objects.filter(is_master=True)[0]
        # form.addresses = self.ContactAddressFormSetFactory(prefix='addresses')
        return redirect("/" + settings.SUB_SITE + 'clientmanagement/organizations/details/' + str(org.id))