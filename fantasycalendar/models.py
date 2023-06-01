import decimal
import math
from decimal import Decimal

from django.db import models
from django.contrib import admin
from django.urls import reverse
from django.conf import settings


class World(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  # remove null=True later
    world_name = models.CharField(max_length=200)

    def __str__(self):
        return self.world_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:world-detail', kwargs={'pk': self.pk})


class Calendar(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    calendar_name = models.CharField(max_length=200)
    default_display_config = models.ForeignKey('DisplayConfig', on_delete=models.CASCADE, null=True, related_name='+',
                                               blank=True)

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


class TimeUnit(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    time_unit_name = models.CharField(max_length=200, default='')
    base_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    length_cycle = models.CharField(max_length=800, default='1')
    base_unit_instance_names = models.CharField(max_length=800, default='', blank=True)
    default_date_format = models.ForeignKey('DateFormat', on_delete=models.CASCADE, null=True, blank=True)

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

    def get_instance_display_name(self, iteration: int, date_format: 'DateFormat' = None) -> str:
        """
        Return a human-readable name for the instance of this time unit
        that exists at a particular iteration.

        In order, prefers a given date format, then the default date
        format for this time unit if none is given, then something like
        (time_unit_name + " " + iteration) if there is no default date
        format for this time unit.
        """
        if date_format is None:
            date_format = self.default_date_format
        if date_format:
            if date_format.time_unit != self:
                raise ValueError
            return date_format.get_formatted_date(iteration)
        else:
            return str(self.time_unit_name) + ' ' + str(iteration)


class Event(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200)
    event_description = models.TextField(max_length=800, blank=True)
    bottom_level_iteration = models.BigIntegerField()

    def __str__(self):
        return self.event_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:event-detail', kwargs={'pk': self.pk, 'calendar_key': self.calendar.pk,
                                                               'world_key': self.calendar.world.pk})


class DateFormat(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    time_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE)
    date_format_name = models.CharField(max_length=200)
    format_string = models.CharField(max_length=200)

    def __str__(self):
        return self.date_format_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:date-format-detail', kwargs={'pk': self.pk, 'calendar_key': self.calendar.pk,
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
            codes.append(formatted_date[l_index+1:r_index])
            indexes.append(l_index)
            formatted_date = formatted_date[:l_index] + formatted_date[r_index+1:]
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
            sub_iteration_in_parent_iteration = parent_unit.\
                get_sub_unit_instance_iteration_within_higher_level_iteration(
                    sub_unit=sub_unit, sub_unit_iteration=sub_iteration)
            answer = 'unknown display type: "' + display + '"'
            if display.lower() in ['n', 'name']:
                instances = list(parent_unit.get_base_unit_instances(iteration=parent_iteration))
                answer = instances[sub_iteration_in_parent_iteration-1][0]
            elif display.lower() in ['i', 'iter', 'iteration']:
                answer = str(sub_iteration_in_parent_iteration)
            answers.append(answer)
        for answer, index in zip(reversed(answers), reversed(indexes)):  # has to be backwards here so indexes work
            formatted_date = formatted_date[:index] + answer + formatted_date[index:]
        return formatted_date


class DisplayConfig(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    display_config_name = models.CharField(max_length=200)
    display_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE)
    nest_level = models.IntegerField(default=0)
    default_date_bookmark = models.ForeignKey('DateBookmark', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.display_config_name


class DateBookmark(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    date_bookmark_name = models.CharField(max_length=200, blank=True)
    bookmark_unit = models.ForeignKey(TimeUnit, on_delete=models.CASCADE)
    bookmark_iteration = models.IntegerField()

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
