from django.db.models import Q
from rest_framework import serializers
from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig, DateBookmark, DisplayUnitConfig


class WorldSerializer(serializers.ModelSerializer):
    class Meta:
        model = World
        fields = ('id', 'creator', 'world_name', 'public')


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ('id', 'world', 'calendar_name', 'default_display_config')


class TimeUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeUnit
        fields = ('id', 'calendar', 'time_unit_name', 'base_unit', 'length_cycle', 'base_unit_instance_names',
                  'default_date_format', 'secondary_date_format')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'calendar', 'event_name', 'event_description', 'bottom_level_iteration')


class DateFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateFormat
        fields = ('id', 'calendar', 'time_unit', 'date_format_name', 'format_string')


class DisplayUnitConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayUnitConfig
        fields = ('id', 'time_unit', 'sub_unit', 'search_type', 'searchable_date_formats', 'header_display_name_type',
                  'header_other_date_format', 'sub_unit_display_name_type', 'sub_unit_other_date_format',
                  'row_grouping_time_unit', 'row_grouping_label_type', 'show_events', 'max_events_per_instance',
                  'show_linked_instance_display_names', 'show_linked_instance_events')


class DisplayConfigSerializer(serializers.ModelSerializer):
    display_unit_configs = DisplayUnitConfigSerializer(source='displayunitconfig_set', many=True)

    class Meta:
        model = DisplayConfig
        fields = ('id', 'calendar', 'display_config_name', 'default_display_unit_config', 'default_date_bookmark',
                  'display_unit_configs')


class DateBookmarkSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField('get_display_name')
    from_event = serializers.SerializerMethodField('get_from_event')

    def get_display_name(self, date_bookmark):
        return date_bookmark.get_display_name()

    def get_from_event(self, date_bookmark):
        return date_bookmark.id < 0  # may be a cleaner way to do this but this works for now

    class Meta:
        model = DateBookmark
        fields = ('id', 'calendar', 'date_bookmark_name', 'bookmark_unit', 'bookmark_iteration', 'bookmark_sub_unit',
                  'display_name', 'personal_bookmark_creator', 'from_event')


class DateBookmarkPersonalSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField('get_display_name')

    def get_display_name(self, date_bookmark):
        return date_bookmark.get_display_name()

    class Meta:
        model = DateBookmark
        fields = ('id', 'calendar', 'date_bookmark_name', 'bookmark_unit', 'bookmark_iteration', 'bookmark_sub_unit',
                  'display_name', 'personal_bookmark_creator')


class CalendarDetailSerializer(serializers.ModelSerializer):
    time_units = TimeUnitSerializer(source='timeunit_set', many=True)
    date_bookmarks = serializers.SerializerMethodField('get_date_bookmarks')

    def get_date_bookmarks(self, calendar):
        date_bookmarks = DateBookmark.objects.filter(calendar_id=calendar.pk)
        bookmark_serializer = DateBookmarkSerializer(instance=date_bookmarks, many=True)
        bookmark_data = list(bookmark_serializer.data)
        events = Event.objects.filter(calendar_id=calendar.pk).filter(
            Q(navigable=True) | Q(navigable=None, event_group__isnull=False, event_group__navigable=True))
        fake_id = -11
        for event in events:
            event_bookmark = DateBookmark(id=fake_id, calendar=calendar, date_bookmark_name=str(event),
                                          bookmark_unit=calendar.get_bottom_level_time_unit(),
                                          bookmark_iteration=event.bottom_level_iteration,
                                          bookmark_sub_unit=None)
            fake_id -= 1
            event_serializer = DateBookmarkSerializer(instance=event_bookmark, many=False)
            bookmark_data = bookmark_data + [event_serializer.data] if bookmark_data is not None \
                else event_serializer.data
        return bookmark_data

    class Meta:
        model = Calendar
        fields = ('id', 'world', 'calendar_name', 'default_display_config', 'time_units', 'date_bookmarks')
