from django.shortcuts import get_object_or_404
from rest_framework import permissions
from .models import Calendar, World


class IsCreatorOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user or obj.public


class IsWorldCreatorOrPublic(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            if 'world' not in request.data:
                return False
            world = get_object_or_404(World, pk=request.data['world'])
            return world.creator == request.user or world.public
        else:
            return True  # has_object_permission will handle creator check for other actions

    def has_object_permission(self, request, view, obj):
        return obj.world.creator == request.user or obj.world.public


class IsCalendarWorldCreatorOrPublic(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            if 'calendar' not in request.data:
                return False
            calendar = get_object_or_404(Calendar, pk=request.data['calendar'])
            return calendar.world.creator == request.user or calendar.world.public
        else:
            return True  # has_object_permission will handle creator check for other actions

    def has_object_permission(self, request, view, obj):
        return obj.calendar.world.creator == request.user or obj.calendar.world.public


class IsCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class IsWorldCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            if 'world' not in request.data:
                return False
            world = get_object_or_404(World, pk=request.data['world'])
            return world.creator == request.user
        else:
            return True  # has_object_permission will handle creator check for other actions

    def has_object_permission(self, request, view, obj):
        return obj.world.creator == request.user


class IsCalendarWorldCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            if 'calendar' not in request.data:
                return False
            calendar = get_object_or_404(Calendar, pk=request.data['calendar'])
            return calendar.world.creator == request.user
        else:
            return True  # has_object_permission will handle creator check for other actions

    def has_object_permission(self, request, view, obj):
        return obj.calendar.world.creator == request.user
