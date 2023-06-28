from rest_framework import serializers
from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig, DateBookmark


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
                  'default_date_format')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'calendar', 'event_name', 'event_description', 'bottom_level_iteration')


class DateFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateFormat
        fields = ('id', 'calendar', 'time_unit', 'date_format_name', 'format_string')


class DisplayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayConfig
        fields = ('id', 'calendar', 'display_config_name', 'display_unit', 'nest_level', 'default_date_bookmark')


class DateBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateBookmark
        fields = ('id', 'calendar', 'date_bookmark_name', 'bookmark_unit', 'bookmark_iteration')
