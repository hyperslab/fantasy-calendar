import decimal
import math
import re
from copy import copy
from decimal import Decimal

from django.db import models
from django.contrib import admin
from django.urls import reverse
from django.conf import settings
from .utils import html_tooltip


class World(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  # remove null=True later
    world_name = models.CharField(max_length=200, help_text=html_tooltip('The name of this world'))
    public = models.BooleanField(default=False,
                                 help_text=html_tooltip('Whether this world is viewable by other people'))

    def __str__(self):
        return self.world_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:world-detail', kwargs={'pk': self.pk})


class Calendar(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    calendar_name = models.CharField(max_length=200, help_text=html_tooltip('The name of this calendar'))
    default_display_config = models.ForeignKey('DisplayConfig', on_delete=models.CASCADE, null=True, related_name='+',
                                               blank=True,
                                               help_text=html_tooltip('The display configuration for this calendar to '
                                                                      'use when initially loading into the page'))

    def __str__(self):
        return self.calendar_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:calendar-detail', kwargs={'pk': self.pk, 'world_key': self.world.pk})

    def get_bottom_level_time_unit(self) -> 'TimeUnit':
        """
        Return the lowest-level unit of time in this calendar, i.e. the
        equivalent of a "day".
        """
        return TimeUnit.objects.get(calendar_id=self.pk, base_unit=None)

    def ensure_bottom_level_time_unit(self, default_name="Day"):
        """
        Create a default bottom-level time unit for this calendar if it does
        not have one.
        """
        if not TimeUnit.objects.filter(calendar_id=self.pk, base_unit=None).exists():
            time_unit = TimeUnit(time_unit_name=default_name, calendar=self)
            time_unit.save()


class TimeUnit(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    time_unit_name = models.CharField(max_length=200, default='',
                                      help_text=html_tooltip('The name of this time unit, e.g. "Month" or "Day"'))
    base_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                  help_text=html_tooltip('The type of time unit that this time unit consists of,  e.g. '
                                                         '"Year" could have a base unit of "Month"'))
    length_cycle = models.CharField(max_length=800, default='1',
                                    help_text=html_tooltip('The number of base time units in this time unit; if the '
                                                           'length varies, specify multiple lengths separated by '
                                                           'spaces, e.g. "10 11 12" would result in a length of 10, '
                                                           'then 11, then 12, then repeat from 10, etc.'))
    base_unit_instance_names = models.CharField(max_length=800, default='', blank=True,
                                                help_text=html_tooltip('The name(s) of each instance of a base time '
                                                                       'unit within this time unit, separated by '
                                                                       'spaces, e.g. "Year" could have base units '
                                                                       'called "January February (...) December"'))
    default_date_format = models.ForeignKey('DateFormat', on_delete=models.CASCADE, null=True, blank=True,
                                            help_text=html_tooltip('The format for instances of this time unit to be '
                                                                   'displayed as most prominently, such as on the '
                                                                   'title of a calendar page'),
                                            related_name='timeunit_default_set')
    secondary_date_format = models.ForeignKey('DateFormat', on_delete=models.CASCADE, null=True, blank=True,
                                              help_text=html_tooltip('The format for instances of this time unit to be '
                                                                     'displayed as in less prominent locations, often '
                                                                     'in groups underneath a parent unit, such as on '
                                                                     'individual boxes in a calendar page'),
                                              related_name='timeunit_secondary_set')

    def __str__(self):
        return self.time_unit_name

    @admin.display(boolean=True, description='Lowest level time unit?')
    def is_bottom_level(self) -> bool:
        """
        Return True if this is the lowest-level unit of time in its
        Calendar, i.e. the equivalent of a "day".
        """
        return self.base_unit is None and self.id is not None  # will not be considered "bottom level" until saved to db

    def get_length_cycle_display(self) -> str:
        """
        Return length_cycle formatted as a string for display.
        """
        lengths = self.get_length_cycle()
        if len(lengths) == 0:  # this shouldn't happen
            return 'Undefined'
        else:
            return ', '.join(['{:f}'.format(x.normalize()) for x in lengths])

    def is_top_level(self) -> bool:
        """
        Return True if there are no other TimeUnit objects that have
        this TimeUnit as their base_unit.
        """
        return TimeUnit.objects.filter(base_unit_id=self.id).count() == 0

    def get_level_depth(self) -> int:
        """
        Return the depth of this TimeUnit relative to its base time
        units, with a bottom level unit like a "day" being level 1. So
        a "month" made of days would be level 2, a "year" made of
        months would be level 3, etc.
        """
        if self.is_bottom_level():
            return 1
        else:
            return self.base_unit.get_level_depth() + 1

    def is_highest_level(self) -> bool:
        """
        Return True if there are no other TimeUnit objects on the
        same Calendar as this TimeUnit that have a higher depth (as
        described in get_level_depth).
        """
        level = self.get_level_depth()
        time_units = TimeUnit.objects.filter(calendar_id=self.calendar.id)
        for time_unit in time_units:
            if time_unit.get_level_depth() > level:
                return False
        return True

    def get_base_unit_instance_names(self) -> list[str]:
        """
        Return base_unit_instance_names as a list of each name.
        """
        if not self.base_unit_instance_names:
            return []
        names = self.base_unit_instance_names.split()
        if type(names) is not list:
            names = [names]
        return names

    def set_base_unit_instance_names(self, names: list[str]):
        """
        Save base_unit_instance_names from a list of each name.
        """
        self.base_unit_instance_names = ' '.join(names)
        self.save()

    def get_length_cycle(self) -> list[decimal]:
        """
        Return length_cycle as a list of each length in the cycle as a
        decimal value.
        """
        if not self.length_cycle:
            return []
        lengths = [Decimal(x) for x in self.length_cycle.split()]
        if type(lengths) is not list:
            lengths = [lengths]
        return lengths

    def set_length_cycle(self, lengths: list[decimal]):
        """
        Save length_cycle from a list of each length in the cycle. Each
        length should be a decimal value.
        """
        self.length_cycle = ' '.join([str(x) for x in lengths])
        self.save()

    def get_length_at_iteration(self, iteration: int) -> int:
        """
        Return the number of base units in the instance of this time
        unit that exists at a particular iteration. An iteration of 1
        corresponds to the first instance of this time unit in its
        calendar; values 0 and below are not used. No base or parent
        units are considered in determining the iteration value.

        As an example, if there are 12 "Month"s in a "Year", the fourth
        Month of Year 3 would have iteration value 28.

        The value returned is a whole integer with "leap"s already
        factored in. Access length_cycle directly to see decimal
        values.
        """
        length_cycle = self.get_length_cycle()
        cycle_location = (iteration - 1) % len(length_cycle)
        cycle_iteration = int((iteration - 1) / len(length_cycle)) + 1
        base_length = int(length_cycle[cycle_location])
        remainder_length = length_cycle[cycle_location] % 1
        extra = 0
        if ((remainder_length * (cycle_iteration - 1)) % 1) + remainder_length >= 1:
            extra = 1
        return int(base_length + extra)

    def get_first_base_unit_instance_iteration_at_iteration(self, iteration: int) -> int:
        """
        Return the iteration value of the first base unit in the
        instance of this time unit that exists at a given iteration.

        As an example, if there are 12 "Month"s in a "Year", then
        calling this method on the Year with an iteration value of 4
        will return 37, as the first Month of Year 4 is Month 37.

        Always returns 1 when the iteration value is 1.
        """
        length_cycle = self.get_length_cycle()
        number_of_complete_cycles = int((iteration - 1) / len(length_cycle))
        current_cycle_completed_instances = (iteration - 1) % len(length_cycle)
        base_iteration = number_of_complete_cycles * sum(length_cycle)
        for i in range(current_cycle_completed_instances):
            base_iteration += length_cycle[i]
        return int(base_iteration) + 1

    def get_base_unit_instances(self, iteration: int = 1) -> list[tuple[str, int]]:
        """
        Return a list of [str, int] tuples representing the names and
        lengths (in whole number of base units) of all base unit
        instances in the instance of this time unit that exists at a
        particular iteration.

        As an example, in a calendar with "Year"s made of "Month"s made
        of "Day"s, calling this method on the Year will return a list
        of tuples containing the name of each month alongside its
        corresponding number of days. It might look like:
        [('January', 31), ('February', 28), ...etc. ]

        For bottom level time units (with no base unit), returns a list
        containing one tuple with the name set to the time unit name
        followed by the iteration value and the length set to 1.
        """
        if not self.base_unit:
            return [(str(self.time_unit_name) + ' ' + str(iteration), 1)]
        numer_of_instances = self.get_length_at_iteration(iteration=iteration)
        lengths = []
        custom_names = self.get_base_unit_instance_names()
        base_name = self.base_unit.time_unit_name
        names = []
        base_iteration = self.get_first_base_unit_instance_iteration_at_iteration(iteration=iteration)
        for i in range(numer_of_instances):
            lengths.append(self.base_unit.get_length_at_iteration(iteration=base_iteration))
            base_iteration += 1
            if i < len(custom_names):
                names.append(custom_names[i])
            else:
                names.append(base_name + ' ' + str(i + 1))
        return zip(names, lengths)

    def get_first_bottom_level_iteration_at_iteration(self, iteration: int) -> int:
        """
        Return the iteration value of the first bottom level time unit
        instance contained in the instance of this time unit that
        exists at a particular iteration.

        As an example, if there are 12 "Month"s in a "Year" and 30
        "Day"s in a Month, Day being the bottom level time unit for
        this calendar, then calling this method on the Year with an
        iteration value of 4 will return 1081, as the first Day of Year
        4 is Day 1081.

        Always returns 1 when the iteration value is 1.
        """
        current_unit = self
        current_unit_iteration = iteration
        while current_unit.base_unit is not None:
            current_unit_iteration = current_unit.get_first_base_unit_instance_iteration_at_iteration(
                iteration=current_unit_iteration)
            current_unit = current_unit.base_unit
        return current_unit_iteration

    def get_bottom_level_length_at_iteration(self, iteration: int) -> int:
        """
        Return the number of bottom level time units in the instance of
        this time unit that exists at a particular iteration.

        As an example, say there are 12 "Month"s in a "Year" and 30
        "Day"s in a Month plus an extra "leap" Day on one of the Months
        every 4 Years, Day being the bottom level time unit for this
        calendar. Calling this method on the Year with an iteration
        value of 3 will return 360, as there are 360 Days in the 3rd
        Year, but calling it on Year 4 will return 361, as there are
        361 Days in the 4th Year.
        """
        current_unit = self
        current_length = self.get_length_at_iteration(iteration=iteration)
        current_first_iteration = iteration
        while current_unit.base_unit is not None:
            current_first_iteration = current_unit.get_first_base_unit_instance_iteration_at_iteration(
                iteration=current_first_iteration)
            new_length = 0
            for i in range(current_first_iteration, current_first_iteration + current_length):
                new_length += current_unit.base_unit.get_length_at_iteration(i)
            current_length = new_length
            current_unit = current_unit.base_unit
        return current_length

    def get_last_bottom_level_iteration_at_iteration(self, iteration: int) -> int:
        """
        Return the iteration value of the last bottom level time unit
        instance contained in the instance of this time unit that
        exists at a particular iteration.

        As an example, if there are 12 "Month"s in a "Year" and 30
        "Day"s in a Month, Day being the bottom level time unit for
        this calendar, then calling this method on the Year with an
        iteration value of 4 will return 1440, as the last Day of Year
        4 is Day 1440.
        """
        return self.get_first_bottom_level_iteration_at_iteration(iteration=iteration) + \
               self.get_bottom_level_length_at_iteration(iteration=iteration) - 1

    def get_events_at_iteration(self, iteration: int) -> list['Event']:
        """
        Return a list of all events on the same calendar as this time
        unit that take place during the instance of this time unit that
        exists at a particular iteration.
        """
        first_bottom_level_iteration = self.get_first_bottom_level_iteration_at_iteration(iteration=iteration)
        last_bottom_level_iteration = self.get_last_bottom_level_iteration_at_iteration(iteration=iteration)
        return [x for x in Event.objects.filter(bottom_level_iteration__gte=first_bottom_level_iteration,
                                                bottom_level_iteration__lte=last_bottom_level_iteration,
                                                calendar_id=self.calendar.id)]

    @staticmethod
    def expand_length_cycle(length_cycle) -> list[int]:
        """
        Return the provided length cycle without any decimals,
        recalculated to be functionally equivalent to the length cycle
        with them.

        As an example, calling this method with a length cycle of
        [30.25] will return [30, 30, 30, 31].

        Does not modify length_cycle.
        """
        required_iterations = []
        running_decimal_totals = {}
        for i, length in enumerate(length_cycle):
            remainder = Decimal(length % 1)
            if remainder == 0:
                required_iterations.append(1)
            else:
                required_iterations.append(remainder.as_integer_ratio()[1])
                running_decimal_totals[i] = Decimal(0)
        total_iterations = math.lcm(*required_iterations)
        final_cycle = []
        for _ in range(total_iterations):
            for i, length in enumerate(length_cycle):
                base_length = int(length)
                remainder_length = Decimal(length % 1)
                if remainder_length > 0:
                    running_decimal_totals[i] += remainder_length
                    if running_decimal_totals[i] >= 1:
                        base_length += 1
                        running_decimal_totals[i] -= 1
                final_cycle.append(base_length)
        return final_cycle

    def get_expanded_length_cycle(self) -> list[int]:
        """
        Return the length cycle of this time unit without any decimals,
        recalculated to be functionally equivalent to the length cycle
        with them.

        As an example, if there are 30.25 "Day"s in a "Month", then
        calling this method on the Month (on which get_length_cycle
        will return [30.25]) will return [30, 30, 30, 31].
        """
        return TimeUnit.expand_length_cycle(self.get_length_cycle())

    def get_bottom_level_length_cycle(self) -> list[decimal]:
        """
        Return the length cycle of ths time unit represented in bottom
        level time units.

        As an example, if there are 12 "Month"s in a "Year" and 30
        "Day"s in a Month, Day being the bottom level time unit for
        this calendar, then calling this method on the Year will return
        [360], as there are 360 Days in a year.
        """
        current_cycle = self.get_length_cycle()
        current_unit = self
        while current_unit.base_unit and current_unit.base_unit.base_unit:
            current_cycle = TimeUnit.expand_length_cycle(current_cycle)
            lower_cycle = []
            base_cycle = current_unit.base_unit.get_length_cycle()
            base_cycle_location = 0
            while True:
                for current_length in current_cycle:
                    lower_length = 0
                    for _ in range(current_length):
                        lower_length += base_cycle[base_cycle_location]
                        base_cycle_location += 1
                        base_cycle_location %= len(base_cycle)
                    lower_cycle.append(lower_length)
                if base_cycle_location == 0:
                    break
            current_cycle = lower_cycle
            current_unit = current_unit.base_unit
        return current_cycle

    def get_iteration_at_bottom_level_iteration(self, bottom_level_iteration: int) -> int:
        """
        Return the iteration value of the instance of this time unit
        that encompasses the instance of the bottom level time unit for
        this calendar that exists at a particular iteration.

        As an example, if there are 30 "Day"s in a "Month", Day being
        the bottom level time unit for this calendar, then calling this
        method on the Month with a bottom_level_iteration value of 75
        will return 3, as the Month containing Day 75 is the 3rd Month.
        """
        if self.is_bottom_level():  # save some time on bottom level units
            return bottom_level_iteration
        bottom_level_length_cycle = TimeUnit.expand_length_cycle(self.get_bottom_level_length_cycle())
        bottom_level_cycle_length = sum(bottom_level_length_cycle)  # this should never be 0
        number_of_complete_cycles = int((bottom_level_iteration - 1) / bottom_level_cycle_length)
        remaining_units_in_current_cycle = int((bottom_level_iteration - 1) % bottom_level_cycle_length)
        current_cycle_position = 0
        while remaining_units_in_current_cycle >= bottom_level_length_cycle[current_cycle_position]:
            remaining_units_in_current_cycle -= bottom_level_length_cycle[current_cycle_position]
            current_cycle_position += 1
        return (number_of_complete_cycles * len(bottom_level_length_cycle)) + current_cycle_position + 1

    def get_first_sub_unit_instance_iteration_at_iteration(self, sub_unit: 'TimeUnit', iteration: int) -> int:
        """
        Return the iteration value of the first instance of a given
        time unit contained in the instance of this time unit that
        exists at a particular iteration.

        The given sub_unit can be any time unit used in the composition
        of this time unit, all the way down the tree, so to speak.
        Raises AttributeError if sub_unit is not found by iteratively
        checking base_unit.

        Always returns 1 when the iteration value is 1.
        """
        current_unit = self
        current_unit_iteration = iteration
        while current_unit.pk is not sub_unit.pk:
            if current_unit.base_unit is None:
                raise AttributeError
            current_unit_iteration = current_unit.get_first_base_unit_instance_iteration_at_iteration(
                iteration=current_unit_iteration)
            current_unit = current_unit.base_unit
        return current_unit_iteration

    def get_sub_unit_instance_iteration_within_higher_level_iteration(self, sub_unit: 'TimeUnit',
                                                                      sub_unit_iteration: int) -> int:
        """
        Return the iteration value of the instance of a given time unit
        at a given iteration relative to its position in the instance
        of this time unit in which it exists.

        As an example, if there are 30 "Day"s in a "Month", then
        calling this method on the Month for the sub_unit Day with a
        sub_unit_iteration value of 75 will return 15, as Day 75 is the
        15th Day in the Month in which it exists.

        If sub_unit is the same as this time unit, returns
        sub_unit_iteration as-is.
        """
        if self.pk == sub_unit.pk:  # save some time when no calculations are needed
            return sub_unit_iteration
        parent_iteration = self.get_iteration_at_bottom_level_iteration(
            bottom_level_iteration=sub_unit.get_first_bottom_level_iteration_at_iteration(iteration=sub_unit_iteration))
        first_sub_instance_iteration = self.get_first_sub_unit_instance_iteration_at_iteration(
            sub_unit=sub_unit, iteration=parent_iteration)
        return sub_unit_iteration - first_sub_instance_iteration + 1

    def get_all_higher_containing_units(self) -> list['TimeUnit']:
        """
        Return a list of all time units that are composed of this time
        unit either directly through base_unit or indirectly through
        some chaining of base_unit.
        """
        parents = []
        new_parents = [x for x in TimeUnit.objects.filter(base_unit_id=self.id)]
        while len(new_parents) > 0:
            one_level_higher = []
            for parent in new_parents:
                one_level_higher += [x for x in TimeUnit.objects.filter(base_unit_id=parent.id)]
            parents += new_parents
            new_parents = one_level_higher
        return parents

    def get_instance_display_name(self, iteration: int, date_format: 'DateFormat' = None,
                                  prefer_secondary: bool = False, primary_secondary_backup: bool = False) -> str:
        """
        Return a human-readable name for the instance of this time unit
        that exists at a particular iteration.

        In order, prefers a given date format, then the default date
        format for this time unit if none is given, then something like
        (time_unit_name + " " + iteration) if there is no default date
        format for this time unit.

        If prefer_secondary is True, use the secondary date format for
        this time unit place of its default date format in the order of
        preference above.

        If primary_secondary_backup is True, attempt to use the
        secondary date format for this time unit if it has no default
        date format before trying something like (time_unit_name +
        " " + iteration), or vice versa if prefer_secondary is True.
        """
        if date_format is None:
            if not prefer_secondary:
                date_format = self.default_date_format
                if date_format is None and primary_secondary_backup:
                    date_format = self.secondary_date_format
            else:
                date_format = self.secondary_date_format
                if date_format is None and primary_secondary_backup:
                    date_format = self.default_date_format
        if date_format:
            if date_format.time_unit != self:
                raise ValueError
            return date_format.get_formatted_date(iteration)
        else:
            return str(self.time_unit_name) + ' ' + str(iteration)


class Event(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200, help_text=html_tooltip('The name of this event'))
    event_description = models.TextField(max_length=4000, blank=True,
                                         help_text=html_tooltip('A description for this event'))
    bottom_level_iteration = models.BigIntegerField(help_text=html_tooltip('The bottom level time unit ("Day" by '
                                                                           'default) instance that this event takes '
                                                                           'place on'))

    def __str__(self):
        return self.event_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:event-detail', kwargs={'pk': self.pk, 'calendar_key': self.calendar.pk,
                                                               'world_key': self.calendar.world.pk})


