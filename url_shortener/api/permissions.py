from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsOwnerOrForbidden(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
