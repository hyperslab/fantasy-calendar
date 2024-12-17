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
        fields = ('id', 'time_unit', 'search_type', 'searchable_date_formats', 'header_display_name_type',
                  'header_other_date_format', 'base_unit_display_name_type', 'base_unit_other_date_format',
                  'row_grouping_time_unit', 'row_grouping_label_type', 'show_events', 'max_events_per_instance',
                  'show_linked_instance_display_names')


class DisplayConfigSerializer(serializers.ModelSerializer):
    display_unit_configs = DisplayUnitConfigSerializer(source='displayunitconfig_set', many=True)

    class Meta:
        model = DisplayConfig
        fields = ('id', 'calendar', 'display_config_name', 'display_unit', 'nest_level', 'default_date_bookmark',
                  'display_unit_configs')


class DateBookmarkSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField('get_display_name')

    def get_display_name(self, date_bookmark):
        return date_bookmark.get_display_name()

    class Meta:
        model = DateBookmark
        fields = ('id', 'calendar', 'date_bookmark_name', 'bookmark_unit', 'bookmark_iteration', 'display_name',
                  'personal_bookmark_creator')


class DateBookmarkPersonalSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField('get_display_name')

    def get_display_name(self, date_bookmark):
        return date_bookmark.get_display_name()

    class Meta:
        model = DateBookmark
        fields = ('id', 'calendar', 'date_bookmark_name', 'bookmark_unit', 'bookmark_iteration', 'display_name',
                  'personal_bookmark_creator')


class CalendarDetailSerializer(serializers.ModelSerializer):
    time_units = TimeUnitSerializer(source='timeunit_set', many=True)
    date_bookmarks = DateBookmarkSerializer(source='datebookmark_set', many=True)

    class Meta:
        model = Calendar
        fields = ('id', 'world', 'calendar_name', 'default_display_config', 'time_units', 'date_bookmarks')
