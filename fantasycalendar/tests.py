from decimal import Decimal

from django.test import TestCase
from .models import TimeUnit, Calendar, World, DateFormat


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

    def test_get_length_at_iteration_with_cycle_of_one_with_decimal_length_and_non_triggering_iteration_after_first_trigger(
            self):
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

    def test_get_length_at_iteration_with_cycle_of_three_with_decimal_length_and_non_decimal_iteration_on_triggering_loop(
            self):
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

    def test_get_first_bottom_level_iteration_at_iteration_with_bottom_level_unit(self):
        """
        get_first_bottom_level_iteration_at_iteration() returns the
        iteration value exactly as it was passed in when called on a
        bottom level time unit (for valid iteration values).
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(1), 1)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(2), 2)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(10), 10)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(1234), 1234)

    def test_get_first_bottom_level_iteration_at_iteration_with_level_two_unit(self):
        """
        get_first_bottom_level_iteration_at_iteration() returns the
        expected value when called on a second level time unit (for
        valid iteration values).
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(1), 1)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(2), 32)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(3), 60)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(15), 421)

    def test_get_first_bottom_level_iteration_at_iteration_with_level_three_unit(self):
        """
        get_first_bottom_level_iteration_at_iteration() returns the
        expected value when called on a third level time unit (for
        valid iteration values).
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        middle_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit,
                                                   length_cycle='31 28.25 31 30')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=middle_time_unit, length_cycle='4')
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(1), 1)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(2), 121)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(3), 241)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(4), 361)
        self.assertEqual(time_unit.get_first_bottom_level_iteration_at_iteration(5), 482)

    def test_get_bottom_level_length_at_iteration_with_bottom_level_unit(self):
        """
        get_bottom_level_length_at_iteration() returns the expected
        value when called on a bottom level time unit (for valid
        iteration values).
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(1), 1)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(2), 1)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(10), 1)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(1234), 1)

    def test_get_bottom_level_length_at_iteration_with_level_two_unit(self):
        """
        get_bottom_level_length_at_iteration() returns the expected
        value when called on a second level time unit (for valid
        iteration values).
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(1), 31)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(2), 28)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(4), 30)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(6), 28)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(14), 29)

    def test_get_bottom_level_length_at_iteration_with_level_three_unit(self):
        """
        get_bottom_level_length_at_iteration() returns the expected
        value when called on a third level time unit (for valid
        iteration values).
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        middle_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit,
                                                   length_cycle='31 28.25 31 30')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=middle_time_unit, length_cycle='4')
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(1), 120)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(2), 120)
        self.assertEqual(time_unit.get_bottom_level_length_at_iteration(4), 121)

    def test_get_expanded_length_cycle_with_no_decimals(self):
        """
        get_expanded_length_cycle() returns the same cycle as
        get_length_cycle() when there are no decimals in the length
        cycle.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1 2 3')
        time_unit_2 = TimeUnit.objects.create(calendar=calendar, length_cycle='10 100 4 9999 20')
        self.assertEqual(time_unit.get_expanded_length_cycle(), time_unit.get_length_cycle())
        self.assertEqual(time_unit_2.get_expanded_length_cycle(), time_unit_2.get_length_cycle())

    def test_get_expanded_length_cycle_with_one_length_decimal(self):
        """
        get_expanded_length_cycle() returns the expanded length cycle
        as expected when the length cycle consists of one length with a
        decimal value.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='30.25')
        self.assertEqual(time_unit.get_expanded_length_cycle(), [30, 30, 30, 31])

    def test_get_expanded_length_cycle_with_one_length_decimal_over_half(self):
        """
        get_expanded_length_cycle() returns the expanded length cycle
        as expected when the length cycle consists of one length with a
        decimal value whose fractional component is greater than 0.5.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1.75')
        self.assertEqual(time_unit.get_expanded_length_cycle(), [1, 2, 2, 2])

    def test_get_expanded_length_cycle_with_two_lengths_both_different_decimal(self):
        """
        get_expanded_length_cycle() returns the expanded length cycle
        as expected when the length cycle consists of two lengths, each
        with a different decimal value.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='30.25 1.75')
        time_unit_2 = TimeUnit.objects.create(calendar=calendar, length_cycle='2.5 5.2')
        self.assertEqual(time_unit.get_expanded_length_cycle(), [30, 1, 30, 2, 30, 2, 31, 2])
        self.assertEqual(time_unit_2.get_expanded_length_cycle(),
                         [2, 5, 3, 5, 2, 5, 3, 5, 2, 6, 3, 5, 2, 5, 3, 5, 2, 5, 3, 6])

    def test_get_expanded_length_cycle_with_many_lengths_one_decimal(self):
        """
        get_expanded_length_cycle() returns the expanded length cycle
        as expected when the length cycle consists of multiple lengths,
        one of which has a decimal value.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_expanded_length_cycle(),
                         [31, 28, 31, 30, 31, 28, 31, 30, 31, 28, 31, 30, 31, 29, 31, 30])

    def test_get_expanded_length_cycle_with_many_lengths_two_decimals(self):
        """
        get_expanded_length_cycle() returns the expanded length cycle
        as expected when the length cycle consists of multiple lengths,
        two of which have a decimal value.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1 2.5 4 5.2')
        self.assertEqual(time_unit.get_expanded_length_cycle(),
                         [1, 2, 4, 5, 1, 3, 4, 5, 1, 2, 4, 5, 1, 3, 4, 5, 1, 2, 4, 6, 1, 3, 4, 5, 1, 2, 4, 5, 1, 3, 4,
                          5, 1, 2, 4, 5, 1, 3, 4, 6])

    def test_get_bottom_level_length_cycle_with_level_three_unit(self):
        """
        get_bottom_level_length_cycle() returns the expected values
        when called on a third level time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        middle_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit,
                                                   length_cycle='31 28.25 31 30')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=middle_time_unit, length_cycle='4')
        self.assertEqual(time_unit.get_bottom_level_length_cycle(), [Decimal(120.25)])

    def test_get_bottom_level_length_cycle_with_level_two_unit(self):
        """
        get_bottom_level_length_cycle() returns the same cycle as
        get_length_cycle() when called on a second level time unit, as
        the length cycle of a time unit whose base unit is already a
        bottom level unit is already a bottom level length cycle.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_bottom_level_length_cycle(), time_unit.get_length_cycle())

    def test_get_bottom_level_length_cycle_with_bottom_level_unit(self):
        """
        get_bottom_level_length_cycle() returns the same cycle as
        get_length_cycle() (which should generally be [1]) when called
        on a bottom level time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        self.assertEqual(time_unit.get_bottom_level_length_cycle(), time_unit.get_length_cycle())

    def test_get_iteration_at_bottom_level_iteration_with_bottom_level_unit(self):
        """
        get_iteration_at_bottom_level_iteration() returns the same
        value that was passed in when called on a bottom level time
        unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(1), 1)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(12121), 12121)

    def test_get_iteration_at_bottom_level_iteration_with_level_two_unit(self):
        """
        get_iteration_at_bottom_level_iteration() returns the expected
        value when called on a second level time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit, length_cycle='31 28.25 31 30')
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(1), 1)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(31), 1)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(32), 2)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(100), 4)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(481), 16)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(482), 17)

    def test_get_iteration_at_bottom_level_iteration_with_level_three_unit(self):
        """
        get_iteration_at_bottom_level_iteration() returns the expected
        value when called on a third level time unit.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        base_time_unit = TimeUnit.objects.create(calendar=calendar, length_cycle='1')
        middle_time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=base_time_unit,
                                                   length_cycle='31 28.25 31 30')
        time_unit = TimeUnit.objects.create(calendar=calendar, base_unit=middle_time_unit, length_cycle='4')
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(1), 1)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(31), 1)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(32), 1)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(120), 1)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(121), 2)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(481), 4)
        self.assertEqual(time_unit.get_iteration_at_bottom_level_iteration(482), 5)