class DateFormat(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    time_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE)
    date_format_name = models.CharField(max_length=200, help_text=html_tooltip('The name of this date format'))
    format_string = models.CharField(max_length=200,
                                     help_text=html_tooltip('A representation of the rules for formatting the date; '
                                                            'use curly braces containing\n1) the ID of the parent time '
                                                            'unit\n2) the ID of the time unit in question\n3) "i" for '
                                                            'the numeric iteration or "n" for the name\nseparated by '
                                                            'dashes to display information about the specific date '
                                                            'being formatted, e.g. {02-01-i} (you can use the Format '
                                                            'String Helper to generate this text for you); all other '
                                                            'characters will be displayed as-is'))

    def __str__(self):
        return self.date_format_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:date-format-detail', kwargs={'pk': self.pk, 'timeunit_key': self.time_unit.pk,
                                                                     'calendar_key': self.calendar.pk,
                                                                     'world_key': self.calendar.world.pk})

    def get_formatted_date(self, iteration: int) -> str:
        """
        Return a string representing a human-readable date for the
        instance of the time unit on this date format that exists at a
        particular iteration, formatted according to the format_string
        on this date format.
        """
        formatted_date = str(self.format_string)
        codes = []
        indexes = []
        while '{' in formatted_date and '}' in formatted_date:
            l_index = formatted_date.index('{')
            r_index = formatted_date.index('}')
            codes.append(formatted_date[l_index + 1:r_index])
            indexes.append(l_index)
            formatted_date = formatted_date[:l_index] + formatted_date[r_index + 1:]
        answers = []
        bottom_level_iteration = self.time_unit.get_first_bottom_level_iteration_at_iteration(iteration=iteration)
        for code in codes:
            [parent, sub, display] = code.split('-')
            parent_unit = TimeUnit.objects.get(pk=int(parent))
            sub_unit = TimeUnit.objects.get(pk=int(sub))
            parent_iteration = parent_unit.get_iteration_at_bottom_level_iteration(
                bottom_level_iteration=bottom_level_iteration)
            sub_iteration = sub_unit.get_iteration_at_bottom_level_iteration(
                bottom_level_iteration=bottom_level_iteration)
            sub_iteration_in_parent_iteration = parent_unit. \
                get_sub_unit_instance_iteration_within_higher_level_iteration(
                    sub_unit=sub_unit, sub_unit_iteration=sub_iteration)
            answer = 'unknown display type: "' + display + '"'
            if display.lower() in ['n', 'name']:
                instances = list(parent_unit.get_base_unit_instances(iteration=parent_iteration))
                answer = instances[sub_iteration_in_parent_iteration - 1][0]
            elif display.lower() in ['i', 'iter', 'iteration']:
                answer = str(sub_iteration_in_parent_iteration)
            answers.append(answer)
        for answer, index in zip(reversed(answers), reversed(indexes)):  # has to be backwards here so indexes work
            formatted_date = formatted_date[:index] + answer + formatted_date[index:]
        return formatted_date

    def is_reversible(self) -> bool:
        """
        Return True if any formatted date string generated by this date
        format can be converted back to an exact iteration for its time
        unit, False otherwise.

        Specifically, these are the conditions the format must meet:
        1) The format string must display this date format's time unit
        2) The format string must contain an absolute reference to a
           time unit at or "above" this date format's time unit
        3) The format string must contain enough time units so that the
           time unit of the absolute reference can "connect" to this
           date format's time unit with an unbroken chain of sub units
        4) Every time unit in the "chain" of step 3 that is referenced
           by name must have an unambiguous name, i.e. the base unit
           instance names of its parent unit must all be unique
           relative to each other
        """
        # decode the format string
        format_string = str(self.format_string)
        codes = []  # [parent, sub, display]
        while '{' in format_string and '}' in format_string:
            l_index = format_string.index('{')
            r_index = format_string.index('}')
            parent_id, sub_id, display_type = format_string[l_index + 1:r_index].split('-')
            codes.append((TimeUnit.objects.get(pk=parent_id), TimeUnit.objects.get(pk=sub_id), display_type))
            format_string = format_string[:l_index] + format_string[r_index + 1:]

        # test condition 1
        if self.time_unit not in [code[1] for code in codes]:
            return False

        # test condition 2
        suitable_absolutes = []
        for parent, sub, display in codes:
            if parent == sub:  # absolute reference is specified by parent and sub time units being the same
                if sub == self.time_unit:  # special match: if there is an absolute reference to the date format's time
                    return True            # unit, that's all we need
                elif sub in self.time_unit.get_all_higher_containing_units():
                    suitable_absolutes.append(sub)  # save all potential matches for future evaluation
        if not suitable_absolutes:
            return False

        # test conditions 3 and 4
        for time_unit in suitable_absolutes:  # test all potential matches from condition 2
            next_parents = [time_unit]  # first "layer" of the chains is just a single target unit
            while True:  # each layer of the chains is searched for via one iteration of this while loop
                current_parents = next_parents
                next_parents = []
                linked = False
                for parent, sub, display in codes:  # check all codes for next chain link down
                    if parent in current_parents and parent != sub:  # absolute references cannot chain down
                        if display.lower() not in ['n', 'name'] or \
                                len(parent.get_base_unit_instance_names()) == \
                                len(set(parent.get_base_unit_instance_names())):  # uniqueness check for names
                            if sub == self.time_unit:  # chain is complete, format is reversible
                                return True
                            else:  # chain link is made, search for the next link in this branch in the next layer
                                next_parents.append(sub)
                                linked = True
                if not linked:  # if no match was ever found, all chains are broken; check next potential target unit
                    break  # breaks the while loop
        return False  # no complete chains were found if we've made it here

    def get_fluff(self) -> list[str]:
        """
        Return the parts of the format string that lie before, between,
        and after the variable codes.
        """
        format_string = str(self.format_string)
        fluff = []
        while '{' in format_string and '}' in format_string:
            l_index = format_string.index('{')
            r_index = format_string.index('}')
            if format_string[:l_index]:
                fluff.append(format_string[:l_index])
            format_string = format_string[r_index + 1:]
        if format_string:
            fluff.append(format_string)
        return fluff

    def get_values_from_formatted_date(self, formatted_string: str) -> list[str]:
        """
        Return a list of the variable values from a formatted date
        string. For example, with a "month/day/year" format string,
        calling this method with a formatted string of "8/2/1900" will
        return [8, 2, 1900]. Everything will be returned as a str.
        """
        # get the non-variable values from the format string ("fluff")
        fluff = self.get_fluff()

        # get the values (everything that isn't fluff) from the formatted string
        values = []
        after = ''
        for junk in fluff:
            before, middle, after = formatted_string.partition(junk)
            if before:
                values.append(before)
            formatted_string = after
        if after:
            values.append(after)
        return values

    def get_iteration(self, formatted_string: str) -> int:
        """
        Return the iteration of this date format's time unit that is
        referred to by a formatted string generated by this date
        format.

        Only works if is_reversible returns True for this date format.
        Check that method before calling this one.
        """
        # decode the format string
        format_string = str(self.format_string)
        codes = []  # [parent, sub, display]
        while '{' in format_string and '}' in format_string:  # this logic is repeated a lot, could probably be a method
            l_index = format_string.index('{')
            r_index = format_string.index('}')
            parent_id, sub_id, display_type = format_string[l_index + 1:r_index].split('-')
            codes.append((TimeUnit.objects.get(pk=parent_id), TimeUnit.objects.get(pk=sub_id), display_type))
            format_string = format_string[:l_index] + format_string[r_index + 1:]

        # get the values from the formatted string
        values = self.get_values_from_formatted_date(formatted_string=formatted_string)

        # get absolute values for each time unit until we find this date format's time unit
        absolutes = {}
        updated = True
        while updated:  # just in case the format string isn't reversible
            updated = False
            for (parent, sub, display), value in zip(codes, values):
                if sub.id not in absolutes:  # don't repeat checks for something we've found already
                    if parent == sub:
                        if display in ['n', 'name']:
                            raise ValueError  # absolutes can't be names, format string is bad
                        absolutes[sub.id] = int(value)
                        updated = True
                    elif parent.id in absolutes:
                        if display in ['n', 'name']:  # get the iteration if we were given a name
                            if parent.base_unit != sub:
                                raise ValueError  # only direct base units can have names, format string is bad
                            base_instance_names = [b[0] for b in  # b[0] is the name, b[1] is the length (unneeded here)
                                                   parent.get_base_unit_instances(iteration=absolutes[parent.id])]
                            value = base_instance_names.index(value) + 1
                        else:
                            value = int(value)
                        absolutes[sub.id] = parent.get_first_sub_unit_instance_iteration_at_iteration(
                            sub_unit=sub, iteration=absolutes[parent.id]) + value - 1
                        updated = True
                    if sub == self.time_unit and sub.id in absolutes:
                        return absolutes[sub.id]
        raise AttributeError  # if we didn't find it, the format string wasn't reversible

    def is_differentiable(self, other_formats: 'DateFormat | list[DateFormat]') -> bool:
        """
        Return True if this date format can be identified as distinct
        from one or more other date formats given any single formatted
        date string, False otherwise.

        In other words, this method returns True if there is no overlap
        between the possible formatted date strings generated by this
        date format and the possible formatted date strings generated
        by any of the other specified date formats.

        Note that in the case of multiple other date formats, the other
        date formats will not be tested against each other.
        """
        if type(other_formats) is not list:
            other_formats = [other_formats]
        own_fluff = self.get_fluff()
        for other_format in other_formats:
            if own_fluff == other_format.get_fluff():
                return False  # this doesn't consider the possible resolutions of the {} codes; could be more permissive
        return True

    def formatted_date_is_possible(self, formatted_string: str) -> bool:
        """
        Return True if the given formatted date string could be
        generated by this date format.

        Does not consider the possible resolutions of variable codes.
        """
        fluff_regex = '.*' + '.*'.join([re.escape(junk) for junk in self.get_fluff()]) + '.*'
        return re.match(fluff_regex, formatted_string) is not None

    @staticmethod
    def find_likely_source_date_formats(formatted_string: str, possible_formats: 'list[DateFormat]') -> \
            'list[DateFormat]':
        """
        Return a list of date formats that could have generated a given
        formatted date string sorted by likelihood from the most likely
        source to the least likely source. Only date formats in
        possible_formats will be considered. Date formats that could
        not have possibly generated the formatted date string will not
        appear in the returned list.
        """
        sorted_formats = copy(possible_formats)  # sort is in place so don't modify what was passed in
        sorted_formats.sort(key=lambda x: len(x.get_fluff()), reverse=True)  # more fluff matched = more likely
        likely_formats = []
        for date_format in sorted_formats:
            if date_format.formatted_date_is_possible(formatted_string=formatted_string):
                likely_formats.append(date_format)
        return likely_formats


