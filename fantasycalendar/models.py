import decimal
from decimal import Decimal

from django.db import models
from django.contrib import admin
from django.urls import reverse


class World(models.Model):
    world_name = models.CharField(max_length=200)

    def __str__(self):
        return self.world_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:world-detail', kwargs={'pk': self.pk})


class Calendar(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    calendar_name = models.CharField(max_length=200)

    def __str__(self):
        return self.calendar_name

    def get_absolute_url(self):
        return reverse('fantasycalendar:calendar-detail', kwargs={'pk': self.pk, 'world_key': self.world.pk})


class TimeUnit(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    time_unit_name = models.CharField(max_length=200, default='')
    base_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    length_cycle = models.CharField(max_length=800, default='1')
    base_unit_instance_names = models.CharField(max_length=800, default='', blank=True)

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

        Always returns 1 when the iteration value is 1. Also returns 1
        for time units that have no base unit.
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
        """
        if not self.base_unit:
            return [(str(self.time_unit_name) + ' 1', 1)]
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
