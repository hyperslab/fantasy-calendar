from rest_framework import viewsets
from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig, DateBookmark
from .serializers import WorldSerializer, CalendarSerializer, TimeUnitSerializer, EventSerializer, \
    DateFormatSerializer, DisplayConfigSerializer, DateBookmarkSerializer


class WorldViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = World.objects.all()
    serializer_class = WorldSerializer


class CalendarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer


class TimeUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimeUnit.objects.all()
    serializer_class = TimeUnitSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class DateFormatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DateFormat.objects.all()
    serializer_class = DateFormatSerializer


class DisplayConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DisplayConfig.objects.all()
    serializer_class = DisplayConfigSerializer


class DateBookmarkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DateBookmark.objects.all()
    serializer_class = DateBookmarkSerializer
