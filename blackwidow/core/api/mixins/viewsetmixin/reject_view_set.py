from rest_framework.decorators import detail_route
from rest_framework.response import Response

__author__ = 'Sohel'

class GenericApiRejectViewSetMixin(object):
    @detail_route(methods=['get'])
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        kwargs.update({'data':request.data})
        serializer.reject(**kwargs)
        return Response(serializer.data)
