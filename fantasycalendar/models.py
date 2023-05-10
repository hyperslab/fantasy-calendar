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
    number_of_base = models.DecimalField('number of base units in this unit', max_digits=8, decimal_places=3, default=0)
    base_unit_instance_names = models.CharField(max_length=800, default='', blank=True)
    base_unit_custom_lengths = models.CharField(max_length=800, default='', blank=True)

    def __str__(self):
        return self.time_unit_name

    @admin.display(boolean=True, description='Lowest level time unit?')
    def is_bottom_level(self):
        """
        Return True if this is the lowest-level unit of time in its
        Calendar, i.e. the equivalent of a "day".
        """
        return self.base_unit is None and self.id is not None  # will not be considered "bottom level" until saved to db

    def get_number_of_base_display(self):
        """
        Return number_of_base formatted for display.
        """
        return self.number_of_base.normalize()

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

    def get_base_unit_custom_lengths(self):
        if not self.base_unit_custom_lengths:
            return []
        lengths = [int(x) for x in self.base_unit_custom_lengths.split()]
        if type(lengths) is not list:
            lengths = [lengths]
        return lengths

    def set_base_unit_custom_lengths(self, lengths: list[int]):
        self.base_unit_custom_lengths = ' '.join([str(x) for x in lengths])
        self.save()

    def get_base_unit_instances(self):
        if not self.base_unit:
            return [(str(self.time_unit_name) + ' 1', 1)]
        numer_of_instances = int(self.number_of_base)
        custom_lengths = self.get_base_unit_custom_lengths()
        lengths = []
        remainder = Decimal('0.0')
        base_length_per = int(self.base_unit.number_of_base)
        if base_length_per < 1:
            base_length_per = 1
        extra_length_per = self.base_unit.number_of_base % 1
        custom_names = self.get_base_unit_instance_names()
        base_name = self.base_unit.time_unit_name
        names = []
        for i in range(numer_of_instances):
            extra = 0
            remainder += extra_length_per
            if remainder >= 1:
                extra += 1
                remainder -= Decimal(1)
            if i < len(custom_lengths):
                lengths.append(custom_lengths[i])
            else:
                lengths.append(base_length_per + extra)
            if i < len(custom_names):
                names.append(custom_names[i])
            else:
                names.append(base_name + ' ' + str(i + 1))
        return zip(names, lengths)
