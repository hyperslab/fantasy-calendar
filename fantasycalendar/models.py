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
    time_unit_name = models.CharField(max_length=200)
    base_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    number_of_base = models.DecimalField('number of base units in this unit', max_digits=8, decimal_places=3, default=0)

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