class DisplayConfig(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    display_config_name = models.CharField(max_length=200,
                                           help_text=html_tooltip('The name of this display configuration'))
    display_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE,
                                     help_text=html_tooltip('The type of time unit to display by default'))
    nest_level = models.IntegerField(default=0,
                                     help_text=html_tooltip('"0" for no nested display, "1" for nested display'))
    default_date_bookmark = models.ForeignKey('DateBookmark', on_delete=models.CASCADE, null=True, blank=True,
                                              help_text=html_tooltip('The date to show by default when this display '
                                                                     'configuration is initially loaded'))

    def __str__(self):
        return self.display_config_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:display-config-detail', kwargs={'pk': self.pk, 'calendar_key': self.calendar.pk,
                                                                        'world_key': self.calendar.world.pk})


class DisplayUnitConfig(models.Model):
    display_config = models.ForeignKey(DisplayConfig, on_delete=models.CASCADE)
    time_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE)

    class SearchType(models.TextChoices):
        ITERATION = 'iteration', 'Iteration'
        DATE_FORMATS = 'formats', 'Date Formats'
        NOT_SEARCHABLE = 'none', 'Not Searchable'
    search_type = models.CharField(max_length=32, choices=SearchType.choices, default=SearchType.ITERATION,
                                   help_text=html_tooltip('How to find a specific instance of this time unit on your '
                                                          'calendar: by typing in an iteration number directly, by '
                                                          'typing in a formatted date of a format you specify (or one '
                                                          'of many formats you specify), or by no means at all'))
    searchable_date_formats = models.ManyToManyField(DateFormat, blank=True,
                                                     help_text=html_tooltip('If search type is "Date Formats", these '
                                                                            'are the date formats to allow searching '
                                                                            'by; you will only see a single search bar '
                                                                            'on the calendar even if multiple formats '
                                                                            'are searchable, but the formats must all '
                                                                            'be distinct enough from each other for '
                                                                            'the system to tell which format was typed '
                                                                            'in'))

    class DisplayNameType(models.TextChoices):
        DEFAULT_FORMAT = 'default', 'Default Date Format'
        SECONDARY_FORMAT = 'secondary', 'Secondary Date Format'
        OTHER_FORMAT = 'other', 'Other Specified Date Format'
        NO_FORMAT = 'basic', 'No Date Format'
    header_display_name_type = models.CharField(max_length=32, choices=DisplayNameType.choices,
                                                default=DisplayNameType.DEFAULT_FORMAT,
                                                help_text=html_tooltip('How to determine the main header of your '
                                                                       'calendar page for this time unit: by using the '
                                                                       'time unit\'s default date format, by using its '
                                                                       'secondary format, by specifying some other '
                                                                       'format, or by using no format, generating '
                                                                       'something like "(time unit name) (iteration)"'))
    header_other_date_format = models.ForeignKey(DateFormat, on_delete=models.CASCADE, related_name='+', blank=True,
                                                 null=True,
                                                 help_text=html_tooltip('The date format to use if "Other" is selected '
                                                                        'for the header display name type'))
    base_unit_display_name_type = models.CharField(max_length=32, choices=DisplayNameType.choices,
                                                   default=DisplayNameType.SECONDARY_FORMAT,
                                                   help_text=html_tooltip('How to determine the header of each cell in '
                                                                          'your calendar page for this time unit: by '
                                                                          'using the base time unit\'s default date '
                                                                          'format, by using its secondary format, by '
                                                                          'specifying some other format, or by using '
                                                                          'no format, generating something like "(base '
                                                                          'time unit name) (relative iteration)"'))
    base_unit_other_date_format = models.ForeignKey(DateFormat, on_delete=models.CASCADE, related_name='+', blank=True,
                                                    null=True,
                                                    help_text=html_tooltip('The date format to use if "Other" is '
                                                                           'selected for the base unit display name '
                                                                           'type'))
    row_grouping_time_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE, related_name='+', blank=True,
                                               null=True,
                                               help_text=html_tooltip('An optional time unit that can be used to '
                                                                      'organize the calendar page into rows, e.g. many '
                                                                      'real life month calendar pages are grouped by '
                                                                      'one week per row; must have the same base unit '
                                                                      'as the page\'s time unit and a non-varying '
                                                                      'length cycle'))

    class RowGroupingLabelType(models.TextChoices):
        NO_LABELS = 'none', 'No Labels'
        COLUMN_NAMES = 'names', 'Label Columns by Name'
        COLUMN_NUMBERS = 'numbers', 'Label Columns by Number'
        ROW_COUNTS = 'counts', 'Label Rows by Count'
    row_grouping_label_type = models.CharField(max_length=32, choices=RowGroupingLabelType.choices,
                                               default=RowGroupingLabelType.NO_LABELS,
                                               help_text=html_tooltip('The style of labeling to use for rows/columns '
                                                                      'if a row grouping time unit is specified: no '
                                                                      'labels, labels on each column with the name of '
                                                                      'the base unit of the row grouping time unit '
                                                                      '(e.g. Wednesday for a week), labels on each '
                                                                      'column with the number of the base unit of the '
                                                                      'row grouping time unit (e.g. 4 instead of '
                                                                      'Wednesday), or labels on each row that count '
                                                                      'the occurrences of the row grouping unit (Week '
                                                                      '1, Week 2, etc.)'))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['display_config', 'time_unit'], name='unique_display_config_time_unit'),
        ]

    def __str__(self):
        return '"' + self.display_config.display_config_name + '" unit config for "' + self.time_unit.time_unit_name + \
               '"'


