from rest_framework.permissions import SAFE_METHODS, BasePermission

from api_yamdb.roles import ROLE_ADMIN


class IsAdmin(BasePermission):
    """Пользователь - админ или суперпользователь."""
    def has_permission(self, request, view):
        result = request.user.is_superuser
        if hasattr(request.user, 'role'):
            result |= request.user.role == ROLE_ADMIN
        return result


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class AuthorAdminModerator(BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
                )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        result = request.user.is_superuser
        if hasattr(request.user, 'role'):
            result |= request.user.role == ROLE_ADMIN
        return result
