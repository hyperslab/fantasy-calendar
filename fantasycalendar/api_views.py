from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig, DateBookmark
from .serializers import WorldSerializer, CalendarSerializer, TimeUnitSerializer, EventSerializer, \
    DateFormatSerializer, DisplayConfigSerializer, DateBookmarkSerializer
from .permissions import IsCreatorOrPublic, IsWorldCreatorOrPublic, IsCalendarWorldCreatorOrPublic, \
    IsCalendarWorldCreator


class UserStatus(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'user_status': 'unauthenticated'})
        if 'world_id' not in request.query_params and 'calendar_id' not in request.query_params:
            return Response({'user_status': 'authenticated',
                             'message': 'send world_id or calendar_id to test for creator status'})
        if 'world_id' in request.query_params:
            world_id = int(request.query_params.get('world_id'))
            world = get_object_or_404(World, pk=world_id)
            return Response({'user_status': 'creator' if world.creator == request.user else 'authenticated'})
        if 'calendar_id' in request.query_params:
            calendar_id = int(request.query_params.get('calendar_id'))
            calendar = get_object_or_404(Calendar, pk=calendar_id)
            return Response({'user_status': 'creator' if calendar.world.creator == request.user else 'authenticated'})


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
            return Response({'message': 'ERROR: time_unit_id and iteration required'},
                            status=status.HTTP_400_BAD_REQUEST)
        time_unit_id = int(request.query_params.get('time_unit_id'))
        iteration = int(request.query_params.get('iteration'))
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
        if time_unit.calendar.world.creator != request.user and not time_unit.calendar.world.public:
            return Response(
                {'message': 'ERROR: this resource is not public and you are not authenticated as its creator'},
                status=status.HTTP_403_FORBIDDEN)
        base_unit = time_unit.base_unit if time_unit.base_unit is not None else time_unit
        instances = time_unit.get_base_unit_instances(iteration=iteration)
        first_base_iteration = time_unit.get_first_base_unit_instance_iteration_at_iteration(iteration=iteration)
        data = []
        for index, instance in enumerate(instances):
            iteration = first_base_iteration + index
            events = base_unit.get_events_at_iteration(iteration)
            data.append({
                "name": instance[0],
                "display_name": instance[0] if not base_unit.secondary_date_format else
                base_unit.get_instance_display_name(iteration=iteration, prefer_secondary=True),
                "time_unit_id": base_unit.pk,
                "iteration": iteration,
                "events": EventSerializer(events, many=True).data,
            })
        return Response(data)


class TimeUnitInstanceDisplayName(APIView):
    def get(self, request):
        if 'time_unit_id' not in request.query_params or 'iteration' not in request.query_params:
            return Response({'message': 'ERROR: time_unit_id and iteration required'},
                            status=status.HTTP_400_BAD_REQUEST)
        time_unit_id = int(request.query_params.get('time_unit_id'))
        iteration = int(request.query_params.get('iteration'))
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
        if time_unit.calendar.world.creator != request.user and not time_unit.calendar.world.public:
            return Response(
                {'message': 'ERROR: this resource is not public and you are not authenticated as its creator'},
                status=status.HTTP_403_FORBIDDEN)
        date_format = None
        prefer_secondary = True if 'secondary_format' in request.query_params else False
        if 'date_format_id' in request.query_params:
            date_format_id = int(request.query_params.get('date_format_id'))
            date_format = get_object_or_404(DateFormat, pk=date_format_id)
        display_name = time_unit.get_instance_display_name(iteration=iteration, date_format=date_format,
                                                           prefer_secondary=prefer_secondary)
        return Response({'display_name': display_name})


class TimeUnitEquivalentIteration(APIView):
    def get(self, request):
        if 'time_unit_id' not in request.query_params or 'iteration' not in request.query_params or \
                'new_time_unit_id' not in request.query_params:
            return Response({'message': 'ERROR: time_unit_id and iteration and new_time_unit_id required'},
                            status=status.HTTP_400_BAD_REQUEST)
        time_unit_id = int(request.query_params.get('time_unit_id'))
        iteration = int(request.query_params.get('iteration'))
        new_time_unit_id = int(request.query_params.get('new_time_unit_id'))
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
        if time_unit.calendar.world.creator != request.user and not time_unit.calendar.world.public:
            return Response(
                {'message': 'ERROR: this resource is not public and you are not authenticated as its creator'},
                status=status.HTTP_403_FORBIDDEN)
        new_time_unit = get_object_or_404(TimeUnit, pk=new_time_unit_id)
        if time_unit.calendar != new_time_unit.calendar:
            return Response(
                {'message': 'ERROR: time_unit_id and new_time_unit_id refer to time units on different calendars'},
                status=status.HTTP_400_BAD_REQUEST)
        base_iteration = time_unit.get_first_bottom_level_iteration_at_iteration(iteration=iteration)
        new_iteration = new_time_unit.get_iteration_at_bottom_level_iteration(bottom_level_iteration=base_iteration)
        return Response({'iteration': new_iteration})


