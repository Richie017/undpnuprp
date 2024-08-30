from rest_framework.decorators import action
from rest_framework.response import Response


class GenericApiMutableViewSetMixin(object):
    @action(detail=True, methods=['get'])
    def mutate(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.mutate()
        return Response(serializer.data)