class DateBookmark(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    date_bookmark_name = models.CharField(max_length=200, blank=True,
                                          help_text=html_tooltip('The name of this date bookmark'))
    bookmark_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE,
                                      help_text=html_tooltip('The type of time unit that this bookmark is for'))
    bookmark_iteration = models.IntegerField(help_text=html_tooltip('The instance of the specified time unit type for '
                                                                    'this bookmark to link to'))
    personal_bookmark_creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                                                  blank=True, help_text=html_tooltip('The creator of this bookmark if '
                                                                                     'this is a personal bookmark; '
                                                                                     'not populated if this is a '
                                                                                     'shared bookmark'))

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        """
        Return the name of this date bookmark if set, otherwise return
        the default date format string for the bookmarked date. If that
        also isn't set, return something like
        (bookmark_unit + " " + bookmark_iteration).
        """
        if self.date_bookmark_name:
            return self.date_bookmark_name
        elif self.bookmark_unit.default_date_format:
            return self.bookmark_unit.default_date_format.get_formatted_date(iteration=self.bookmark_iteration)
        else:
            return str(self.bookmark_unit.time_unit_name) + ' ' + str(self.bookmark_iteration)

    def is_personal(self):
        """
        Return True if this is a personal bookmark only intended for
        use by the user that created it or False if this is a shared
        bookmark made by the world creator intended for anyone to use.
        """
        return True if self.personal_bookmark_creator else False