class TimeUnitContainedIteration(APIView):
    def get(self, request):
        if 'time_unit_id' not in request.query_params or 'iteration' not in request.query_params or \
                'containing_time_unit_id' not in request.query_params:
            return Response({'message': 'ERROR: time_unit_id and iteration and containing_time_unit_id required'},
                            status=status.HTTP_400_BAD_REQUEST)
        time_unit_id = int(request.query_params.get('time_unit_id'))
        iteration = int(request.query_params.get('iteration'))
        containing_time_unit_id = int(request.query_params.get('containing_time_unit_id'))
        time_unit = get_object_or_404(TimeUnit, pk=time_unit_id)
        if time_unit.calendar.world.creator != request.user and not time_unit.calendar.world.public:
            return Response(
                {'message': 'ERROR: this resource is not public and you are not authenticated as its creator'},
                status=status.HTTP_403_FORBIDDEN)
        containing_time_unit = get_object_or_404(TimeUnit, pk=containing_time_unit_id)
        if time_unit.calendar != containing_time_unit.calendar:
            return Response({'message': 'ERROR: time_unit_id and containing_time_unit_id refer to time units on '
                                        'different calendars'}, status=status.HTTP_400_BAD_REQUEST)
        contained_iteration = containing_time_unit.get_sub_unit_instance_iteration_within_higher_level_iteration(
            sub_unit=time_unit, sub_unit_iteration=iteration)
        return Response({'iteration': contained_iteration})


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


class DateFormatReverse(APIView):
    def get(self, request):
        # initial validation
        required_params = [
            'formatted_date',
            'possible_formats',
        ]
        missing_fields = [param for param in required_params if param not in request.query_params]
        if len(missing_fields) > 0:
            return Response({'message': 'ERROR: missing required fields ' + ' and '.join(missing_fields)},
                            status=status.HTTP_400_BAD_REQUEST)

        # calculation
        formatted_date = request.query_params.get('formatted_date')
        possible_format_ids = request.query_params.get('possible_formats').split(',')
        possible_formats = [get_object_or_404(DateFormat, pk=possible_id) for possible_id in possible_format_ids]
        likely_formats = DateFormat.find_likely_source_date_formats(formatted_date, possible_formats)
        if len(likely_formats) < 1:
            return Response({'message': 'no matching formats found'})
        likeliest_format = likely_formats[0]
        if not likeliest_format.is_reversible():
            return Response({'message': 'ERROR: matching format was not reversible'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            iteration = likeliest_format.get_iteration(formatted_string=formatted_date)
        except ValueError as error:
            return Response({'message': 'matching format found but parse failed: ' + str(error)})

        # response
        return Response({
            'date_format_id': likeliest_format.id,
            'time_unit_id': likeliest_format.time_unit.id,
            'iteration': iteration,
        })


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


class DateBookmarkViewSet(viewsets.ModelViewSet):
    queryset = DateBookmark.objects.all()
    serializer_class = DateBookmarkSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsCalendarWorldCreatorOrPublic]
        else:
            permission_classes = [IsCalendarWorldCreator]  # only creators can change data
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super(DateBookmarkViewSet, self).get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(calendar__world__creator_id=self.request.user.id) | \
                    queryset.filter(calendar__world__public=True)
                queryset = queryset.filter(personal_bookmark_creator=None) | \
                    queryset.filter(personal_bookmark_creator=self.request.user)
            else:
                queryset = queryset.filter(calendar__world__public=True).filter(personal_bookmark_creator=None)
            if 'bookmark_unit_id' in self.request.query_params:
                bookmark_unit_id = int(self.request.query_params.get('bookmark_unit_id'))
                queryset = queryset.filter(bookmark_unit_id=bookmark_unit_id)
            elif 'calendar_id' in self.request.query_params:
                calendar_id = int(self.request.query_params.get('calendar_id'))
                queryset = queryset.filter(calendar_id=calendar_id)
        return queryset


class DateBookmarkCreatePersonal(APIView):
    def post(self, request):
        # initial validation
        if not request.user:
            return Response({'message': 'ERROR: user is not authenticated'}, status=status.HTTP_403_FORBIDDEN)
        required_params = [
            'calendar',
            'date_bookmark_name',
            'bookmark_unit',
            'bookmark_iteration',
        ]
        missing_fields = [param for param in required_params if param not in request.data]
        if len(missing_fields) > 0:
            return Response({'message': 'ERROR: missing required fields ' + ' and '.join(missing_fields)},
                            status=status.HTTP_400_BAD_REQUEST)

        # creation
        calendar = get_object_or_404(Calendar, pk=int(request.data['calendar']))
        if not calendar.world.public and calendar.world.creator != request.user:
            return Response(
                {'message': "ERROR: this resource's world is not public and you are not authenticated as its creator"},
                status=status.HTTP_403_FORBIDDEN)
        date_bookmark_name = request.data['date_bookmark_name']
        bookmark_unit = get_object_or_404(TimeUnit, pk=int(request.data['bookmark_unit']))
        bookmark_iteration = int(request.data['bookmark_iteration'])
        bookmark = DateBookmark.objects.create(calendar=calendar, date_bookmark_name=date_bookmark_name,
                                               bookmark_unit=bookmark_unit, bookmark_iteration=bookmark_iteration,
                                               personal_bookmark_creator=request.user)

        # response
        serializer = DateBookmarkSerializer(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
