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
    def is_bottom_level(self):
        """
        Return True if this is the lowest-level unit of time in its
        Calendar, i.e. the equivalent of a "day".
        """
        return self.base_unit is None and self.id is not None  # will not be considered "bottom level" until saved to db

    def get_length_cycle_display(self):
        """
        Return length_cycle formatted as a string for display.
        """
        lengths = self.get_length_cycle()
        if len(lengths) == 0:  # this shouldn't happen
            return 'Undefined'
        else:
            return ', '.join(['{:f}'.format(x.normalize()) for x in lengths])

    def is_top_level(self):
        """
        Return True if there are no other TimeUnit objects that have
        this TimeUnit as their base_unit.
        """
        return TimeUnit.objects.filter(base_unit_id=self.id).count() == 0

    def get_level_depth(self):
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

    def is_highest_level(self):
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

    def get_base_unit_instance_names(self):
        if not self.base_unit_instance_names:
            return []
        names = self.base_unit_instance_names.split()
        if type(names) is not list:
            names = [names]
        return names

    def set_base_unit_instance_names(self, names: list[str]):
        self.base_unit_instance_names = ' '.join(names)
        self.save()

    def get_length_cycle(self) -> list[decimal]:
        if not self.length_cycle:
            return []
        lengths = [Decimal(x) for x in self.length_cycle.split()]
        if type(lengths) is not list:
            lengths = [lengths]
        return lengths

    def set_length_cycle(self, lengths: list[decimal]):
        self.length_cycle = ' '.join([str(x) for x in lengths])
        self.save()

    def get_length_at_iteration(self, iteration):
        length_cycle = self.get_length_cycle()
        cycle_location = (iteration - 1) % len(length_cycle)
        cycle_iteration = int((iteration - 1) / len(length_cycle)) + 1
        base_length = int(length_cycle[cycle_location])
        remainder_length = length_cycle[cycle_location] % 1
        extra = 0
        if ((remainder_length * (cycle_iteration - 1)) % 1) + remainder_length >= 1:
            extra = 1
        return int(base_length + extra)

    def get_first_base_unit_instance_iteration_at_iteration(self, iteration):
        length_cycle = self.get_length_cycle()
        number_of_complete_cycles = int((iteration - 1) / len(length_cycle))
        current_cycle_completed_instances = (iteration - 1) % len(length_cycle)
        base_iteration = number_of_complete_cycles * sum(length_cycle)
        for i in range(current_cycle_completed_instances):
            base_iteration += length_cycle[i]
        return int(base_iteration) + 1

    def get_base_unit_instances(self, iteration=1):
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
