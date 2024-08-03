from rest_framework.permissions import IsAuthenticated

__author__ = 'Mahmud'


class IsAuthorized(IsAuthenticated):
    # def has_permission(self, request, view):
    #     if ~(request.user.is_anonymous()):
    #         c_user = ConsoleUser.objects.get(user=request.user)
    #         ContextManager.initialize_context(request, {'user': c_user, 'org': c_user.organization})
    #     return request.user and request.user.is_authenticated()
    pass