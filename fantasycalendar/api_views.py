from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig, DateBookmark
from .serializers import WorldSerializer, CalendarSerializer, TimeUnitSerializer, EventSerializer, \
    DateFormatSerializer, DisplayConfigSerializer, DateBookmarkSerializer
from .permissions import IsCreatorOrPublic, IsWorldCreatorOrPublic, IsCalendarWorldCreatorOrPublic


class WorldViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = World.objects.all()
    serializer_class = WorldSerializer
    permission_classes = [IsCreatorOrPublic]

    def get_queryset(self):
        queryset = super(WorldViewSet, self).get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(creator_id=self.request.user.id) | queryset.filter(public=True)
            else:
                queryset = queryset.filter(public=True)
            if 'creator_id' in self.request.query_params:
                creator_id = int(self.request.query_params.get('creator_id'))
                queryset = queryset.filter(creator_id=creator_id)
        return queryset


class CalendarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsWorldCreatorOrPublic]

    def get_queryset(self):
        queryset = super(CalendarViewSet, self).get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(world__creator_id=self.request.user.id) | queryset.filter(world__public=True)
            else:
                queryset = queryset.filter(world__public=True)
            if 'world_id' in self.request.query_params:
                world_id = int(self.request.query_params.get('world_id'))
                queryset = queryset.filter(world_id=world_id)
        return queryset


class TimeUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimeUnit.objects.all()
    serializer_class = TimeUnitSerializer
    permission_classes = [IsCalendarWorldCreatorOrPublic]

    def get_queryset(self):
        queryset = super(TimeUnitViewSet, self).get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(calendar__world__creator_id=self.request.user.id) | \
                           queryset.filter(calendar__world__public=True)
            else:
                queryset = queryset.filter(calendar__world__public=True)
            if 'calendar_id' in self.request.query_params:
                calendar_id = int(self.request.query_params.get('calendar_id'))
                queryset = queryset.filter(calendar_id=calendar_id)
        return queryset


class TimeUnitBaseInstances(APIView):
    def get(self, request):
        if 'time_unit_id' not in request.query_params or 'iteration' not in request.query_params:
            return Response({'message': 'ERROR: time_unit_id and iteration required'}, status=HTTP_400_BAD_REQUEST)
        time_unit_id = int(request.query_params.get('time_unit_id'))
        iteration = int(request.query_params.get('iteration'))
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
        if time_unit.calendar.world.creator != request.user and not time_unit.calendar.world.public:
            return Response(
                {'message': 'ERROR: this resource is not public and you are not authenticated as its creator'},
                status=HTTP_403_FORBIDDEN)
        base_unit = time_unit.base_unit if time_unit.base_unit is not None else time_unit
        instances = time_unit.get_base_unit_instances(iteration=iteration)
        first_base_iteration = time_unit.get_first_base_unit_instance_iteration_at_iteration(iteration=iteration)
        data = []
        for index, instance in enumerate(instances):
            iteration = first_base_iteration + index
            events = base_unit.get_events_at_iteration(iteration)
            data.append({
                "name": instance[0],
                "time_unit_id": base_unit.pk,
                "iteration": iteration,
                "events": EventSerializer(events, many=True).data,
            })
        return Response(data)


class TimeUnitInstanceDisplayName(APIView):
    def get(self, request):
        if 'time_unit_id' not in request.query_params or 'iteration' not in request.query_params:
            return Response({'message': 'ERROR: time_unit_id and iteration required'}, status=HTTP_400_BAD_REQUEST)
        time_unit_id = int(request.query_params.get('time_unit_id'))
        iteration = int(request.query_params.get('iteration'))
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
        if time_unit.calendar.world.creator != request.user and not time_unit.calendar.world.public:
            return Response(
                {'message': 'ERROR: this resource is not public and you are not authenticated as its creator'},
                status=HTTP_403_FORBIDDEN)
        date_format = time_unit.default_date_format
        if 'date_format_id' in request.query_params:
            date_format_id = int(request.query_params.get('date_format_id'))
            date_format = get_object_or_404(DateFormat, pk=date_format_id)
        display_name = time_unit.get_instance_display_name(iteration=iteration, date_format=date_format)
        return Response({'display_name': display_name})


