from rest_framework.decorators import detail_route
from rest_framework.response import Response

__author__ = 'Sohel'

class GenericApiApproveViewSetMixin(object):
    @detail_route(methods=['GET','POST'])
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        kwargs.update({'data': request.data})
        updated_instance = serializer.approve(**kwargs)
        serializer = self.get_serializer(updated_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
