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

    def test_get_length_at_iteration_with_cycle_of_one_and_iteration_one(self):
        """
        get_length_at_iteration() returns the only length in a length
        cycle with only one length when the iteration is 1.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='4')
        self.assertIs(time_unit.get_length_at_iteration(1), 4)

    def test_get_length_at_iteration_with_cycle_of_one_and_any_valid_iteration(self):
        """
        get_length_at_iteration() returns the only length in a length
        cycle with only one length when the iteration is any integer of
        1 or higher.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='4')
        self.assertIs(time_unit.get_length_at_iteration(1), 4)
        self.assertIs(time_unit.get_length_at_iteration(2), 4)
        self.assertIs(time_unit.get_length_at_iteration(10), 4)
        self.assertIs(time_unit.get_length_at_iteration(100), 4)
        self.assertIs(time_unit.get_length_at_iteration(987654321), 4)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_one(self):
        """
        get_length_at_iteration() returns the first length in a length
        cycle with 4 lengths when the iteration is 1.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(1), 2)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_two(self):
        """
        get_length_at_iteration() returns the second length in a length
        cycle with 4 lengths when the iteration is 2.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(2), 5)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_three(self):
        """
        get_length_at_iteration() returns the third length in a length
        cycle with 4 lengths when the iteration is 3.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(3), 8)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_four(self):
        """
        get_length_at_iteration() returns the fourth length in a length
        cycle with 4 lengths when the iteration is 4.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(4), 12)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_five(self):
        """
        get_length_at_iteration() returns the first length in a length
        cycle with 4 lengths when the iteration is 5.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(5), 2)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_six(self):
        """
        get_length_at_iteration() returns the second length in a length
        cycle with 4 lengths when the iteration is 6.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(6), 5)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_seven(self):
        """
        get_length_at_iteration() returns the third length in a length
        cycle with 4 lengths when the iteration is 7.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(7), 8)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_eight(self):
        """
        get_length_at_iteration() returns the fourth length in a length
        cycle with 4 lengths when the iteration is 8.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(8), 12)

    def test_get_length_at_iteration_with_cycle_of_four_and_iteration_nine(self):
        """
        get_length_at_iteration() returns the first length in a length
        cycle with 4 lengths when the iteration is 9.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='2 5 8 12')
        self.assertIs(time_unit.get_length_at_iteration(9), 2)

    def test_get_length_at_iteration_with_cycle_of_one_with_decimal_length_and_pre_trigger_iteration(self):
        """
        get_length_at_iteration() returns the truncated integer portion
        of a length with a decimal that has not iterated enough for the
        decimal to contribute to the length.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='3.5')
        self.assertIs(time_unit.get_length_at_iteration(1), 3)

    def test_get_length_at_iteration_with_cycle_of_one_with_decimal_length_and_first_triggering_iteration(self):
        """
        get_length_at_iteration() returns 1 higher than the truncated
        integer portion of a length with a decimal that has iterated
        just enough for the decimal to contribute to the length.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='3.5')
        self.assertIs(time_unit.get_length_at_iteration(2), 4)

    def test_get_length_at_iteration_with_cycle_of_one_with_decimal_length_and_non_triggering_iteration_after_first_trigger(self):
        """
        get_length_at_iteration() returns the truncated integer portion
        of a length with a decimal that has previously iterated enough
        for the decimal to contribute to the length but with this
        particular iteration not pushing the remainder over the "1.0"
        threshold.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='3.5')
        self.assertIs(time_unit.get_length_at_iteration(3), 3)

    def test_get_length_at_iteration_with_cycle_of_three_with_decimal_length_and_non_triggering_iteration(self):
        """
        get_length_at_iteration() returns the truncated integer portion
        of a length with a decimal for an iteration that does not
        trigger the extra length when the length cycle contains 3
        lengths.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='11 12.5 14')
        self.assertIs(time_unit.get_length_at_iteration(8), 12)

    def test_get_length_at_iteration_with_cycle_of_three_with_decimal_length_and_triggering_iteration(self):
        """
        get_length_at_iteration() returns 1 higher than the truncated
        integer portion of a length with a decimal for an iteration
        that triggers the extra length when the length cycle contains 3
        lengths.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='11 12.5 14')
        self.assertIs(time_unit.get_length_at_iteration(11), 13)

    def test_get_length_at_iteration_with_cycle_of_three_with_decimal_length_and_non_decimal_iteration_on_triggering_loop(self):
        """
        get_length_at_iteration() returns the specified length for a
        position in the length cycle that does not have a decimal
        value, even when a different length in the same loop of the
        cycle that does have a decimal triggered its extra length.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='11 12.5 14')
        self.assertIs(time_unit.get_length_at_iteration(12), 14)

    def test_get_length_at_iteration_with_cycle_of_three_with_multiple_decimal_lengths(self):
        """
        get_length_at_iteration() returns the expected values for
        iterations in a length cycle that has multiple different
        decimal length values.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1.5 4.25 100.1')
        self.assertIs(time_unit.get_length_at_iteration(1), 1)
        self.assertIs(time_unit.get_length_at_iteration(2), 4)
        self.assertIs(time_unit.get_length_at_iteration(3), 100)
        self.assertIs(time_unit.get_length_at_iteration(4), 2)
        self.assertIs(time_unit.get_length_at_iteration(5), 4)
        self.assertIs(time_unit.get_length_at_iteration(6), 100)
        self.assertIs(time_unit.get_length_at_iteration(10), 2)
        self.assertIs(time_unit.get_length_at_iteration(11), 5)
        self.assertIs(time_unit.get_length_at_iteration(12), 100)
        self.assertIs(time_unit.get_length_at_iteration(28), 2)
        self.assertIs(time_unit.get_length_at_iteration(29), 4)
        self.assertIs(time_unit.get_length_at_iteration(30), 101)

    def test_get_first_base_unit_instance_iteration_at_iteration_with_iteration_one(self):
        """
        get_first_base_unit_instance_iteration_at_iteration() returns 1
        when the iteration is 1.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='1')
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(1), 1)

    def test_get_first_base_unit_instance_iteration_at_iteration_with_iteration_in_first_loop(self):
        """
        get_first_base_unit_instance_iteration_at_iteration() returns
        the expected value when the iteration is within the first loop
        of the length cycle.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(1), 1)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(2), 32)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(3), 60)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(4), 91)

    def test_get_first_base_unit_instance_iteration_at_iteration_with_iteration_in_second_loop(self):
        """
        get_first_base_unit_instance_iteration_at_iteration() returns
        the expected value when the iteration is within the second loop
        of the length cycle.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(5), 121)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(6), 152)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(7), 180)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(8), 211)

    def test_get_first_base_unit_instance_iteration_at_iteration_with_iteration_for_decimal_trigger(self):
        """
        get_first_base_unit_instance_iteration_at_iteration() returns
        the expected value before, during, and after an iteration on a
        decimal length value triggers an extra (or "leap") time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(13), 361)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(14), 392)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(15), 421)
        self.assertEqual(time_unit.get_first_base_unit_instance_iteration_at_iteration(16), 452)
