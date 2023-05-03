from django.db import models
from django.contrib import admin


class World(models.Model):
    world_name = models.CharField(max_length=200)

    def __str__(self):
        return self.world_name


class Calendar(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    calendar_name = models.CharField(max_length=200)

    def __str__(self):
        return self.calendar_name


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
