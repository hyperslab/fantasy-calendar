from django.test import TestCase
from .models import TimeUnit, Calendar, World


class TimeUnitModelTests(TestCase):
    def test_is_bottom_level_with_no_base_unit(self):
        """
        is_bottom_level() returns True for time units that do not have
        a base_unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(bottom_level_time_unit.is_bottom_level(), True)

    def test_is_bottom_level_with_base_unit(self):
        """
        is_bottom_level() returns False for time units that do have a
        base_unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(higher_level_time_unit.is_bottom_level(), False)

    def test_is_top_level_with_no_other_base_unit_as_self(self):
        """
        is_top_level() returns True for time units that are not set as
        the base_unit of any other time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(higher_level_time_unit.is_top_level(), True)

    def test_is_top_level_with_other_base_unit_as_self(self):
        """
        is_top_level() returns False for time units that are set as the
        base_unit of another time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(bottom_level_time_unit.is_top_level(), False)

    def test_is_top_level_with_middle_of_three_units(self):
        """
        is_top_level() returns False for a time unit that has another
        time unit as its base_unit when there are other time units that
        have it set as their base_unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        even_higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=higher_level_time_unit)
        self.assertIs(higher_level_time_unit.is_top_level(), False)

    def test_get_level_depth_with_bottom_level_unit(self):
        """
        get_level_depth() returns 1 for bottom level time units.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(bottom_level_time_unit.get_level_depth(), 1)

    def test_get_level_depth_with_unit_one_level_higher(self):
        """
        get_level_depth() returns 2 for units one level above the
        bottom.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(higher_level_time_unit.get_level_depth(), 2)

    def test_get_level_depth_with_unit_two_levels_higher(self):
        """
        get_level_depth() returns 3 for units two levels above the
        bottom.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        even_higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=higher_level_time_unit)
        self.assertIs(even_higher_level_time_unit.get_level_depth(), 3)

    def test_is_highest_level_with_single_unit(self):
        """
        is_highest_level() returns True for the only time unit in a
        calendar.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        only_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        self.assertIs(only_level_time_unit.is_highest_level(), True)

    def test_is_highest_level_with_lower_of_two_units(self):
        """
        is_highest_level() returns False for a time unit that is set as
        the base_unit of another time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(bottom_level_time_unit.is_highest_level(), False)

    def test_is_highest_level_with_higher_of_two_units(self):
        """
        is_highest_level() returns True for a time unit that has
        another time unit as its base_unit when there are also no other
        time units that have it set as their base_unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(higher_level_time_unit.is_highest_level(), True)

    def test_is_highest_level_with_middle_of_three_units(self):
        """
        is_highest_level() returns False for a time unit that has
        another time unit as its base_unit when there are other time
        units that have it set as their base_unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        even_higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=higher_level_time_unit)
        self.assertIs(higher_level_time_unit.is_highest_level(), False)

    def test_is_highest_level_with_top_level_but_not_highest_level_unit(self):
        """
        is_highest_level() returns False for a time unit that has no
        other time units that have it set as their base_unit when there
        are other time units in the same calendar in a different
        "branch" that have a higher level of depth.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        higher_level_time_unit_2 = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        highest_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=higher_level_time_unit_2)
        self.assertIs(higher_level_time_unit.is_highest_level(), False)

    def test_is_highest_level_with_branches_of_equal_depth(self):
        """
        is_highest_level() returns True for a top level time unit when
        there is another "branch" in the calendar whose top level time
        unit is of equal (but not greater) depth.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        bottom_level_time_unit = TimeUnit.objects.create(calendar=calendar)
        higher_level_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        higher_level_time_unit_2 = TimeUnit.objects.create(calendar=calendar, base_unit=bottom_level_time_unit)
        self.assertIs(higher_level_time_unit.is_highest_level(), True)