class DateFormatModelTests(TestCase):
    def test_is_reversible_with_reversible_day_month_year_iterations(self):
        """
        is_reversible() returns True for a standard "month/day/year"
        date format that uses all numbers.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day)
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month)
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        self.assertTrue(date_format.is_reversible())

    def test_is_reversible_with_reversible_day_month_year_names(self):
        """
        is_reversible() returns True for a standard "month day, year"
        date format that uses month names.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day)
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month,
                                       base_unit_instance_names='January February March April May June July August '
                                                                'September October November December')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-n}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='Standard Day Format',
                                 format_string=month_code + ' ' + day_code + ', ' + year_code)
        self.assertTrue(date_format.is_reversible())

    def test_is_reversible_with_not_reversible_day_month_year_iterations(self):
        """
        is_reversible() returns False for a "day/year" date format
        where day is relative to month.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day)
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month)
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string='/' + day_code + '/' + year_code)
        self.assertFalse(date_format.is_reversible())

    def test_is_reversible_with_not_reversible_day_month_year_names(self):
        """
        is_reversible() returns False for a "month day, year" date
        format that uses month names if there are multiple months in a
        year that have the same name.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day)
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month,
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-n}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='Standard Day Format',
                                 format_string=month_code + ' ' + day_code + ', ' + year_code)
        self.assertFalse(date_format.is_reversible())

    def test_is_reversible_with_reversible_day_month_year_century_branching(self):
        """
        is_reversible() returns True for a "day-month-year-century"
        date format if year and month are both relative to century and
        day is relative to month, regardless of the order of the codes
        in the format string.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day)
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month)
        century = TimeUnit.objects.create(calendar=calendar, base_unit=year)
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(century.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(century.id) + '-' + str(year.id) + '-i}'
        century_code = '{' + str(century.id) + '-' + str(century.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='Century Dashes',
                                 format_string=day_code + '-' + month_code + '-' + year_code + '-' + century_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='Century Dashes',
                                   format_string=century_code + '-' + year_code + '-' + month_code + '-' + day_code)
        date_format3 = DateFormat(calendar=calendar, time_unit=day, date_format_name='Century Dashes',
                                  format_string=year_code + '-' + day_code + '-' + century_code + '-' + month_code)
        self.assertTrue(date_format.is_reversible())
        self.assertTrue(date_format_2.is_reversible())
        self.assertTrue(date_format3.is_reversible())

    def test_is_reversible_with_not_reversible_day_week_month_year_century_branching(self):
        """
        is_reversible() returns False for a "day-month-year-century"
        date format if year and month are both relative to century and
        day is relative to week, regardless of the order of the codes in
        the format string.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        week = TimeUnit.objects.create(calendar=calendar, base_unit=day)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day)
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month)
        century = TimeUnit.objects.create(calendar=calendar, base_unit=year)
        day_code = '{' + str(week.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(century.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(century.id) + '-' + str(year.id) + '-i}'
        century_code = '{' + str(century.id) + '-' + str(century.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='Century Dashes',
                                 format_string=day_code + '-' + month_code + '-' + year_code + '-' + century_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='Century Dashes',
                                   format_string=century_code + '-' + year_code + '-' + month_code + '-' + day_code)
        date_format3 = DateFormat(calendar=calendar, time_unit=day, date_format_name='Century Dashes',
                                  format_string=year_code + '-' + day_code + '-' + century_code + '-' + month_code)
        self.assertFalse(date_format.is_reversible())
        self.assertFalse(date_format_2.is_reversible())
        self.assertFalse(date_format3.is_reversible())

    def test_get_values_from_formatted_date_with_day_month_year_iterations(self):
        """
        get_values_from_formatted_date() returns the expected values
        for a date format that uses all numbers.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date = date_format.get_formatted_date(100)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Extra Slashes',
                                   format_string='/' + month_code + '/' + day_code + '/' + year_code + '/')
        date_2 = date_format_2.get_formatted_date(100)
        self.assertEqual(date, '4/10/1')
        self.assertEqual(date_format.get_values_from_formatted_date(date), ['4', '10', '1'])
        self.assertEqual(date_2, '/4/10/1/')
        self.assertEqual(date_format_2.get_values_from_formatted_date(date_2), ['4', '10', '1'])

    def test_get_values_from_formatted_date_with_day_month_year_names(self):
        """
        get_values_from_formatted_date() returns the expected values
        for a date format that contains a name.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-n}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date = date_format.get_formatted_date(100)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Extra Slashes',
                                   format_string='/' + month_code + '/' + day_code + '/' + year_code + '/')
        date_2 = date_format_2.get_formatted_date(100)
        self.assertEqual(date, 'April/10/1')
        self.assertEqual(date_format.get_values_from_formatted_date(date), ['April', '10', '1'])
        self.assertEqual(date_2, '/April/10/1/')
        self.assertEqual(date_format_2.get_values_from_formatted_date(date_2), ['April', '10', '1'])

    def test_get_iteration_with_day_month_year_iterations(self):
        """
        get_iteration() returns the expected value for a date format
        that uses all numbers.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date = date_format.get_formatted_date(100)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Extra Slashes',
                                   format_string='/' + month_code + '/' + day_code + '/' + year_code + '/')
        date_2 = date_format_2.get_formatted_date(100)
        self.assertEqual(date, '4/10/1')
        self.assertEqual(date_format.get_iteration(date), 100)
        self.assertEqual(date_2, '/4/10/1/')
        self.assertEqual(date_format_2.get_iteration(date_2), 100)

    def test_get_iteration_with_day_month_year_names(self):
        """
        get_iteration() returns the expected value for a date format
        that contains a name.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-n}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date = date_format.get_formatted_date(100)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Extra Slashes',
                                   format_string='/' + month_code + '/' + day_code + '/' + year_code + '/')
        date_2 = date_format_2.get_formatted_date(100)
        self.assertEqual(date, 'April/10/1')
        self.assertEqual(date_format.get_iteration(date), 100)
        self.assertEqual(date_2, '/April/10/1/')
        self.assertEqual(date_format_2.get_iteration(date_2), 100)

    def test_is_differentiable_with_differentiable_single_other(self):
        """
        is_differentiable() returns True when comparing a
        "month/day/year" date format and a "day-month-year" date
        format.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Dashes',
                                   format_string=day_code + '-' + month_code + '-' + year_code)
        self.assertTrue(date_format.is_differentiable(date_format_2))
        self.assertTrue(date_format_2.is_differentiable(date_format))

    def test_is_differentiable_with_differentiable_two_differentiable_others(self):
        """
        is_differentiable() returns True when comparing a
        "month/day/year" date format to a "day-month-year" date format
        and a "day.month.year" date format.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Dashes',
                                   format_string=day_code + '-' + month_code + '-' + year_code)
        date_format_3 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Dots',
                                   format_string=day_code + '.' + month_code + '.' + year_code)
        self.assertTrue(date_format.is_differentiable([date_format_2, date_format_3]))

    def test_is_differentiable_with_differentiable_two_non_differentiable_others(self):
        """
        is_differentiable() returns True when comparing a
        "month/day/year" date format to a "day-month-year" date format
        and a "month-day-year" date format.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Dashes',
                                   format_string=day_code + '-' + month_code + '-' + year_code)
        date_format_3 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Dashes',
                                   format_string=month_code + '-' + day_code + '-' + year_code)
        self.assertTrue(date_format.is_differentiable([date_format_2, date_format_3]))

    def test_is_differentiable_with_non_differentiable_single_other(self):
        """
        is_differentiable() returns False when comparing a
        "month/day/year" date format and a "day/month/year" date
        format.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Slashes',
                                   format_string=day_code + '/' + month_code + '/' + year_code)
        self.assertFalse(date_format.is_differentiable(date_format_2))
        self.assertFalse(date_format_2.is_differentiable(date_format))

    def test_is_differentiable_with_two_others_one_non_differentiable(self):
        """
        is_differentiable() returns False when comparing a
        "month/day/year" date format to a "day-month-year" date format
        and a "day/month/year" date format.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Dashes',
                                   format_string=day_code + '-' + month_code + '-' + year_code)
        date_format_3 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Slashes',
                                   format_string=day_code + '/' + month_code + '/' + year_code)
        self.assertFalse(date_format.is_differentiable([date_format_2, date_format_3]))
        self.assertFalse(date_format.is_differentiable([date_format_3, date_format_2]))

    def test_is_differentiable_with_non_differentiable_two_others(self):
        """
        is_differentiable() returns True when comparing a
        "month/day/year" date format to a "day/month/year" date format
        and a "year/month/day" date format.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='European Slashes',
                                   format_string=day_code + '/' + month_code + '/' + year_code)
        date_format_3 = DateFormat(calendar=calendar, time_unit=day, date_format_name='Descending Slashes',
                                   format_string=year_code + '-' + month_code + '-' + day_code)
        self.assertFalse(date_format.is_differentiable([date_format_2, date_format_3]))
        self.assertFalse(date_format.is_differentiable([date_format_3, date_format_2]))

    def test_formatted_date_is_possible_with_possible_date(self):
        """
        formatted_date_is_possible() returns True when given a
        formatted date string that the date format could have
        generated.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date = date_format.get_formatted_date(100)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Extra Slashes',
                                   format_string='/' + month_code + '/' + day_code + '/' + year_code + '/')
        date_2 = date_format_2.get_formatted_date(100)
        self.assertTrue(date_format.formatted_date_is_possible(date))
        self.assertTrue(date_format.formatted_date_is_possible('12/20/1995'))
        self.assertTrue(date_format.formatted_date_is_possible('1/1/1'))
        self.assertTrue(date_format_2.formatted_date_is_possible(date_2))
        self.assertTrue(date_format_2.formatted_date_is_possible('/12/20/1995/'))
        self.assertTrue(date_format_2.formatted_date_is_possible('/1/1/1/'))

    def test_formatted_date_is_possible_with_non_possible_date(self):
        """
        formatted_date_is_possible() returns False when given a
        formatted date string that the date format could not have
        generated.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Extra Slashes',
                                   format_string='/' + month_code + '/' + day_code + '/' + year_code + '/')
        self.assertFalse(date_format.formatted_date_is_possible('12/1995'))
        self.assertFalse(date_format.formatted_date_is_possible('1-1-1'))
        self.assertFalse(date_format_2.formatted_date_is_possible('12/20/1995'))
        self.assertFalse(date_format_2.formatted_date_is_possible('-1-1/1/'))

    def test_find_likely_source_date_formats_with_one_possible_match(self):
        """
        find_likely_source_date_formats() returns a list containing one
        correct date format when only one of the date formats it was
        provided could have generated the formatted date string it was
        provided.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Dashes',
                                   format_string=month_code + '-' + day_code + '-' + year_code)
        date = '2/3/1800'
        likely_formats = DateFormat.find_likely_source_date_formats(date, [date_format, date_format_2])
        self.assertEqual(len(likely_formats), 1)
        self.assertEqual(likely_formats[0], date_format)
        date_2 = '2-3-1800'
        likely_formats_2 = DateFormat.find_likely_source_date_formats(date_2, [date_format, date_format_2])
        self.assertEqual(len(likely_formats_2), 1)
        self.assertEqual(likely_formats_2[0], date_format_2)

    def test_find_likely_source_date_formats_with_two_possible_matches(self):
        """
        find_likely_source_date_formats() returns a correctly ordered
        list containing two date formats when both of the date formats
        it was provided could have generated the formatted date string
        it was provided.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Extra Slashes',
                                   format_string='/' + month_code + '/' + day_code + '/' + year_code + '/')
        date = '/2/3/1800/'
        likely_formats = DateFormat.find_likely_source_date_formats(date, [date_format, date_format_2])
        self.assertEqual(len(likely_formats), 2)
        self.assertEqual(likely_formats[0], date_format_2)  # the extra slashes is the most likely match
        self.assertEqual(likely_formats[1], date_format)  # but a {} code could resolve to e.g. "/2" so this is possible
        likely_formats_2 = DateFormat.find_likely_source_date_formats(date, [date_format_2, date_format])  # list swap
        self.assertEqual(len(likely_formats_2), 2)
        self.assertEqual(likely_formats_2[0], date_format_2)
        self.assertEqual(likely_formats_2[1], date_format)

    def test_find_likely_source_date_formats_with_no_possible_matches(self):
        """
        find_likely_source_date_formats() returns an empty list when
        none of the date formats it was provided could have generated
        the formatted date string it was provided.
        """
        world = World.objects.create()
        calendar = Calendar.objects.create(world=world)
        day = TimeUnit.objects.create(calendar=calendar)
        month = TimeUnit.objects.create(calendar=calendar, base_unit=day, length_cycle='30')
        year = TimeUnit.objects.create(calendar=calendar, base_unit=month, length_cycle='12',
                                       base_unit_instance_names='January February March April January June July August '
                                                                'September January March September')
        day_code = '{' + str(month.id) + '-' + str(day.id) + '-i}'
        month_code = '{' + str(year.id) + '-' + str(month.id) + '-i}'
        year_code = '{' + str(year.id) + '-' + str(year.id) + '-i}'
        date_format = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Slashes',
                                 format_string=month_code + '/' + day_code + '/' + year_code)
        date_format_2 = DateFormat(calendar=calendar, time_unit=day, date_format_name='American Dashes',
                                   format_string=month_code + '-' + day_code + '-' + year_code)
        date = '2.3.1800'
        likely_formats = DateFormat.find_likely_source_date_formats(date, [date_format, date_format_2])
        self.assertEqual(len(likely_formats), 0)
        date_2 = '2-3/1800'
        likely_formats_2 = DateFormat.find_likely_source_date_formats(date_2, [date_format, date_format_2])
        self.assertEqual(len(likely_formats_2), 0)
