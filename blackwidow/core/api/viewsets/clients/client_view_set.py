from blackwidow.core.api.mixins.viewsetmixin.viewset_mixin import GenericApiViewSetMixin
from blackwidow.core.models.clients.client import Client

__author__ = 'Mahmud'


class ClientViewSet(GenericApiViewSetMixin):
    model = Client