class TimeUnitEquivalentIteration(APIView):
    def get(self, request):
        if 'time_unit_id' not in request.query_params or 'iteration' not in request.query_params or \
                'new_time_unit_id' not in request.query_params:
            return Response({'message': 'ERROR: time_unit_id and iteration and new_time_unit_id required'}, status=HTTP_400_BAD_REQUEST)
        time_unit_id = int(request.query_params.get('time_unit_id'))
        iteration = int(request.query_params.get('iteration'))
        new_time_unit_id = int(request.query_params.get('new_time_unit_id'))
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
        if time_unit.calendar.world.creator != request.user and not time_unit.calendar.world.public:
            return Response(
                {'message': 'ERROR: this resource is not public and you are not authenticated as its creator'},
                status=HTTP_403_FORBIDDEN)
        new_time_unit = get_object_or_404(TimeUnit, pk=new_time_unit_id)
        if time_unit.calendar != new_time_unit.calendar:
            return Response(
                {'message': 'ERROR: time_unit_id and new_time_unit_id refer to time units on different calendars'},
                status=HTTP_400_BAD_REQUEST)
        base_iteration = time_unit.get_first_bottom_level_iteration_at_iteration(iteration=iteration)
        new_iteration = new_time_unit.get_iteration_at_bottom_level_iteration(bottom_level_iteration=base_iteration)
        return Response({'iteration': new_iteration})


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsCalendarWorldCreatorOrPublic]

    def get_queryset(self):
        if self.action != 'list':
            return super(EventViewSet, self).get_queryset()
        if 'time_unit_id' in self.request.query_params and 'iteration' in self.request.query_params:
            time_unit_id = int(self.request.query_params.get('time_unit_id'))
            iteration = int(self.request.query_params.get('iteration'))
            time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
            if not time_unit.calendar.world.public and self.request.user != time_unit.calendar.world.creator:
                return []
            events = time_unit.get_events_at_iteration(iteration)
            return events
        else:
            queryset = super(EventViewSet, self).get_queryset()
            if self.request.user.is_authenticated:
                queryset = queryset.filter(calendar__world__creator_id=self.request.user.id) | \
                           queryset.filter(calendar__world__public=True)
            else:
                queryset = queryset.filter(calendar__world__public=True)
            if 'calendar_id' in self.request.query_params:
                calendar_id = int(self.request.query_params.get('calendar_id'))
                queryset = queryset.filter(calendar_id=calendar_id)
            return queryset


class DateFormatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DateFormat.objects.all()
    serializer_class = DateFormatSerializer
    permission_classes = [IsCalendarWorldCreatorOrPublic]

    def get_queryset(self):
        queryset = super(DateFormatViewSet, self).get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(calendar__world__creator_id=self.request.user.id) | \
                           queryset.filter(calendar__world__public=True)
            else:
                queryset = queryset.filter(calendar__world__public=True)
            if 'time_unit_id' in self.request.query_params:
                time_unit_id = int(self.request.query_params.get('time_unit_id'))
                queryset = queryset.filter(time_unit_id=time_unit_id)
            elif 'calendar_id' in self.request.query_params:
                calendar_id = int(self.request.query_params.get('calendar_id'))
                queryset = queryset.filter(calendar_id=calendar_id)
        return queryset


class DisplayConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DisplayConfig.objects.all()
    serializer_class = DisplayConfigSerializer
    permission_classes = [IsCalendarWorldCreatorOrPublic]

    def get_queryset(self):
        queryset = super(DisplayConfigViewSet, self).get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(calendar__world__creator_id=self.request.user.id) | \
                           queryset.filter(calendar__world__public=True)
            else:
                queryset = queryset.filter(calendar__world__public=True)
            if 'display_unit_id' in self.request.query_params:
                display_unit_id = int(self.request.query_params.get('display_unit_id'))
                queryset = queryset.filter(display_unit_id=display_unit_id)
            elif 'calendar_id' in self.request.query_params:
                calendar_id = int(self.request.query_params.get('calendar_id'))
                queryset = queryset.filter(calendar_id=calendar_id)
        return queryset


class DateBookmarkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DateBookmark.objects.all()
    serializer_class = DateBookmarkSerializer
    permission_classes = [IsCalendarWorldCreatorOrPublic]

    def get_queryset(self):
        queryset = super(DateBookmarkViewSet, self).get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(calendar__world__creator_id=self.request.user.id) | \
                           queryset.filter(calendar__world__public=True)
            else:
                queryset = queryset.filter(calendar__world__public=True)
            if 'bookmark_unit_id' in self.request.query_params:
                bookmark_unit_id = int(self.request.query_params.get('bookmark_unit_id'))
                queryset = queryset.filter(bookmark_unit_id=bookmark_unit_id)
            elif 'calendar_id' in self.request.query_params:
                calendar_id = int(self.request.query_params.get('calendar_id'))
                queryset = queryset.filter(calendar_id=calendar_id)
        return queryset
