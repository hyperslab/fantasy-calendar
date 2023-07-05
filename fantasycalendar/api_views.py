from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST
from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig, DateBookmark
from .serializers import WorldSerializer, CalendarSerializer, TimeUnitSerializer, EventSerializer, \
    DateFormatSerializer, DisplayConfigSerializer, DateBookmarkSerializer


class WorldViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = World.objects.all()
    serializer_class = WorldSerializer

    def get_queryset(self):
        queryset = super(WorldViewSet, self).get_queryset()
        if 'creator_id' in self.request.query_params:
            creator_id = int(self.request.query_params.get('creator_id'))
            queryset = queryset.filter(creator_id=creator_id)
        return queryset


class CalendarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

    def get_queryset(self):
        queryset = super(CalendarViewSet, self).get_queryset()
        if 'world_id' in self.request.query_params:
            world_id = int(self.request.query_params.get('world_id'))
            queryset = queryset.filter(world_id=world_id)
        return queryset


class TimeUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimeUnit.objects.all()
    serializer_class = TimeUnitSerializer

    def get_queryset(self):
        queryset = super(TimeUnitViewSet, self).get_queryset()
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
        instances = time_unit.get_base_unit_instances(iteration=iteration)
        first_base_iteration = time_unit.get_first_base_unit_instance_iteration_at_iteration(iteration=iteration)
        data = []
        for index, instance in enumerate(instances):
            data.append({
                "name": instance[0],
                "time_unit_id": time_unit.base_unit.pk if time_unit.base_unit is not None else time_unit.pk,
                "iteration": first_base_iteration + index,
            })
        return Response(data)


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        if 'time_unit_id' in self.request.query_params and 'iteration' in self.request.query_params:
            time_unit_id = int(self.request.query_params.get('time_unit_id'))
            iteration = int(self.request.query_params.get('iteration'))
            time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
            events = time_unit.get_events_at_iteration(iteration)
            return events
        else:
            queryset = super(EventViewSet, self).get_queryset()
            if 'calendar_id' in self.request.query_params:
                calendar_id = int(self.request.query_params.get('calendar_id'))
                queryset = queryset.filter(calendar_id=calendar_id)
            return queryset


class DateFormatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DateFormat.objects.all()
    serializer_class = DateFormatSerializer

    def get_queryset(self):
        queryset = super(DateFormatViewSet, self).get_queryset()
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

    def get_queryset(self):
        queryset = super(DisplayConfigViewSet, self).get_queryset()
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

    def get_queryset(self):
        queryset = super(DateBookmarkViewSet, self).get_queryset()
        if 'bookmark_unit_id' in self.request.query_params:
            bookmark_unit_id = int(self.request.query_params.get('bookmark_unit_id'))
            queryset = queryset.filter(bookmark_unit_id=bookmark_unit_id)
        elif 'calendar_id' in self.request.query_params:
            calendar_id = int(self.request.query_params.get('calendar_id'))
            queryset = queryset.filter(calendar_id=calendar_id)
        return queryset
