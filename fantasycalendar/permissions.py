from rest_framework import permissions


class IsCreatorOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user or obj.public


class IsWorldCreatorOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.world.creator == request.user or obj.world.public


class IsCalendarWorldCreatorOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.calendar.world.creator == request.user or obj.calendar.world.public
