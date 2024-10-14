from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    message = 'Доступ запрещен!'

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_admin
            or request.user.is_superuser
        )


class SelfUserOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user


class AdminModeratorAuthorOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_anonymous:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderate
            or request.user.is_superuser
        )
